import gridfs
import pymongo.database
from bson import ObjectId
from dependencies import app
from flask_pymongo import PyMongo
from errors import HttpError
from cachetools import cached
from werkzeug.datastructures import FileStorage


mongo = PyMongo(app)


@cached({})
def get_db() -> pymongo.database.Database:
    return mongo.db


@cached({})
def get_fs() -> gridfs.GridFS:
    return gridfs.GridFS(get_db())


def get_image(doc_id: str, upscale_file=False) -> bytes:
    db = get_db()
    fs = get_fs()

    document = db["upscale"].find_one({"_id": ObjectId(doc_id)})

    if upscale_file:
        file_id = document["upscale_file"]
        image = fs.get(file_id)
        if image:
            return image.read()
        else:
            raise HttpError(404, "Upscale file not found")

    elif document and "original_file" in document:
        file_id = document["original_file"]
        image = fs.get(file_id)
        if image:
            return image.read()
        else:
            raise HttpError(404, "Original file not found")
    else:
        raise HttpError(404, "Document not found")


def update_image(new_file: bytes, doc_id: str) -> dict:
    fs = get_fs()
    db = get_db()

    document = db["upscale"].find_one({"_id": ObjectId(doc_id)})
    if document:
        new_file_id = fs.put(new_file)

        result = db["upscale"].update_one(
            {"_id": ObjectId(doc_id)}, {"$set": {"upscale_file": new_file_id}}
        )
        if result.matched_count > 0:
            return db["upscale"].find_one({"_id": result.upserted_id})
        else:
            raise HttpError(406, "The document does not exist in the database")
    else:
        raise HttpError(404, "Document not found")


def save_image(file: FileStorage) -> ObjectId:
    fs = get_fs()
    file_id = fs.put(file, filename=file.filename)

    # Сохраняем метаданные о файле в основной коллекции
    db = get_db()
    result = db["upscale"].insert_one({
        "name": f"{file.filename}",
        "original_file": file_id,
        "upscale_file": None
    })

    return result.inserted_id
