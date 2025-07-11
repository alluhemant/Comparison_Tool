import asyncio
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime
from app.services.fetcher import fetch_data
from app.core.comparator import ResponseComparator
from app.data.db import DBHandler
from app.config import settings
from app.models import ComparisonResult
import logging

logger = logging.getLogger(__name__)

class ComparisonError(Exception):
    """Custom exception for comparison failures"""
    pass


class ComparisonEngine:
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.db = DBHandler()
        self.comparator = ResponseComparator()

    async def _fetch_data(self, url: str) -> str:
        try:
            logger.info(f"Fetching data from {url}")
            return await fetch_data(url)
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
            raise

    async def run_comparison(self, compare_type: str = 'xml') -> ComparisonResult:
        try:
            tibco_resp, python_resp = await asyncio.gather(
                self._fetch_data(settings.TIBCO_URL),
                self._fetch_data(settings.PYTHON_URL)
            )

            if not tibco_resp or not python_resp:
                raise ValueError("One or both responses are empty.")

            if compare_type == 'json':
                try:
                    tibco_json = json.loads(tibco_resp)
                    python_json = json.loads(python_resp)
                except json.JSONDecodeError as e:
                    print("JSON decoding failed:", e)
                    raise ComparisonError("Invalid JSON in one of the responses.") from e

                diff, metrics = self.comparator.compare_json(tibco_json, python_json)
            else:
                diff, metrics = self.comparator.compare_xml(tibco_resp, python_resp)

            def save_to_db():
                try:
                    with sqlite3.connect(settings.DB_PATH) as conn:
                        cursor = conn.execute(
                            """INSERT INTO comparisons 
                            (tibco_response, python_response, differences, metrics) 
                            VALUES (?, ?, ?, ?)""",
                            (tibco_resp, python_resp, diff, json.dumps(metrics)))
                        conn.commit()
                        return cursor.rowcount > 0
                except Exception as e:
                    print(f"Failed to save to database: {e}")
                    return False

            saved = await asyncio.get_event_loop().run_in_executor(
                self.thread_pool, save_to_db
            )

            if not saved:
                raise ComparisonError("Failed to save comparison to the database.")

            return ComparisonResult(
                tibco_response=tibco_resp,
                python_response=python_resp,
                differences=diff,
                metrics=metrics
            )

        except Exception as e:
            print(f"Comparison failed: {e}")
            logger.error(f"Comparison failed: {str(e)}", exc_info=True)
            raise ComparisonError(f"Comparison failed: {str(e)}")
