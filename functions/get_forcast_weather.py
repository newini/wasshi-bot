#!/usr/bin/env python3
#coding:UTF-8

import os, requests, datetime

from linebot.models import CarouselColumn

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
    x = []
    y = []
    for forcast_list in data["list"]:
        if cnt > 8*forcast_day: break
        text += ("\n"+ datetime.datetime.fromtimestamp(forcast_list["dt"], JST).strftime('%m/%d %H:%M') + " " + str(forcast_list["main"]["temp"]) + "°C "
                + forcast_list["weather"][0]["main"] + ":" + forcast_list["weather"][0]["description"])
        x.append(datetime.datetime.fromtimestamp(forcast_list["dt"], JST))
        y.append(forcast_list["main"]["temp"])
        cnt += 1

    # Get plotly page
    wasshi_url = "https://wasshi-bot.herokuapp.com/"
    page_name = "plot_graph"
    params = {"city": city_jp, "x": x, "y": y}
    print(params)
    plot_response = requests.get(url = wasshi_url+page_name, params = params)

    capsules = []
    capsules.append(
        CarouselColumn(
            #thumbnail_image_url=dict_elem["image"],
            #title=dict_elem["title"][0:39],
            #text=dict_elem["description"][0:59],
            text=text[0:119],
            actions=[{"type": "uri", "label": "URI", "uri": plot_response.url}]
        )
    )

    return capsules
