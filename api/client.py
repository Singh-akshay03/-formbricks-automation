"""Formbricks API client for interacting with Management and Client APIs."""

import requests
from typing import Dict, List, Any, Optional
import time


class FormbricksClient:
    """Client for interacting with Formbricks Management and Client APIs."""

    def __init__(self, base_url: str, api_key: str, organization_id: str, environment_id: str):
        """Initialize the Formbricks client.

        Args:
            base_url: Base URL of the Formbricks instance
            api_key: API key for authentication
            organization_id: Organization ID
            environment_id: Environment ID
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.organization_id = organization_id
        self.environment_id = environment_id
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-api-key": api_key
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        retries: int = 3
    ) -> Dict[str, Any]:
        """Make an API request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            retries: Number of retries on failure

        Returns:
            Response data as dictionary

        Raises:
            requests.RequestException: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    timeout=30
                )

                # For successful responses
                if response.status_code in (200, 201, 204):
                    if response.status_code == 204:
                        return {}
                    return response.json() if response.text else {}

                # For errors, raise with details
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text

                response.raise_for_status()

            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

        return {}

    # User Management APIs
    def create_user(self, name: str, email: str, role: str = "manager") -> Dict[str, Any]:
        """Create a new user in the organization.

        Args:
            name: User's name
            email: User's email
            role: User's role (owner, manager, or member)

        Returns:
            Created user data
        """
        endpoint = f"/api/v2/{self.organization_id}/users"
        data = {
            "name": name,
            "email": email,
            "role": role,
            "isActive": True
        }
        return self._make_request("POST", endpoint, data=data)

    # Survey Management APIs
    def create_survey(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new survey.

        Args:
            survey_data: Survey configuration data

        Returns:
            Created survey data
        """
        endpoint = "/api/v1/management/surveys"
        # Ensure environmentId is set
        survey_data["environmentId"] = self.environment_id
        return self._make_request("POST", endpoint, data=survey_data)

    def get_survey(self, survey_id: str) -> Dict[str, Any]:
        """Get a survey by ID.

        Args:
            survey_id: Survey ID

        Returns:
            Survey data
        """
        endpoint = f"/api/v1/management/surveys/{survey_id}"
        return self._make_request("GET", endpoint)

    def list_surveys(self) -> List[Dict[str, Any]]:
        """List all surveys in the environment.

        Returns:
            List of surveys
        """
        endpoint = "/api/v1/management/surveys"
        params = {"environmentId": self.environment_id}
        result = self._make_request("GET", endpoint, params=params)
        return result.get("data", []) if isinstance(result, dict) else []

    # Response Management APIs
    def create_response(self, survey_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a survey response using the Client API.

        Args:
            survey_id: Survey ID
            response_data: Response data including answers

        Returns:
            Created response data
        """
        endpoint = f"/api/v1/client/{self.environment_id}/responses"
        data = {
            "surveyId": survey_id,
            **response_data
        }
        return self._make_request("POST", endpoint, data=data)

    def get_responses(self, survey_id: str) -> List[Dict[str, Any]]:
        """Get all responses for a survey.

        Args:
            survey_id: Survey ID

        Returns:
            List of responses
        """
        endpoint = f"/api/v1/management/surveys/{survey_id}/responses"
        result = self._make_request("GET", endpoint)
        return result.get("data", []) if isinstance(result, dict) else []

    # Health check
    def health_check(self) -> bool:
        """Check if the Formbricks instance is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    # Account verification
    def verify_auth(self) -> Dict[str, Any]:
        """Verify API authentication.

        Returns:
            User account information
        """
        endpoint = "/api/v1/me"
        return self._make_request("GET", endpoint)
