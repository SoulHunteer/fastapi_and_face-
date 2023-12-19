from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from PIL import Image, ImageDraw
from io import BytesIO

app = FastAPI()
API_KEY = ''
API_SECRET = ''

# Использование словаря здесь исключительно чтобы не отвлекаться на БД
# В реальной жизни разумеется так делать не стоит
uploaded_images = {}


def highlight_faces(image_data, faces, color='red'):
    """
    Выделяет лица на изображении прямоугольниками указанного цвета.

    :param image_data: Данные изображения в байтах.
    :param faces: Информация о лицах на изображении.
    :param color: Цвет прямоугольников (по умолчанию - 'red').
    :return: Изображение с выделенными лицами в байтах.
    """
    img = Image.open(BytesIO(image_data))
    draw = ImageDraw.Draw(img)

    for face in faces:
        face_rectangle = face['face_rectangle']
        left = face_rectangle['left']
        top = face_rectangle['top']
        right = left + face_rectangle['width']
        bottom = top + face_rectangle['height']

        draw.rectangle([left, top, right, bottom], outline=color, width=2)

    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return buffered.getvalue()



@app.post("/upload", response_model=dict)
async def upload_image(file: UploadFile = File(...)):
    """
    Загружает изображение, обращается к FacePlusPlus для распознавания лиц
    и сохраняет информацию о лицах и изображении.

    :param file: Загружаемое изображение.
    :return: Информация о загруженном изображении и распознанных лицах.
    """
    async with httpx.AsyncClient() as client:
        file_bytes = file.file.read()
        response = await client.post(
            'https://api-us.faceplusplus.com/facepp/v3/detect',
            params={'api_key': API_KEY, 'api_secret': API_SECRET},
            files={'image_file': (file.filename, file.file)}
        )

    data = response.json()
    print(data)
    image_id = len(uploaded_images) + 1
    uploaded_images[image_id] = {'faces': data['faces'], 'file': file_bytes}

    return {'image_id': image_id, 'faces': data['faces']}


@app.get("/get_image/{image_id}", response_class=StreamingResponse)
async def get_image(image_id: int, color: str = 'red', faces: list = []):
    """
    Возвращает изображение с выделенными лицами по указанному идентификатору.

    :param image_id: Идентификатор загруженного изображения.
    :param color: Цвет для выделения лиц (по умолчанию - 'red').
    :param faces: Массив токенов лиц для выделения (необязательно).
    :return: Изображение с выделенными лицами.
    """
    if image_id not in uploaded_images:
        raise HTTPException(status_code=404, detail='Image not found')

    image_data = uploaded_images[image_id]
    highlighted_image = highlight_faces(image_data['file'], image_data['faces'], color=color)

    return StreamingResponse(BytesIO(highlighted_image), media_type="image/jpeg")


@app.post("/compare_faces", response_model=dict)
async def compare_faces(face_token1: str, face_token2: str):
    """
    Сравнивает два лица по токенам и возвращает вероятность совпадения.

    :param face_token1: Токен первого лица.
    :param face_token2: Токен второго лица.
    :return: Вероятность совпадения (от 1 до 100).
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'https://api-us.faceplusplus.com/facepp/v3/compare?face_token1={face_token1}&face_token2={face_token2}',
            params={'api_key': API_KEY, 'api_secret': API_SECRET}
        )

    similarity = response.json().get('confidence', 0)
    print(response.json())
    return {'similarity': similarity}


@app.delete("/delete_image/{image_id}", response_model=dict)
async def delete_image(image_id: int):
    """
    Удаляет изображение по указанному идентификатору.

    :param image_id: Идентификатор загруженного изображения.
    :return: Сообщение об успешном удалении изображения.
    """
    if image_id not in uploaded_images:
        raise HTTPException(status_code=404, detail='Image not found')

    del uploaded_images[image_id]
    return {'message': 'Image deleted successfully'}
