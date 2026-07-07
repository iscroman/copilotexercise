from fastapi.testclient import TestClient

from src import app as app_module


def test_unregister_participant():
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    original_participants = list(app_module.activities[activity_name]["participants"])

    try:
        email = original_participants[0]
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in app_module.activities[activity_name]["participants"]
    finally:
        app_module.activities[activity_name]["participants"] = original_participants
