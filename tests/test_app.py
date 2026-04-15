import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial activities data for resetting
INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for interscholastic play",
        "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["ryan@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Tennis training and friendly matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["alex@mergington.edu", "jordan@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and mixed media projects",
        "schedule": "Wednesdays and Saturdays, 2:00 PM - 4:00 PM",
        "max_participants": 25,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Drama Club": {
        "description": "Theater productions and performance techniques",
        "schedule": "Thursdays, 3:30 PM - 5:30 PM",
        "max_participants": 30,
        "participants": ["natalie@mergington.edu"]
    },
    "Debate Team": {
        "description": "Competitive debate and public speaking skills",
        "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["marcus@mergington.edu", "ava@mergington.edu"]
    },
    "Science Club": {
        "description": "Hands-on experiments and scientific exploration",
        "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["henry@mergington.edu"]
    }
}

@pytest.fixture
def client():
    return TestClient(app, follow_redirects=False)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update(INITIAL_ACTIVITIES)

def test_root_redirect(client):
    """Test that root path redirects to static index"""
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test getting all activities returns correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9
    assert "Chess Club" in data

    # Check structure of one activity
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)
    assert len(activity["participants"]) == 2  # michael and daniel

def test_signup_success(client):
    """Test successful signup adds participant"""
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for Chess Club" == data["message"]

    # Verify added to participants
    response = client.get("/activities")
    data = response.json()
    assert email in data["Chess Club"]["participants"]

def test_signup_activity_not_found(client):
    """Test signup for non-existent activity returns 404"""
    response = client.post("/activities/NonExistent/signup?email=test@test.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_signup_already_signed_up(client):
    """Test signup when already signed up returns 400"""
    email = "duplicate@mergington.edu"
    # First signup
    client.post(f"/activities/Chess Club/signup?email={email}")
    # Second signup should fail
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_case_sensitive_activity(client):
    """Test that activity names are case sensitive"""
    response = client.post("/activities/chess club/signup?email=test@test.com")
    assert response.status_code == 404  # "chess club" != "Chess Club"

def test_signup_empty_email(client):
    """Test signup with empty email (currently allowed)"""
    response = client.post("/activities/Chess Club/signup?email=")
    assert response.status_code == 200  # Currently no validation
    # Verify empty string added
    response = client.get("/activities")
    data = response.json()
    assert "" in data["Chess Club"]["participants"]

def test_signup_whitespace_email(client):
    """Test signup with whitespace in email"""
    email = " test@test.com "
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    # Verify whitespace preserved
    response = client.get("/activities")
    data = response.json()
    assert email in data["Chess Club"]["participants"]

def test_delete_success(client):
    """Test successful unregister removes participant"""
    email = "michael@mergington.edu"  # Already signed up
    response = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from Chess Club" == data["message"]

    # Verify removed from participants
    response = client.get("/activities")
    data = response.json()
    assert email not in data["Chess Club"]["participants"]

def test_delete_activity_not_found(client):
    """Test delete from non-existent activity returns 404"""
    response = client.delete("/activities/NonExistent/signup?email=test@test.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_delete_not_signed_up(client):
    """Test delete when not signed up returns 404"""
    email = "notsignedup@mergington.edu"
    response = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 404
    data = response.json()
    assert "not signed up" in data["detail"]

def test_delete_case_sensitive_activity(client):
    """Test that delete activity names are case sensitive"""
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/chess club/signup?email={email}")
    assert response.status_code == 404  # "chess club" != "Chess Club"

def test_data_integrity_multiple_operations(client):
    """Test that multiple signups and deletes maintain data integrity"""
    email1 = "student1@mergington.edu"
    email2 = "student2@mergington.edu"

    # Signup two students
    client.post(f"/activities/Programming Class/signup?email={email1}")
    client.post(f"/activities/Programming Class/signup?email={email2}")

    # Check both added
    response = client.get("/activities")
    data = response.json()
    participants = data["Programming Class"]["participants"]
    assert email1 in participants
    assert email2 in participants
    assert len(participants) == 4  # 2 original + 2 new

    # Delete one
    client.delete(f"/activities/Programming Class/signup?email={email1}")

    # Check one removed, one remains
    response = client.get("/activities")
    data = response.json()
    participants = data["Programming Class"]["participants"]
    assert email1 not in participants
    assert email2 in participants
    assert len(participants) == 3  # 2 original + 1 new

def test_no_duplicates_after_signup(client):
    """Test that signup doesn't create duplicates"""
    email = "unique@mergington.edu"
    # Signup twice (second should fail)
    client.post(f"/activities/Chess Club/signup?email={email}")
    client.post(f"/activities/Chess Club/signup?email={email}")  # Should fail

    # Check only one instance
    response = client.get("/activities")
    data = response.json()
    participants = data["Chess Club"]["participants"]
    assert participants.count(email) == 1