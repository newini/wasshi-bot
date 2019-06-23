#!/usr/bin/env python3
#coding:UTF-8
from configs.imports import *

# Open Weather Map
OWM_KEY = os.environ["OWM_KEY"]
owm_forcast_url = "http://api.openweathermap.org/data/2.5/forecast?units=metric&q={city}&APPID={key}&lang=ja"
forcast_day = 1 # 1 day

# Timezone
timezone = 9
JST = datetime.timezone(datetime.timedelta(hours=timezone), 'JST')

# Use Open Weather Map API
def getForecastWeather(data):
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

    cnt = 0
    x = []
    y = []
    text = []
    for forcast_list in data["list"]:
        #if forcast_list["weather"][0]["main"].lower() == "clear":
        #    text.append(u'\U00002600')
        #elif forcast_list["weather"][0]["main"].lower() == "clouds":
        #    text.append(u'\U00002601')
        #elif forcast_list["weather"][0]["main"].lower() == "rain":
        #    text.append(u'\U0001f327')
        #else:
        #    text.append(forcast_list["weather"][0]["main"])
        text.append(forcast_list["weather"][0]["main"])
        x.append(datetime.datetime.fromtimestamp(forcast_list["dt"], JST))
        y.append(forcast_list["main"]["temp"])
        cnt += 1
        if cnt > 7*forcast_day: break
        #text += ("\n"+ datetime.datetime.fromtimestamp(forcast_list["dt"], JST).strftime('%m/%d %H:%M') + " " + str(forcast_list["main"]["temp"]) + "°C "
        #        + forcast_list["weather"][0]["main"] + ":" + forcast_list["weather"][0]["description"])

    # Plot graph in tmp directory
    wasshi_url = "https://wasshi-bot.herokuapp.com/"
    page_name = "plot_graph"
    params = {"city": city_en, "x": x, "y": y, "text": text}
    plot_response = requests.get(url = wasshi_url+page_name, params = params)

    page_name = "send_from_tmp"
    image_url = wasshi_url + page_name + "?filename=" + city_en + ".jpeg&" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    return image_url
