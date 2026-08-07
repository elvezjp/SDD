"""
API tests for Projects endpoints
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.api
class TestProjectsAPI:
    """Test Projects API endpoints."""

    def test_health_check(self, test_client: TestClient):
        """Test health check endpoint."""
        response = test_client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_check_has_csp_header(self, test_client: TestClient):
        """Test that CSP header is set on responses."""
        response = test_client.get("/api/health")
        csp = response.headers.get("content-security-policy", "")
        assert "default-src 'self'" in csp
        assert "script-src 'self'" in csp
        assert "connect-src 'self';" in csp

    def test_create_project(self, test_client: TestClient, sample_project_data: dict):
        """Test creating a new project."""
        response = test_client.post("/api/projects/", json=sample_project_data)
        assert response.status_code == 201

        data = response.json()
        assert "project_id" in data
        assert data["display_name"] == sample_project_data["display_name"]
        assert data["current_phase"] == 1
        assert "created_at" in data
        assert "phase_status" in data

    def test_create_project_invalid_name(self, test_client: TestClient):
        """Test creating project with invalid name."""
        response = test_client.post("/api/projects/", json={"display_name": ""})
        assert response.status_code == 422  # Validation error

    def test_list_projects_empty(self, test_client: TestClient):
        """Test listing projects when none exist."""
        response = test_client.get("/api/projects/")
        assert response.status_code == 200

        data = response.json()
        assert "projects" in data
        assert "total" in data
        assert isinstance(data["projects"], list)

    def test_list_projects(self, test_client: TestClient):
        """Test listing projects."""
        # Create some projects
        test_client.post("/api/projects/", json={"display_name": "project-1"})
        test_client.post("/api/projects/", json={"display_name": "project-2"})

        response = test_client.get("/api/projects/")
        assert response.status_code == 200

        data = response.json()
        assert data["total"] >= 2
        assert len(data["projects"]) >= 2

    def test_get_project(self, test_client: TestClient, sample_project_data: dict):
        """Test getting project details."""
        # Create project and capture project_id
        create_response = test_client.post("/api/projects/", json=sample_project_data)
        project_id = create_response.json()["project_id"]

        # Get project by project_id
        response = test_client.get(f"/api/projects/{project_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["project_id"] == project_id
        assert data["display_name"] == sample_project_data["display_name"]

    def test_get_project_not_found(self, test_client: TestClient):
        """Test getting non-existent project."""
        response = test_client.get("/api/projects/00000000")
        assert response.status_code == 404

    def test_get_project_status(self, test_client: TestClient, sample_project_data: dict):
        """Test getting project status."""
        # Create project
        create_response = test_client.post("/api/projects/", json=sample_project_data)
        project_id = create_response.json()["project_id"]

        # Get status
        response = test_client.get(f"/api/projects/{project_id}/status")
        assert response.status_code == 200

        data = response.json()
        assert data["project_id"] == project_id
        assert "current_phase" in data
        assert "phases" in data
        assert "overall_progress" in data
        assert len(data["phases"]) == 7

        # Check each phase info
        for phase in data["phases"]:
            assert "phase_num" in phase
            assert "phase_name" in phase
            assert "status" in phase
            assert "qa_count" in phase

    def test_delete_project(self, test_client: TestClient, sample_project_data: dict):
        """Test deleting a project."""
        # Create project
        create_response = test_client.post("/api/projects/", json=sample_project_data)
        project_id = create_response.json()["project_id"]

        # Delete project
        response = test_client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 204

        # Verify project is deleted
        response = test_client.get(f"/api/projects/{project_id}")
        assert response.status_code == 404

    def test_delete_project_not_found(self, test_client: TestClient):
        """Test deleting non-existent project."""
        response = test_client.delete("/api/projects/00000000")
        assert response.status_code == 404


@pytest.mark.api
@pytest.mark.integration
class TestProjectsWorkflow:
    """Test complete project workflow."""

    def test_create_get_delete_workflow(self, test_client: TestClient):
        """Test complete CRUD workflow."""
        # 1. Create project
        create_response = test_client.post(
            "/api/projects/",
            json={"display_name": "workflow-test"}
        )
        assert create_response.status_code == 201
        project_id = create_response.json()["project_id"]

        # 2. List projects
        list_response = test_client.get("/api/projects/")
        assert list_response.status_code == 200
        projects = list_response.json()["projects"]
        assert any(p["project_id"] == project_id for p in projects)

        # 3. Get project details
        get_response = test_client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 200
        assert get_response.json()["display_name"] == "workflow-test"

        # 4. Get project status
        status_response = test_client.get(f"/api/projects/{project_id}/status")
        assert status_response.status_code == 200
        assert status_response.json()["overall_progress"] == 0.0

        # 5. Delete project
        delete_response = test_client.delete(f"/api/projects/{project_id}")
        assert delete_response.status_code == 204

        # 6. Verify deletion
        verify_response = test_client.get(f"/api/projects/{project_id}")
        assert verify_response.status_code == 404
