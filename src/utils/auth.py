"""
Authentication utilities for Linear API
"""

import requests
from typing import Optional
from config.settings import LINEAR_API_KEY, LINEAR_API_URL


def get_auth_headers() -> dict:
    """
    Get authentication headers for Linear API requests

    Returns:
        dict: Headers with authorization token
    """
    return {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json"
    }


def validate_api_key(api_key: Optional[str] = None) -> tuple[bool, str]:
    """
    Validate Linear API key by making a test request

    Args:
        api_key: API key to validate (uses config if not provided)

    Returns:
        tuple: (is_valid, message)
    """
    key = api_key if api_key is not None else LINEAR_API_KEY

    if not key or (isinstance(key, str) and len(key.strip()) == 0):
        return False, "API key is empty or not set"

    # Simple test query to check if the API key works
    test_query = """
    query {
        viewer {
            id
            name
        }
    }
    """

    headers = {
        "Authorization": key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            LINEAR_API_URL,
            json={"query": test_query},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                return False, f"API error: {data['errors'][0]['message']}"
            return True, "API key is valid"
        elif response.status_code == 401:
            return False, "Invalid API key or unauthorized"
        else:
            return False, f"API returned status code {response.status_code}"

    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)}"


def get_viewer_info() -> Optional[dict]:
    """
    Get information about the authenticated user

    Returns:
        dict: User information or None if failed
    """
    query = """
    query {
        viewer {
            id
            name
            email
        }
    }
    """

    headers = get_auth_headers()

    try:
        response = requests.post(
            LINEAR_API_URL,
            json={"query": query},
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if "data" in data and "viewer" in data["data"]:
                return data["data"]["viewer"]
    except requests.exceptions.RequestException:
        pass

    return None
