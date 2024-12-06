import pytest
import sys
import os
from io import BytesIO
import io
# Add the outer folder to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app  # Import `main.py` from the outer folder
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test the home route
def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Upload' in response.data  # Check if 'Upload' appears on the page

# Test file upload with no file
def test_upload_no_file(client):
    response = client.post('/upload', data={})
    assert response.status_code == 400
    assert b'No file or URL provided' in response.data

# Test file upload with invalid file type
def test_upload_invalid_file_type(client):
    data = {
        'file': (io.BytesIO(b"Not a PDF content"), 'test.txt')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b'Invalid file type' in response.data

# Test dashboard route with no data
def test_dashboard_no_data(client):
    response = client.get('/dashboard')
    assert response.status_code == 400
    assert b'No data available for dashboard' in response.data

# Test data API with no data
def test_get_data_no_data(client):
    response = client.get('/data')
    assert response.status_code == 500  # Should handle the error properly
    assert b'Error fetching incident summary' in response.data
