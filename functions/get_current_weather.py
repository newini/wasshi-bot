#!/usr/bin/env python3
# -*- coding: utf-8 -*
from configs.production import *

# Use Open Weather Map API
def getCurrentWeather(city_jp):
    if city_jp == "":
        return "Cannot recognize your city!"

    translator = Translator()
    city_en = translator.translate(city_jp).text
    
    url = owm_current_url.format(city = city_en, key = OWM_KEY)
    response = requests.get(url)
    data = response.json()

    # Time
    timezone = data["timezone"] # shift second
    unix_time = unix = datetime.datetime.utcnow().timestamp()
    local_time = datetime.datetime.fromtimestamp(unix_time+timezone)

    text = city_jp + " is " + data["weather"][0]["main"] + ":" + data["weather"][0]["description"] + " and " + str(data["main"]["temp"]) + "°C " + str(data["main"]["humidity"]) + "% Now."
    text += "\nCurrent time is " + local_time.strftime("%m/%d %H:%M:%S") + "."
    #text += "Max: " + str(data["main"]["temp_max"]) + "°C, min: " + str(data["main"]["temp_min"]) + "°C"

    return text
