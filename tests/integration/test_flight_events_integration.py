import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_real_flight_events_api(test_app: AsyncClient):
    response = await test_app.get(
        "/journeys/search",
        params={"from": "MAD", "to": "BUE", "departure_date": "2021-12-31"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "connections": 0,
            "path": [
                {
                    "flight_number": "IB1234",
                    "from": "MAD",
                    "to": "BUE",
                    "departure_time": "2021-12-31T23:59:59Z",
                    "arrival_time": "2022-01-01T12:00:00Z",
                }
            ],
        }
    ]


@pytest.mark.asyncio
async def test_real_flight_events_api_with_unexisting_airport_destination(
    test_app: AsyncClient,
):
    response = await test_app.get(
        "/journeys/search",
        params={"from": "MAD", "to": "XXX", "departure_date": "2021-12-31"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_real_flight_events_api_with_unexisting_airport_origin(
    test_app: AsyncClient,
):
    response = await test_app.get(
        "/journeys/search",
        params={"from": "XXX", "to": "BUE", "departure_date": "2021-12-31"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_real_flight_events_api_with_existing_airports_and_no_route(
    test_app: AsyncClient,
):
    response = await test_app.get(
        "/journeys/search",
        params={"from": "BUE", "to": "MAD", "departure_date": "2021-12-31"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
