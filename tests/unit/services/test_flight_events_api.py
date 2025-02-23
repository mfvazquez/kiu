import pytest
import pytest_asyncio
import httpx
from datetime import datetime
from typing import List
from unittest.mock import AsyncMock, Mock, patch

from app.services.flight_events import FlightEvent
from app.services.flight_events.flight_events_api import FlightEventsAPIService
from app.services.flight_events.exceptions import FlightEventsAPIError


@pytest_asyncio.fixture
def api_service():
    return FlightEventsAPIService(api_url="http://test-api.com/flights")


@pytest_asyncio.fixture
def sample_api_response() -> List[dict]:
    return [
        {
            "flight_number": "AA100",
            "departure_city": "BUE",
            "arrival_city": "MAD",
            "departure_datetime": "2024-09-12T08:00:00",
            "arrival_datetime": "2024-09-12T22:00:00",
        },
        {
            "flight_number": "IB200",
            "departure_city": "MAD",
            "arrival_city": "LON",
            "departure_datetime": "2024-09-13T10:00:00",
            "arrival_datetime": "2024-09-13T12:00:00",
        },
    ]


@pytest_asyncio.fixture
async def mock_httpx_client(sample_api_response):
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_api_response
    mock_response.raise_for_status.return_value = None

    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    return mock_client


@pytest.mark.asyncio
async def test_get_flight_events_success(
    api_service: FlightEventsAPIService, mock_httpx_client
):
    """Should fetch and parse flight events correctly"""
    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        events = await api_service.get_flight_events()

        # Verify the API was called correctly
        mock_httpx_client.get.assert_called_once_with(
            "http://test-api.com/flights", timeout=30.0
        )

        # Verify response parsing
        assert len(events) == 2
        assert isinstance(events[0], FlightEvent)
        assert events[0].flight_number == "AA100"
        assert events[0].departure_datetime == datetime(2024, 9, 12, 8, 0)

        assert events[1].flight_number == "IB200"
        assert events[1].departure_datetime == datetime(2024, 9, 13, 10, 0)


@pytest.mark.asyncio
async def test_get_flight_events_api_error(
    api_service: FlightEventsAPIService, mock_httpx_client
):
    """Should handle API errors correctly"""
    mock_httpx_client.get.side_effect = httpx.RequestError("Connection failed")

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        with pytest.raises(FlightEventsAPIError) as exc_info:
            await api_service.get_flight_events()

        assert "Connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_invalid_response_format(
    api_service: FlightEventsAPIService, mock_httpx_client
):
    """Should handle invalid response format"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"invalid": "data"}]
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.get.return_value = mock_response

    with patch("httpx.AsyncClient", return_value=mock_httpx_client):
        with pytest.raises(FlightEventsAPIError) as exc_info:
            await api_service.get_flight_events()

        assert "validation error" in str(exc_info.value).lower()
