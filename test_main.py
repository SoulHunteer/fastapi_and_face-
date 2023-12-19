import time

from fastapi.testclient import TestClient
from main import app, uploaded_images


def test_upload_image():
    with TestClient(app) as client:
        file_path = 'test_image.jpg'
        files = {'file': (file_path, open(file_path, 'rb'))}
        response_upload = client.post("/upload", files=files)
        assert response_upload.status_code == 200
        image_id = response_upload.json()['image_id']
        assert image_id in uploaded_images


def test_get_image():
    with TestClient(app) as client:
        file_path = 'test_image.jpg'
        files = {'file': (file_path, open(file_path, 'rb'))}
        response_upload = client.post("/upload", files=files)
        assert response_upload.status_code == 200
        image_id = response_upload.json()['image_id']
        response_get_image = client.get(f"/get_image/{image_id}?color=blue")
        assert response_get_image.status_code == 200


def test_compare_faces():
    with TestClient(app) as client:
        file_path_1 = 'test_image.jpg'
        files_1 = {'file': (file_path_1, open(file_path_1, 'rb'))}
        response_upload_1 = client.post("/upload", files=files_1)
        assert response_upload_1.status_code == 200
        face_token_1 = response_upload_1.json()['faces'][0]['face_token']

        # Необходимая задержка для API чтобы не было rate limit {'error_message': 'CONCURRENCY_LIMIT_EXCEEDED'}
        time.sleep(2)

        file_path_2 = 'test_image2.jpg'
        files_2 = {'file': (file_path_2, open(file_path_2, 'rb'))}
        response_upload_2 = client.post("/upload", files=files_2)
        assert response_upload_2.status_code == 200
        face_token_2 = response_upload_2.json()['faces'][0]['face_token']

        response_compare_faces = client.post(f"/compare_faces?face_token1={face_token_1}&face_token2={face_token_2}")
        assert response_compare_faces.status_code == 200
        assert 'similarity' in response_compare_faces.json()
        assert response_compare_faces.json()['similarity'] > 0


def test_delete_image():
    with TestClient(app) as client:
        file_path = 'test_image.jpg'
        files = {'file': (file_path, open(file_path, 'rb'))}
        response_upload = client.post("/upload", files=files)
        assert response_upload.status_code == 200
        image_id = response_upload.json()['image_id']

        response_delete_image = client.delete(f"/delete_image/{image_id}")
        assert response_delete_image.status_code == 200

        assert image_id not in uploaded_images
