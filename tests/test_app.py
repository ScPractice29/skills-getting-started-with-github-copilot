"""
Unit tests for the High School Management System API

Tests cover:
- Root endpoint redirect
- Getting all activities
- Signing up for activities
- Error handling for invalid activities
- Error handling for duplicate signups
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Save initial state
    initial_state = {
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
        "Basketball": {
            "description": "Team-based basketball games and skills training",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Tennis": {
            "description": "Learn tennis techniques and compete in friendly matches",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": []
        },
        "Pottery": {
            "description": "Learn ceramic art and create pottery pieces on the wheel",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Photography": {
            "description": "Explore photography techniques and build a portfolio",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 8,
            "participants": []
        },
        "Debate Club": {
            "description": "Develop public speaking and critical thinking skills through debate",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Math Olympiad": {
            "description": "Solve challenging math problems and prepare for competitions",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": []
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_state)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(initial_state)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Verify response contains all expected activities
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball" in data
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participants_count(self, client):
        """Test that participants list has correct initial values"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        
        # Basketball should be empty
        assert len(data["Basketball"]["participants"]) == 0


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "alice@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alice@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        # Sign up
        client.post(
            "/activities/Basketball/signup",
            params={"email": "bob@mergington.edu"}
        )
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert "bob@mergington.edu" in data["Basketball"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test that signup fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "alice@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate_email(self, client):
        """Test that duplicate signup is rejected"""
        # Try to sign up someone already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students(self, client):
        """Test that multiple different students can sign up"""
        # Sign up first student
        response1 = client.post(
            "/activities/Tennis/signup",
            params={"email": "student1@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            "/activities/Tennis/signup",
            params={"email": "student2@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both are in participants
        response = client.get("/activities")
        data = response.json()
        assert len(data["Tennis"]["participants"]) == 2
        assert "student1@mergington.edu" in data["Tennis"]["participants"]
        assert "student2@mergington.edu" in data["Tennis"]["participants"]
    
    def test_signup_same_student_different_activities(self, client):
        """Test that same student can sign up for different activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for Basketball
        response1 = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Tennis
        response2 = client.post(
            "/activities/Tennis/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]
        assert email in data["Tennis"]["participants"]


class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_invalid_activity_name_case_sensitive(self, client):
        """Test that activity names are case-sensitive"""
        response = client.post(
            "/activities/basketball/signup",  # lowercase
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_signup_with_empty_email(self, client):
        """Test signup with empty email parameter"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": ""}
        )
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_response_message_format(self, client):
        """Test that response message has proper format"""
        response = client.post(
            "/activities/Photography/signup",
            params={"email": "format@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"].startswith("Signed up")
        assert "format@mergington.edu" in data["message"]
        assert "Photography" in data["message"]
