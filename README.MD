
# Face Recognition API

Face Recognition API - это сервис для распознавания лиц с использованием FacePlusPlus API.

## Установка

1. Установите зависимости:

```bash
pip install -r requirements.txt
```

2. Запустите сервер:

```bash
uvicorn main:app --reload
```

## Эндпоинты

### 1. Загрузка изображения

- **Метод**: POST
- **Путь**: `/upload`

Этот эндпоинт позволяет загрузить изображение для распознавания лиц.

### 2. Получение изображения по id

- **Метод**: GET
- **Путь**: `/get_image/{image_id}`

Получает изображение с выделенными лицами по идентификатору и массиву токенов лиц.

### 3. Сравнение двух лиц по токенам

- **Метод**: POST
- **Путь**: `/compare_faces`

Сравнивает два лица по их токенам и возвращает вероятность совпадения.

### 4. Удаление изображения

- **Метод**: DELETE
- **Путь**: `/delete_image/{image_id}`

Удаляет изображение по его идентификатору.

## Примеры использования

### 1. Пример загрузки изображения и получения идентификатора и токенов лиц:

```python
import requests

files = {'file': ('image.jpg', open('test_image.jpg', 'rb'))}
upload_response = requests.post('http://127.0.0.1:8000/upload', files=files)

image_id = upload_response.json()['image_id']
face_tokens = [face['face_token'] for face in upload_response.json()['faces']]

print(f"ID изображения: {image_id}")
print(f"Токены лиц: {face_tokens}")
```

### 2. Пример получения изображения с выделенными лицами по идентификатору и токенам лиц:

```python
import requests

image_id = 1
response = requests.get(f'http://127.0.0.1:8000/get_image/{image_id}?color=red&faces=["face_token_1", "face_token_2"]')

with open('highlighted_image.jpg', 'wb') as f:
    f.write(response.content)

print("Новое изображение сохранено")
```

### 3. Пример сравнения двух лиц по токенам:

```python
import requests

face_token_1 = "face_token_1"
face_token_2 = "face_token_2"

compare_response = requests.post(
            f'https://api-us.faceplusplus.com/facepp/v3/compare?face_token1={face_token_1}&face_token2={face_token_2}')

similarity = compare_response.json()['similarity']
print(f"Процент совпадения двух лиц равен: {similarity}%")
```

### 4. Пример удаления изображения по идентификатору:

```python
import requests

image_id = 1
delete_response = requests.delete(f'http://127.0.0.1:8000/delete_image/{image_id}')

if delete_response.status_code == 200:
    print(f"Изображение с ID {image_id} успешно удалено")
else:
    print(f"Ошибка удаления изображения с ID {image_id}")
```

Эти примеры могут быть использованы в вашем клиентском коде для взаимодействия с вашим API для распознавания лиц. Пожалуйста, замените фиктивные значения на реальные ваши токены и идентификаторы изображений.

## Тестирование

Проект включает в себя набор тестов для проверки функциональности API. Для запуска тестов выполните следующие шаги:

1. Установите pytest:

```bash
pip install pytest
```

2. Запустите тесты с использованием Pytest:

```bash
pytest test_main.py
```

Эти тесты включают в себя проверки для эндпоинтов загрузки изображения, получения изображения, сравнения лиц и удаления изображения. Убедитесь, что ваш сервер работает перед запуском тестов.

## Конфигурация FacePlusPlus API

Для корректной работы сервиса, необходимо вставить `API_KEY` и `API_SECRET` в файле `main.py`.
