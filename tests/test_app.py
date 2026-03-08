from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory data so tests do not leak state.
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_all():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert "Programming Class" in body


def test_signup_success():
    # Arrange
    client = TestClient(app)
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    client = TestClient(app)
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_success():
    # Arrange
    client = TestClient(app)
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_missing_returns_404():
    # Arrange
    client = TestClient(app)
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_signup_unknown_activity_returns_404():
    # Arrange
    client = TestClient(app)
    email = "somebody@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unknown_activity_returns_404():
    # Arrange
    client = TestClient(app)
    email = "somebody@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

