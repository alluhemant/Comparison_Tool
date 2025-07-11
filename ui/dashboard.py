import streamlit as st
import requests
import time
from datetime import datetime
from difflib import unified_diff, ndiff
from typing import List, Dict, Tuple, Optional
from html import escape
import uuid
from app.config import settings

API_BASE_URL = settings.API_BASE_URL

# API documentation curl commands with proper versioning
compare_curl = f"""curl -X 'POST' \\
  '{API_BASE_URL}/api/v1/compare' \\
  -H 'accept: application/json' \\
  -d ''
"""

latest_curl = f"""curl -X 'GET' \\
  '{API_BASE_URL}/api/v1/latest' \\
  -H 'accept: application/json'
"""

history_curl = f"""curl -X 'GET' \\
  '{API_BASE_URL}/api/v1/history?limit=10' \\
  -H 'accept: application/json'
"""

docs_curl = f"""curl -X 'GET' \\
  '{API_BASE_URL}/docs' \\
  -H 'accept: application/json'
"""


def show_api_endpoints():
    """Display API documentation in sidebar"""
    st.sidebar.title("API Documentation")
    with st.sidebar.expander("Compare APIs"):
        st.markdown("**POST** - Run a new comparison")
        st.code(compare_curl, language="bash")
    with st.sidebar.expander("Get Latest Comparison"):
        st.markdown("**GET** - Get the latest comparison result")
        st.code(latest_curl, language="bash")
    with st.sidebar.expander("Get History of Comparisons"):
        st.markdown("**GET** - Get recent comparison results")
        st.code(history_curl, language="bash")
    with st.sidebar.expander("API Documentation"):
        st.markdown("**GET** - OpenAPI/Swagger documentation")
        st.code(docs_curl, language="bash")


def show_api_tester(key_suffix=""):
    """API testing interface in sidebar"""
    st.sidebar.title("API Tester")
    with st.sidebar.expander("Test Endpoints"):
        endpoint = st.selectbox(
            "Select Endpoint",
            ["/api/v1/compare", "/api/v1/latest", "/api/v1/history", "/"],
            index=0,
            key=f"api_tester_endpoint{key_suffix}"
        )
        if endpoint == "/api/v1/compare":
            if st.button("Send POST Request", key=f"post_btn{key_suffix}"):
                with st.spinner("Sending request..."):
                    try:
                        response = requests.post(f"{API_BASE_URL}{endpoint}")
                        if response.status_code == 200:
                            st.sidebar.success("Request successful!")
                        else:
                            st.sidebar.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.sidebar.error(f"Request failed: {str(e)}")
        else:
            if st.button("Send GET Request", key=f"get_btn{key_suffix}"):
                with st.spinner("Sending request..."):
                    try:
                        response = requests.get(f"{API_BASE_URL}{endpoint}")
                        if response.status_code == 200:
                            st.sidebar.success("Request successful!")
                        else:
                            st.sidebar.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.sidebar.error(f"Request failed: {str(e)}")


def fetch_latest_comparison() -> Optional[Dict]:
    """Fetch the latest comparison from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/latest")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"API connection failed: {str(e)}")
        return None


def fetch_comparisons(limit: int = 10) -> List[Dict]:
    """Fetch comparison history from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/history", params={"limit": limit})
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"API connection failed: {str(e)}")
        return []


def parse_diff(old_text: str, new_text: str) -> Tuple[Dict[str, List[str]], str]:
    """Parse differences between two texts"""
    diff = list(unified_diff(
        old_text.splitlines(),
        new_text.splitlines(),
        fromfile='tibco',
        tofile='python'
    ))
    changes = {'added': [], 'removed': [], 'changed': []}
    for line in diff[3:]:
        if line.startswith('+') and not line.startswith('+++'):
            field = line[1:].split(':')[0].strip(' "\'')
            if field:
                changes['added'].append(field)
        elif line.startswith('-') and not line.startswith('---'):
            field = line[1:].split(':')[0].strip(' "\'')
            if field:
                changes['removed'].append(field)
    changes['changed'] = list(set(changes['added']) & set(changes['removed']))
    changes['added'] = [f for f in changes['added'] if f not in changes['changed']]
    changes['removed'] = [f for f in changes['removed'] if f not in changes['changed']]
    return changes, '\n'.join(diff)


