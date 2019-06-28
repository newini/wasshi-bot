#!/usr/bin/env python3
# -*- coding: utf-8 -*
from configs.production import *

# Use Open Weather Map API
def getCurrentWeather(data):
    city_jp = ""
    for word in data["wordList"]:
        if "地域" in word["feature"]:
            city_jp = word["surface"]
            break

    if city_jp == "":
        return "Cannot recognize your city!"

    translator = Translator()
    city_en = translator.translate(city_jp).text
    
    url = owm_current_url.format(city = city_en, key = OWM_KEY)
    response = requests.get(url)
    data = response.json()

    text = city_jp + " is " + data["weather"][0]["main"] + ":" + data["weather"][0]["description"] + " and " + str(data["main"]["temp"]) + "°C " + str(data["main"]["humidity"]) + "% Now."
    #text += "Max: " + str(data["main"]["temp_max"]) + "°C, min: " + str(data["main"]["temp_min"]) + "°C"

    return text
