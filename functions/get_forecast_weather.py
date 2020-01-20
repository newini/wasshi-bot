#!/usr/bin/env python3
#coding:UTF-8
from configs.production import *

# Timezone
timezone = 9
JST = datetime.timezone(datetime.timedelta(hours=timezone), 'JST')

# Use Open Weather Map API
def getForecastWeather(city_jp):
    if city_jp == "":
        shutil.copyfile("assets/images/city_not_found.jpg", "tmp/city_not_found.jpg")
        return "https://wasshi-bot.herokuapp.com/send_from_tmp?filename=city_not_found.jpg"

    translator = Translator()
    city_en = translator.translate(city_jp).text

    url = owm_forcast_url.format(city = city_en, key = OWM_KEY)
    response = requests.get(url)
    data = response.json()

    # If city not found in OWM
    if "cod" in data and data["cod"] == "404":
        shutil.copyfile("assets/images/city_not_found_owm.jpg", "tmp/city_not_found_owm.jpg")
        return "https://wasshi-bot.herokuapp.com/send_from_tmp?filename=city_not_found_owm.jpg"

    # Time
    timezone = data["city"]["timezone"] # shift second

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
        x.append(datetime.datetime.fromtimestamp(forcast_list["dt"]+timezone))
        y.append(forcast_list["main"]["temp"])
        cnt += 1
        if cnt > 7*forcast_day: break

    # Add city and contry into text
    text[0] = city + '<br>' + data['sys']['country'] + "<br>" + text[0]

    # Plot graph in tmp directory
    wasshi_url = "https://wasshi-bot.herokuapp.com/"
    page_name = "plot_graph"
    params = {"city": city_en, "x": x, "y": y, "text": text}
    plot_response = requests.get(url = wasshi_url+page_name, params = params)

    page_name = "send_from_tmp"
    image_url = wasshi_url + page_name + "?filename=" + city_en + ".jpeg&" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    return image_url
