import time

from fastapi.testclient import TestClient

from main import app

create_data = {"x": 1, "y": 2, "operator": "+"}
validation_data = [{"x": 1, "y": 2, "operator": "1"}, {"x": 1, "y": 2, "operator": "+-"}]
validation_data_int = [{"x": "y", "y": 2, "operator": "+"}, {"x": 1, "y": "j", "operator": "+"}]
operators = [{"x": 2, "y": 2, "operator": "+"}, {"x": 3, "y": 3, "operator": "*"},
             {"x": 5, "y": 2, "operator": "-"}, {"x": 8, "y": 2, "operator": "/"}]
results = [4, 9, 3, 4]


def test_create_task():
    with TestClient(app) as client:
        response = client.post("/calculate", json=create_data)
        assert response.status_code == 201
        assert response.json() == {"id": 1}
        response = client.get("/getresult", params={"task_id": 1})
        assert response.status_code == 200
        assert response.json() == {"await": 'task in progress'}
        response = client.get("/task")
        assert response.status_code == 200
        assert len(response.json()['tasks']) == 1


def test_autoincrement_id():
    with TestClient(app) as client:
        for i in range(1, 5):
            response = client.post("/calculate", json=create_data)
            assert response.status_code == 201
            assert response.json() == {"id": i}


def test_validation_input():
    with TestClient(app) as client:
        for date in validation_data:
            response = client.post("/calculate", json=date)
            assert response.status_code == 422
            assert response.json() == {"detail": 'invalid operator'}

        for date in validation_data_int:
            response = client.post("/calculate", json=date)
            assert response.status_code == 422

        response = client.get("/task")
        assert response.status_code == 200
        assert len(response.json()['tasks']) == 0


def test_divide_by_zero():
    with TestClient(app) as client:
        response = client.post("/calculate", json={"x": 1, "y": 0, "operator": "/"})
        assert response.status_code == 422


def test_operator():
    with TestClient(app) as client:
        for date in operators:
            response = client.post("/calculate", json=date)
            assert response.status_code == 201


def test_task_count():
    with TestClient(app) as client:
        for date in operators + [create_data]:
            response = client.post("/calculate", json=date)
            assert response.status_code == 201
        response = client.get("/task")
        assert response.status_code == 200
        assert len(response.json()['tasks']) == 5


def test_get_result():
    with TestClient(app) as client:
        for date in operators + [create_data]:
            response = client.post("/calculate", json=date)
            assert response.status_code == 201
        count = len(operators + [create_data]) + 1
        for i in range(1, count):
            response = client.get("/getresult", params={"task_id": i})
            assert response.status_code == 200
            assert response.json() == {"await": 'task in progress'}
        response = client.get("/getresult", params={"task_id": count})
        assert response.status_code == 404
        assert response.json() == {"error": "id not found"}


def test_result():
    with TestClient(app) as client:
        for date in operators:
            response = client.post("/calculate", json=date)
            assert response.status_code == 201
        response = client.get("/task")
        assert response.status_code == 200
        time.sleep(4)
        for i in range(1, len(operators)):
            response = client.get("/getresult", params={"task_id": i})
            assert response.json()['result'] == results[i - 1]
