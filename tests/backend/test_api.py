import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_state = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(original_state)


def test_get_activities_returns_catalog():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["max_participants"] == 12


def test_signup_for_activity_adds_participant():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    existing_email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity():
    # Arrange
    client = TestClient(app_module.app)

    # Act
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_student():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_returns_404_for_missing_participant():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{missing_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"
