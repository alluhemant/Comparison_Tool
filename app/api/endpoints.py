from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Dict, Any
from app.core.engine import ComparisonEngine, ComparisonError
from app.data.db import DBHandler, DatabaseError
import logging
from app.config import settings
from fastapi import APIRouter


# Add prefix to router
router = APIRouter(prefix="/api/v1")
engine = ComparisonEngine()
db_handler = DBHandler()
logger = logging.getLogger(__name__)


@router.post("/compare")
async def compare_apis():
    try:
        result = await engine.run_comparison()

        # ✅ Save the result to DB
        db_handler.insert(result.dict())

        latest = db_handler.get_comparisons(limit=1)
        if not latest:
            logger.error("Comparison saved but not found in DB.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Comparison completed but not saved to database"
            )

        return result.dict()

    except ComparisonError as e:
        logger.error(f"ComparisonError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@router.get("/latest")
async def get_latest_comparison():
    try:
        results = db_handler.get_comparisons(limit=1)
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No comparisons found"
            )
        return results[0]
    except Exception as e:
        logger.error(f"Failed to fetch latest comparison: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve latest comparison"
        )


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_recent_comparisons(
        limit: int = Query(10, gt=0, le=100, description="Number of comparisons to return")
):
    """Get recent comparison results with robust error handling"""
    try:
        results = db_handler.get_comparisons(limit=limit)
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No comparisons found in database"
            )

        # Validate each result has required fields
        for result in results:
            if not all(k in result for k in ['tibco_response', 'python_response', 'differences']):
                logger.warning(f"Incomplete comparison entry found: {result.get('id', 'unknown')}")

        logger.info(f"Successfully returned {len(results)} comparisons")
        return results

    except DatabaseError as e:
        logger.error(f"Database error in history endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
    except HTTPException:
        raise  # Re-raise explicitly raised HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error in history endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while fetching history"
        )


@router.get("/debug/history")
async def debug_history():
    try:
        results = db_handler.get_comparisons(limit=10)
        logger.info(f"Raw DB results: {results}")
        return {
            "db_query": "SELECT * FROM comparisons ORDER BY id DESC LIMIT 10",
            "count": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Debug endpoint failed: {e}")
        raise HTTPException(status_code=500, detail="Debug endpoint failed.")