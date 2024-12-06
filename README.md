
# README for Incident Analysis Application

## Author
Vamsi Manda
UFID-43226231

## Overview
This application provides tools to process incident data from uploaded or URL-provided PDF files. It generates visual dashboards and clustering insights, offering actionable information through an easy-to-use web interface.

---

## File Structure

```
.
├── .pytest_cache/
├── docs/
│   └── Incident_Report.pdf        # Example report for testing/analysis
├── static/
│   ├── css/
│   │   ├── dashboard.css          # Styling for the dashboard
│   │   └── upload.css             # Styling for the upload page
│   ├── js/
│       └── charts.js              # JavaScript for dashboard charts
├── templates/
│   ├── base.html                  # Common layout template
│   ├── dashboard.html             # Template for dashboard page
│   └── upload.html                # Template for file upload page
├── tests/
│   └── test_main.py               # Pytest cases for testing the Flask app
├── utils/
│   ├── db_handler.py              # Handles database operations
│   ├── pdf_handler.py             # Extracts and processes data from PDFs
│   └── test.pdf                   # Sample PDF for testing purposes
├── COLLABORATORS.md               # List of contributors
├── LICENSE                        # Project license
├── main.py                        # Main Flask application
├── Pipfile                        # Pipenv configuration file
└── Pipfile.lock                   # Locked Pipenv dependencies
```

---

## Features
- **Upload PDFs or Provide URLs**: Process incident data from files or external links.
- **Interactive Dashboards**: Visualize incident trends, clustering results, and geographical heatmaps.
- **Cluster Analysis**: Use K-Means and PCA to group incidents.
- **RESTful API**: Fetch incident summaries in JSON format.

---

## Installation

### Prerequisites
- Python 3.7 or higher
- Pipenv installed (install it using `pip install pipenv`)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Vamsi404/cis6930fa24-project3.git
   ```

2. Install dependencies using Pipenv:
   ```bash
   pipenv install
   ```

3. Start the Flask application:
   ```bash
   pipenv run python main.py
   ```

---

## Running Tests
1. Run tests with pytest:
   ```bash
   pipenv run pytest tests/test_main.py
   ```

---

## Tests Explained
Here’s an explanation of the key tests in `test_main.py`:

### 1. **Test Application Initialization**
This test ensures that the Flask application initializes correctly.

```python
from main import app

def test_app_initialization():
    """
    Test if the Flask application initializes without errors.
    """
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200, "Home page should load successfully."
```

**Explanation**:
- This test uses Flask's `test_client` to simulate a GET request to the home page (`/`).
- It checks whether the response status code is `200` (OK), ensuring the application starts successfully.

---

### 2. **Test File Upload Endpoint**
This test verifies that the `/upload` endpoint processes files correctly.

```python
import io

def test_upload_file():
    """
    Test the file upload functionality with a sample PDF.
    """
    with app.test_client() as client:
        data = {
            'file': (io.BytesIO(b'Test PDF Content'), 'test.pdf')
        }
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200, "File upload should return status code 200."
        assert b"File uploaded successfully" in response.data, "Response should confirm successful upload."
```

**Explanation**:
- A test client is used to simulate a POST request to the `/upload` endpoint.
- A sample PDF file (`test.pdf`) is uploaded as part of the request.
- The test checks that the response is successful (`200`) and that the success message is present in the response.

---

### 3. **Test Database Handling**
This test ensures that database operations, like storing incident data, work as expected.

```python
from utils.db_handler import insert_incident, fetch_incidents

def test_database_operations():
    """
    Test inserting and fetching data from the database.
    """
    # Insert a test record
    incident_data = {
        "id": 1,
        "type": "Test Incident",
        "description": "This is a test record.",
        "location": "Test Location"
    }
    insert_incident(incident_data)

    # Fetch the record and validate it
    incidents = fetch_incidents()
    assert len(incidents) > 0, "Database should contain the inserted record."
    assert incidents[0]['type'] == "Test Incident", "Fetched data should match the inserted record."
```

**Explanation**:
- The test directly interacts with the database using utility functions `insert_incident` and `fetch_incidents`.
- It verifies that data is correctly inserted and retrieved, ensuring database operations work as intended.

---

## Usage Example
1. Launch the application at [http://127.0.0.1:8000](http://127.0.0.1:8000).
2. Upload a PDF or provide a URL to start analysis.
3. View the results on the dashboard, which includes:
   - Bar and pie charts for incident types
   - Heatmaps and clustering outputs
4. Access summarized incident data via the `/data` endpoint in JSON format.

---

## Assumptions
- Input PDFs contain structured and valid incident data.
- URLs provided should directly link to downloadable PDF files.

---

## Known Bugs
- **File Validation**: The application may not handle corrupted or non-standard PDFs gracefully.
- **Data Edge Cases**: Limited handling of missing or malformed data in the PDFs.

---

## External Resources
- Flask Documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- Pytest Documentation: [https://pytest.org/](https://pytest.org/)
- Pandas Documentation: [https://pandas.pydata.org/](https://pandas.pydata.org/)
- Seaborn Documentation: [https://seaborn.pydata.org/](https://seaborn.pydata.org/)

---

## Acknowledgments
This project was self-developed without unapproved external code. Feedback and guidance from the course instructor were strictly followed.
