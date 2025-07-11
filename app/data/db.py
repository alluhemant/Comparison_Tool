import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import lru_cache
import json
import logging
from pathlib import Path
from app.config import settings
from app.models import ComparisonResult

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Raised when a database operation fails"""
    pass


class DBHandler:
    def __init__(self):
        try:
            self.db_path = str(Path(settings.DB_PATH).absolute())
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._init_db()
            logger.info(f"Database handler initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize DBHandler: {e}")
            raise DatabaseError("Database initialization failed.") from e

    def _init_db(self):
        try:
            with self._get_connection() as conn:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS comparisons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tibco_response TEXT NOT NULL,
                    python_response TEXT NOT NULL,
                    differences TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                conn.commit()
                logger.info("Database tables initialized")
        except sqlite3.Error as e:
            logger.error("Database error during initialization:", e)
            raise DatabaseError("Error while setting up the database.") from e

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path, detect_types=sqlite3.PARSE_DECLTYPES)

    @lru_cache(maxsize=128)
    def get_comparison(self, comparison_id: int) -> Optional[ComparisonResult]:
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM comparisons WHERE id = ?",
                    (comparison_id,)
                )
                result = cursor.fetchone()
                if result:
                    result_dict = dict(zip(result.keys(), result))
                    result_dict['metrics'] = json.loads(result_dict['metrics'])
                    return ComparisonResult(**result_dict)
                return None
        except sqlite3.Error as e:
            logger.error(f"Database error while fetching comparison {comparison_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding metrics JSON: {e}")
            return None

    def get_comparisons(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve comparison history with robust row conversion"""
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM comparisons ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()

                results = []
                for row in rows:
                    try:
                        row_dict = dict(zip(row.keys(), row))

                        # Handle metrics JSON
                        try:
                            row_dict['metrics'] = json.loads(row_dict['metrics'])
                        except (json.JSONDecodeError, TypeError):
                            logger.warning("Invalid metrics JSON, using empty dict")
                            row_dict['metrics'] = {}

                        # Handle datetime conversion
                        if 'created_at' in row_dict and isinstance(row_dict['created_at'], str):
                            try:
                                row_dict['created_at'] = datetime.fromisoformat(row_dict['created_at'])
                            except ValueError:
                                pass

                        results.append(row_dict)

                    except Exception as row_error:
                        logger.warning(f"Skipping malformed row: {str(row_error)}")
                        continue

                logger.info(f"Retrieved {len(results)} comparisons from DB")
                return results

        except sqlite3.Error as e:
            logger.error(f"Database error fetching comparisons: {str(e)}")
            raise DatabaseError(f"Failed to fetch comparisons: {str(e)}")

    def save_comparison(
            self,
            tibco_resp: str,
            python_resp: str,
            diff: str,
            metrics: Dict[str, Any]
    ) -> bool:
        try:
            changed_lines = self._extract_changed_lines(diff)
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """INSERT INTO comparisons 
                    (tibco_response, python_response, differences, metrics) 
                    VALUES (?, ?, ?, ?)""",
                    (tibco_resp, python_resp, changed_lines, json.dumps(metrics))
                )
                conn.commit()
                if cursor.rowcount == 1:
                    logger.info(f"Saved comparison with ID: {cursor.lastrowid}")
                    return True
                logger.warning("No rows affected while saving.")
                return False
        except sqlite3.Error as e:
            logger.error(f"Database error during save: {e}")
            return False
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"Error with metrics JSON encoding: {e}")
            return False

    def insert(self, result: dict) -> bool:
        """Wrapper for insert, used by endpoint"""
        try:
            return self.save_comparison(
                tibco_resp=result.get("tibco_response", ""),
                python_resp=result.get("python_response", ""),
                diff=result.get("differences", ""),
                metrics=result.get("metrics", {})
            )
        except Exception as e:
            logger.error(f"Insert failed: {e}")
            return False

    @staticmethod
    def _extract_changed_lines(diff: str) -> str:
        return "\n".join(
            line for line in diff.splitlines()
            if line.startswith(('+', '-'))
        )

    def get_recent_comparisons(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.get_comparisons(limit)

    def __del__(self):
        logger.info("Database handler cleanup")
