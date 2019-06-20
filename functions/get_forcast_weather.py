#!/usr/bin/env python3
#coding:UTF-8

import os, requests, datetime

# Translate
from googletrans import Translator

# Open Weather Map
OWM_KEY = os.environ["OWM_KEY"]
owm_forcast_url = "http://api.openweathermap.org/data/2.5/forecast?units=metric&q={city}&APPID={key}&lang=ja"
forcast_day = 1 # 1 day

# Timezone
timezone = 9
JST = datetime.timezone(datetime.timedelta(hours=timezone), 'JST')

# Use Open Weather Map API
def getForcastWeather(data):
    city_jp = ""
    for word in data["wordList"]:
        if "地域" in word["feature"]:
            city_jp = word["surface"]
            break

    if city_jp == "":
        return "Cannot recognize your city!"

    translator = Translator()
    city_en = translator.translate(city_jp).text

    url = owm_forcast_url.format(city = city_en, key = OWM_KEY)
    response = requests.get(url)
    data = response.json()

    text = ""
    cnt = 0
    for forcast_list in data["list"]:
        if cnt > 8*forcast_day: break
        text += ("\n"+ datetime.datetime.fromtimestamp(forcast_list["dt"], JST).strftime('%m/%d %H:%M') + " " + str(forcast_list["main"]["temp"]) + "°C "
                + forcast_list["weather"][0]["main"] + ":" + forcast_list["weather"][0]["description"])
        cnt += 1

    return text
