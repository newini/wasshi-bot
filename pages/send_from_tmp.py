#!/usr/bin/env python3
# coding:UTF-8
FILE_NAME = "send_from_tmp.py"
from configs.imports import *

send_from_tmp_api = Blueprint("send_from_tmp_api", __name__)


@send_from_tmp_api.route("/send_from_tmp", methods=["GET"])
def send_from_tmp():
    if request.args.get("filename"):
        filename = request.args.get("filename")
    if not filename:
        return "ERROR!"
    return send_from_directory("tmp/", filename)
