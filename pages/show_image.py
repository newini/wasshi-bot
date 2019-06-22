#!/usr/bin/env python3
#coding:UTF-8
from configs.imports import *

PAGE_NAME = "show_image"


show_image_api = Blueprint('show_image_api', __name__)

@show_image_api.route("/show_image", methods=['GET'])
def show_image():
    if request.args.get("city"): city = request.args.get("city")

    if not city: return "ERROR!"

    return render_template("show_image.html", city=city)
