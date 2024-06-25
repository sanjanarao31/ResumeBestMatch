import pytest
from app import app  # Import your Flask app from the main script

@pytest.fixture
def client():
    # Initialize the Flask app for testing
    app.testing = True
    return app.test_client()

def test_process_resumes_success(client):
    # Write your test cases here
    # For example:
    response = client.post('/process-resumes', json={'context': 'Your context', 'noOfMatches': 3, 'inputPath': 'Your input path'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_process_resumes_error(client):
    # Write your error test cases here
    # For example:
    response = client.post('/process-resumes', json={'context': 12})
    assert response.status_code == 500
