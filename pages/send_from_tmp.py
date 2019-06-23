#!/usr/bin/env python3
#coding:UTF-8
FILE_NAME = "send_from_tmp.py"
from configs.imports import *

from flask import Flask, send_from_directory

send_from_tmp_api = Blueprint('send_from_tmp_api', __name__)

@send_from_tmp_api.route("/send_from_tmp/<filename>")
#@send_from_tmp_api.route("/send_from_tmp", methods=['GET'])
def send_from_tmp(filename):
    print(filename)
    return send_from_directory('tmp/', filename)
