import os
from flask import Blueprint

if not os.path.exists("tmp"):
    os.makedirs("tmp")

tmp_api = Blueprint("tmp_api", __name__,
    static_url_path='/tmp', static_folder='tmp'
)