def prepare_report_text(changes: Dict[str, List[str]], diff_text: str) -> str:
    """Prepare a text report of differences"""
    content = []
    if changes['changed']:
        content.append("Changed Fields:\n" + "\n".join([f"- {field}" for field in changes['changed']]) + "\n")
    if changes['added']:
        content.append("Added Fields:\n" + "\n".join([f"+ {field}" for field in changes['added']]) + "\n")
    if changes['removed']:
        content.append("Removed Fields:\n" + "\n".join([f"- {field}" for field in changes['removed']]) + "\n")
    content.append("Full Differences:\n" + diff_text)
    return "\n\n".join(content)


def render_github_like_diff(diff_text: str):
    """Render diff in GitHub style"""
    styled_lines = []
    for line in diff_text.splitlines():
        if line.startswith('+') and not line.startswith('+++'):
            styled_lines.append(
                f'<div style="background-color:#e6ffed;padding:2px 6px;font-family:monospace;">{line}</div>')
        elif line.startswith('-') and not line.startswith('---'):
            styled_lines.append(
                f'<div style="background-color:#ffeef0;padding:2px 6px;font-family:monospace;">{line}</div>')
        elif line.startswith('@@'):
            styled_lines.append(
                f'<div style="background-color:#f0f0f0;padding:2px 6px;font-family:monospace;font-weight:bold;">{line}</div>')
        else:
            styled_lines.append(
                f'<div style="background-color:#f6f8fa;padding:2px 6px;font-family:monospace;">{line}</div>')
    html_diff = "\n".join(styled_lines)
    st.markdown(html_diff, unsafe_allow_html=True)


def render_split_diff(old: str, new: str):
    """Render side-by-side diff view"""
    left_lines = old.splitlines()
    right_lines = new.splitlines()
    diffs = list(ndiff(left_lines, right_lines))
    table_style = """
        <style>
        .diff-wrapper {
            overflow-x: auto;
            border: 1px solid #ccc;
            max-width: 100%;
            padding: 10px;
        }
        .diff-table {
            border-collapse: collapse;
            width: 100%;
            font-family: monospace;
            table-layout: fixed;
        }
        .diff-table th, .diff-table td {
            padding: 6px 10px;
            vertical-align: top;
            word-wrap: break-word;
            border: 1px solid #ddd;
            white-space: pre-wrap;
        }
        .diff-add {
            background-color: #e6ffed;
        }
        .diff-remove {
            background-color: #ffeef0;
        }
        .diff-context {
            background-color: #f6f8fa;
        }
        .diff-empty {
            background-color: #fff;
        }
        </style>
    """
    html = [table_style, "<div class='diff-wrapper'>", "<table class='diff-table'>",
            "<tr><th>TIBCO</th><th>Python</th></tr>"]
    for line in diffs:
        tag = line[0]
        content = escape(line[2:])
        if tag == ' ':
            left_cell = f"<td class='diff-context'>{content}</td>"
            right_cell = f"<td class='diff-context'>{content}</td>"
        elif tag == '-':
            left_cell = f"<td class='diff-remove'>{content}</td>"
            right_cell = f"<td class='diff-empty'></td>"
        elif tag == '+':
            left_cell = f"<td class='diff-empty'></td>"
            right_cell = f"<td class='diff-add'>{content}</td>"
        else:
            continue
        html.append(f"<tr>{left_cell}{right_cell}</tr>")
    html.append("</table></div>")
    st.markdown("\n".join(html), unsafe_allow_html=True)


