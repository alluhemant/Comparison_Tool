from difflib import unified_diff
from deepdiff import DeepDiff
import json

# Custom exception for comparison issues
class ComparisonError(Exception):
    """Raised when a comparison operation fails"""
    pass


class ResponseComparator:
    @staticmethod
    def compare_xml(tibco_xml: str, python_xml: str) -> tuple:
        try:
            diff = ''.join(unified_diff(
                tibco_xml.splitlines(keepends=True),
                python_xml.splitlines(keepends=True),
                fromfile="tibco",
                tofile="python"
            ))

            metrics = {
                "tibco_lines": len(tibco_xml.splitlines()),
                "python_lines": len(python_xml.splitlines()),
                "changed_lines": diff.count('\n+') + diff.count('\n-')
            }

            return diff, metrics
        except Exception as e:
            print(f"Error comparing XML: {e}")
            raise ComparisonError("An error occurred while comparing XML.") from e

    @staticmethod
    def compare_json(tibco_json: dict, python_json: dict) -> tuple:
        try:
            diff = DeepDiff(tibco_json, python_json, ignore_order=True)
            metrics = {
                "changes": len(diff.get('values_changed', {})),
                "type_changes": len(diff.get('type_changes', {}))
            }
            return json.dumps(diff), metrics
        except Exception as e:
            print(f"Error comparing JSON: {e}")
            raise ComparisonError("An error occurred while comparing JSON.") from e
