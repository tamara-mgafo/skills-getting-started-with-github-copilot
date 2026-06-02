import copy

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

INITIAL_ACTIVITIES = copy.deepcopy(activities)


def setup_function():
    """Reset the in-memory activity state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_signup_adds_participant_and_returns_updated_activity():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}

    refreshed = client.get("/activities")
    assert refreshed.status_code == 200
    assert new_email in refreshed.json()[activity_name]["participants"]


def test_remove_participant_deletes_existing_participant():
    # Arrange
    activity_name = "Gym Class"
    participant_email = "john@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {participant_email} from {activity_name}"}

    refreshed = client.get("/activities")
    assert refreshed.status_code == 200
    assert participant_email not in refreshed.json()[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request():
    # Arrange
    activity_name = "Programming Class"
    existing_email = "emma@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
