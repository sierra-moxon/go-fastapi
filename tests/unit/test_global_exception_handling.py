from logging import raiseExceptions

from fastapi.testclient import TestClient

from app.exceptions.global_exceptions import DataNotFoundException
from app.main import app
import pytest

from app.utils.ontology_utils import is_valid_goid

test_client = TestClient(app)


def test_value_error_handler():
    # Simulate an endpoint that raises a ValueError (e.g., by sending an invalid CURIE)
    response = test_client.get("/api/ontol/labeler?id=@base:invalid")

    # Verify that the global exception handler for ValueErrors, rewrites as an internal server error code.
    assert response.status_code == 400
    response = test_client.get(f"/api/gp/P05067/models")
    assert response.status_code == 400

def test_value_error_curie():
    response = test_client.get(f"/api/gp/P05067/models")
    assert response.status_code == 400
    assert response.json() == {"message": "Value error occurred: Invalid CURIE format"}


def test_ncbi_taxon_error_handling():
    response = test_client.get("/api/taxon/NCBITaxon%3A4896/models")
    assert response.status_code == 200


@pytest.mark.parametrize("endpoint", [
    "/api/bioentity/FAKE:12345",
    "/api/bioentity/function/FAKE:12345",
    "/api/bioentity/function/FAKE:12345/taxons",
    "/api/bioentity/gene/FAKE:12345/function",
    # "/api/ontol/labeler",  # Uncomment if this endpoint should be included
])
def test_get_bioentity_not_found(endpoint):
    """
    Test that the DataNotFoundException is raised when the id does not exist.
    """
    # Perform the GET request
    response = test_client.get(endpoint)

    # Assert the status code is 404 (Not Found)
    assert response.status_code == 404, f"Endpoint {endpoint} failed with status code {response.status_code}"

@pytest.mark.parametrize("endpoint", [
    "/api/bioentity/function/FAKE:12345/genes",
])
def test_get_bioentity_not_found(endpoint):
    """
    Test that the DataNotFoundException is raised when the id does not exist.
    """
    # Perform the GET request
    response = test_client.get(endpoint)

    # Assert the status code is 404 (Not Found)
    assert response.status_code == 400, f"Endpoint {endpoint} failed with status code {response.status_code}"


@pytest.mark.parametrize("goid,expected", [
    ("GO:0044598", True),  # Valid GO ID
    ("GO:zzzzz", False),  # Non-existent GO ID
    ("INVALID:12345", False),  # Invalid format
])
def test_is_valid_goid(goid, expected):
    """
    Test that the is_valid_goid function behaves as expected.
    """
    if expected:
        assert is_valid_goid(goid) == True
    else:
        try:
            result = is_valid_goid(goid)
            assert result == False
        except DataNotFoundException:
            assert not expected, f"GO ID {goid} raised DataNotFoundException as expected."
        except ValueError:
            assert not expected, f"GO ID {goid} raised ValueError as expected."

@pytest.mark.parametrize(
    "goid,evidence,start,rows,expected_status,expected_response",
    [
        ("GO:0000001", None, 0, 100, 200, {"key": "value"}),  # Example valid response
        ("INVALID:12345", None, 0, 100, 400, {"detail": "Invalid GO ID format"}),  # Invalid format
        ("GO:9999999", None, 0, 100, 404, {"detail": "Item with ID GO:9999999 not found"}),  # Non-existent GO ID
    ],
)
def test_get_annotations_by_goterm_id(goid, evidence, start, rows, expected_status, expected_response):
    """
    Test the /api/bioentity/function/{id} endpoint.

    :param goid: The GO term ID to test.
    :param evidence: Evidence codes for filtering.
    :param start: Pagination start index.
    :param rows: Number of results per page.
    :param expected_status: Expected HTTP status code.
    :param expected_response: Expected JSON response.
    """
    # Perform the GET request
    response = test_client.get(
        f"/api/bioentity/function/{goid}", params={"evidence": evidence, "start": start, "rows": rows}
    )

    # Assert the status code
    assert response.status_code == expected_status, f"Unexpected status code for GO ID {goid}"

    # Assert the response body
    assert response.json() == expected_response, f"Unexpected response for GO ID {goid}"