def show_comparison_result(comp: Dict, idx: int, section_prefix: str = "recent"):
    """Display a single comparison result"""
    if not all(k in comp for k in ['tibco_response', 'python_response']):
        st.error("Invalid comparison data structure")
        return

    diff_mode = st.radio(
        "Select Diff View Mode",
        ["Unified", "Split"],
        horizontal=True,
        key=f"diff_mode_{section_prefix}_{idx}"
    )
    changes, diff_text = parse_diff(comp["tibco_response"], comp["python_response"])
    report_text = prepare_report_text(changes, diff_text)

    with st.expander("View Detailed Differences", expanded=False):
        if diff_mode == "Unified":
            render_github_like_diff(diff_text)
        else:
            render_split_diff(comp["tibco_response"], comp["python_response"])

    with st.expander("View Full Responses", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("TIBCO Response")
            st.code(comp["tibco_response"],
                    language="xml" if comp["tibco_response"].strip().startswith('<') else "json")
        with col2:
            st.subheader("Python Response")
            st.code(comp["python_response"],
                    language="xml" if comp["python_response"].strip().startswith('<') else "json")

    st.download_button(
        label="Download Full Differences Report",
        data=report_text,
        file_name=f"comparison_{comp.get('id', uuid.uuid4().hex)}.txt",
        mime="text/plain",
        key=f"dl_{section_prefix}_{idx}"
    )


def show_dashboard():
    """Main dashboard function"""
    st.set_page_config(layout="wide", page_title="XML Comparison Dashboard", page_icon="🔍")
    show_api_endpoints()
    show_api_tester(key_suffix="_main")

    st.title("XML Comparison Dashboard")
    st.markdown("---")

    # Initialize session state with robust structure
    if 'comparison_data' not in st.session_state:
        st.session_state.comparison_data = {
            'all_history': [],  # Complete history from API
            'latest': None,  # Latest comparison object
            'last_fetched': None,  # Timestamp of last fetch
            'api_status': 'pending'  # API health status
        }

    def fetch_all_comparisons():
        """Fetch and validate all comparison data from API"""
        try:
            # Get full history with increased timeout
            history_response = requests.get(f"{API_BASE_URL}/api/v1/history?limit=20", timeout=10)
            if history_response.status_code != 200:
                st.session_state.comparison_data['api_status'] = f"history_error_{history_response.status_code}"
                return False

            history = history_response.json()
            if not isinstance(history, list):
                st.session_state.comparison_data['api_status'] = "history_invalid_format"
                return False

            # Get latest comparison with validation
            latest_response = requests.get(f"{API_BASE_URL}/api/v1/latest", timeout=10)
            if latest_response.status_code != 200:
                st.session_state.comparison_data['api_status'] = f"latest_error_{latest_response.status_code}"
                return False

            latest = latest_response.json()
            if not all(k in latest for k in ['id', 'tibco_response', 'python_response']):
                st.session_state.comparison_data['api_status'] = "latest_incomplete_data"
                return False

            # Update session state
            st.session_state.comparison_data = {
                'all_history': history,
                'latest': latest,
                'last_fetched': datetime.now().isoformat(),
                'api_status': "ok"
            }
            return True

        except requests.exceptions.RequestException as e:
            st.session_state.comparison_data['api_status'] = f"request_error_{str(e)}"
            return False
        except Exception as e:
            st.session_state.comparison_data['api_status'] = f"unexpected_error_{str(e)}"
            return False

    # Initial data load
    if not st.session_state.comparison_data['all_history']:
        with st.spinner("Loading comparison history..."):
            if not fetch_all_comparisons():
                st.error("Initial data load failed")

    # Run new comparison
    with st.form("new_comparison"):
        st.subheader("Run New Comparison")
        if st.form_submit_button("Execute Comparison"):
            with st.spinner("Running comparison..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/api/v1/compare", timeout=10)
                    if response.status_code == 200:
                        st.success("Comparison completed!")
                        # Force full refresh
                        if fetch_all_comparisons():
                            st.rerun()
                        else:
                            st.warning("Refresh after comparison failed")
                    else:
                        st.error(f"Comparison failed: {response.text}")
                except Exception as e:
                    st.error(f"Request failed: {str(e)}")

    # Display controls
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh All Data", help="Force reload from API"):
                with st.spinner("Refreshing data..."):
                    if fetch_all_comparisons():
                        st.rerun()
                    else:
                        st.error("Refresh failed")
        with col2:
            debug_expander = st.expander("🔍 Debug Tools")

    # Display latest comparison with validation
    st.subheader("Latest Comparison")
    latest = st.session_state.comparison_data.get('latest')
    if latest:
        if all(k in latest for k in ['tibco_response', 'python_response']):
            show_comparison_result(latest, 0, "latest")
        else:
            st.error("Latest comparison has missing data")
    else:
        st.warning("No latest comparison available")

    # Display recent comparisons with robust handling
    st.subheader("Recent Comparisons")
    all_history = st.session_state.comparison_data.get('all_history', [])
    latest_id = latest.get('id') if latest else None

    if len(all_history) > 0:
        # Create list of recent comparisons excluding latest
        recent_comparisons = [
            comp for comp in all_history
            if str(comp.get('id')) != str(latest_id)
        ]

        if recent_comparisons:
            st.success(f"Showing {len(recent_comparisons)} recent comparisons (of {len(all_history)} total)")

            # Display each comparison with validation
            for idx, comp in enumerate(recent_comparisons[:10], 1):  # Limit to 10
                if not all(k in comp for k in ['tibco_response', 'python_response']):
                    st.error(f"Comparison #{comp.get('id')} has missing data - skipping")
                    continue

                with st.expander(f"Comparison #{comp.get('id', idx)} - {comp.get('created_at', 'Unknown date')}"):
                    show_comparison_result(comp, idx, "recent")
        else:
            st.info("No additional comparisons found (only latest available)")
    else:
        st.warning("No comparison history available")

    # Enhanced debug information
    with debug_expander:
        st.write("### System Status")
        status_col1, status_col2 = st.columns(2)

        with status_col1:
            st.write("**API Status:**")
            status = st.session_state.comparison_data.get('api_status', 'unknown')
            if status == 'ok':
                st.success("✅ Operational")
            else:
                st.error(f"❌ {status}")

            st.write("**Last Fetched:**")
            st.write(st.session_state.comparison_data.get('last_fetched', 'Never'))

        with status_col2:
            st.write("**Data Counts:**")
            st.write(f"Total: {len(all_history)}")
            st.write(f"Latest ID: {latest_id or 'None'}")

        st.write("### Verification Tools")

        if st.button("Verify API Endpoints"):
            try:
                st.write("#### History Endpoint")
                history_resp = requests.get(f"{API_BASE_URL}/api/v1/history?limit=5")
                if history_resp.status_code == 200:
                    history_data = history_resp.json()
                    st.success(f"✅ Returned {len(history_data)} comparisons")
                    st.json({
                        "sample_ids": [x.get('id') for x in history_data],
                        "first_item": {k: v for k, v in history_data[0].items()
                                       if k in ['id', 'created_at']} if history_data else None
                    })
                else:
                    st.error(f"❌ Failed: {history_resp.status_code}")

                st.write("#### Latest Endpoint")
                latest_resp = requests.get(f"{API_BASE_URL}/api/v1/latest")
                if latest_resp.status_code == 200:
                    latest_data = latest_resp.json()
                    st.success("✅ Operational")
                    st.json({
                        "id": latest_data.get('id'),
                        "created_at": latest_data.get('created_at')
                    })
                else:
                    st.error(f"❌ Failed: {latest_resp.status_code}")

            except Exception as e:
                st.error(f"Verification failed: {str(e)}")

        if st.button("Check Data Consistency"):
            try:
                history = requests.get(f"{API_BASE_URL}/api/v1/history?limit=1").json()
                latest = requests.get(f"{API_BASE_URL}/api/v1/latest").json()

                st.write("#### Consistency Report")
                cols = st.columns(3)

                with cols[0]:
                    st.write("**History**")
                    st.write(f"Count: {len(history)}")
                    st.write(f"First ID: {history[0]['id'] if history else 'None'}")

                with cols[1]:
                    st.write("**Latest**")
                    st.write(f"ID: {latest.get('id', 'None')}")

                with cols[2]:
                    st.write("**Match**")
                    if history and latest:
                        match = history[0]['id'] == latest['id']
                        st.write("✅" if match else "❌")
                        st.write("Consistent" if match else "Inconsistent")
                    else:
                        st.write("⚠️ No data")

            except Exception as e:
                st.error(f"Check failed: {str(e)}")


if __name__ == "__main__":
    show_dashboard()