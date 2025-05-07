from flask import jsonify, request
from flask.views import MethodView
from config import ALLOWED_EXTENSIONS
from errors import HttpError
from dependencies import app
from werkzeug.utils import secure_filename
from model_tasks import upscale, get_task
from functions_db import save_image, get_image


@app.errorhandler(HttpError)
def error_headler(err: HttpError):
    http_responce = jsonify({"error": err.message})
    http_responce.status_code = err.status_code
    return http_responce


class UpscaleView(MethodView):

    def post(self):
        if "file" not in request.files:
            raise HttpError(400, {"error": "No file"})
        file = request.files.get("file")

        if file.filename == "":
            raise HttpError(400, {"error": "File not selected"})

        if file and self.allowed_file(file.filename):
            check_filename = secure_filename(file.filename)
            file.filename = check_filename
            doc_id = save_image(file)
            task = upscale.delay(str(doc_id))
            return jsonify({"task_id": task.id, "doc_id": str(doc_id)})

        else:
            raise HttpError(400, {"error": "Invalid file extension"})

    def allowed_file(self, filename):
        try:
            return (
                "." in filename
                and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
            )
        except Exception:
            return jsonify({"error": "Error checking file extension"})


class TaskView(MethodView):

    def get(self, task_id: str):
        try:
            task = get_task(task_id)
            if task.status == "PENDING":
                return jsonify({
                    "status": task.status,
                    "message": "Task is pending..."
                })

            elif task.status == "RETRY":
                return jsonify({
                    "status": task.status,
                    "message": "Failed, please try again"
                })

            elif task.status == "SUCCESS":
                return jsonify({"status": task.status, "result": "Done!"})

            elif task.status == "FAILURE":
                return jsonify({
                    "status": task.status,
                    "message": "Failed, please try again"
                })
        except Exception as e:
            return jsonify({"error": f"{e}"})


class ProcessedView(MethodView):

    def get(self, doc_id: str):
        image_bytes = get_image(doc_id, upscale_file=True)
        return image_bytes


upscale_view = UpscaleView.as_view("upcsale_view")
task_view = TaskView.as_view("task_view")
processed_view = ProcessedView.as_view("processed_view")

app.add_url_rule("/api/v1/upscale/", view_func=upscale_view, methods=["POST"])

app.add_url_rule(
    "/api/v1/tasks/<string:task_id>",
    view_func=task_view, methods=["GET"]
)

app.add_url_rule(
    "/api/v1/processed/<string:doc_id>",
    view_func=processed_view, methods=["GET"]
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
