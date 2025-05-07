import cv2
import numpy as np
from dependencies import app
from cv2 import dnn_superres
from celery.result import AsyncResult
from functions_db import get_image, update_image
from celery_utils import celery_app_instance

celery = celery_app_instance(app)


@celery.task
def upscale(doc_id: str, model_path: str = "EDSR_x2.pb") -> None:
    """
    :param doc_id: id загружаемого документа
    :return:
    """

    scaler = dnn_superres.DnnSuperResImpl_create()
    scaler.readModel(model_path)
    scaler.setModel("edsr", 2)

    image_bytes = get_image(doc_id)
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result = scaler.upsample(image)

    # Кодирование результата в формат, подходящий для хранения в MongoDB
    _, buffer = cv2.imencode(".jpg", result)
    result_bytes = buffer.tobytes()
    result = update_image(result_bytes, doc_id)
    return result


def get_task(task_id: str) -> AsyncResult:
    return AsyncResult(task_id, app=celery)
