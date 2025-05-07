from config import MONGO_DSN
from flask import Flask


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1000 * 1000
app.config["MONGO_URI"] = MONGO_DSN
