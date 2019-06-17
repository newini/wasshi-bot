#!/usr/bin/env python3
#coding:UTF-8
import os, json, random, requests, datetime

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn,
    TextSendMessage # text message
)

# CURL
import urllib.request, urllib.parse

# Translate
from googletrans import Translator

# Line messange api
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Talk api
NOBYAPI_KEY = os.environ["NOBYAPI_KEY"]
nobyapi_url = "https://www.cotogoto.ai/webapi/noby.json?"
nobyapi_persona = 1 # 0: normal, 1: tsundere-onna, 2: tsundere-otoko, 3: kami

# Line notify
LINENOTIFY_TOKEN = os.environ["LINENOTIFY_TOKEN"]
linenotify_url = "https://notify-api.line.me/api/notify"

# Open Weather Map
OWM_KEY = os.environ["OWM_KEY"]
owm_current_url = "http://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&APPID={key}&lang=ja"
owm_forcast_url = "http://api.openweathermap.org/data/2.5/forecast?units=metric&q={city}&APPID={key}&lang=ja"
forcast_day = 1 # 1 day

# Timezone
timezone = 9
JST = datetime.timezone(datetime.timedelta(hours=timezone), 'JST')

# Wasshi value
ayamaru_rate = 0.5


##########################################################################
#                               Main Body
##########################################################################
# App
app = Flask(__name__)

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

    text = city_jp + " is " + data["weather"][0]["main"] + ":" + data["weather"][0]["description"] + " and " + str(data["main"]["temp"]) + "°C " + str(data["main"]["humidity"]) + "% Now.\n"
    text += "Max: " + str(data["main"]["temp_max"]) + "°C, min: " + str(data["main"]["temp_min"]) + "°C"

    return text

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


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def response_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    reply_text = ""
    do_current_weather = False
    do_forcast_weather = False

    if "天気" in event.message.text or "気温" in event.message.text:
        do_current_weather = True

    if do_current_weather and "予報" in event.message.text:
        do_forcast_weather = True
        
    # Noby api
    params = {
        "appkey": NOBYAPI_KEY,
        "text": event.message.text,
        "persona": nobyapi_persona,
    }
    p = urllib.parse.urlencode(params)
    url = nobyapi_url + p
    with urllib.request.urlopen(url) as res:
        html = res.read().decode("utf-8")
        #print(html)
        data = json.loads(html)
        reply_text = data["text"]

        if do_current_weather:
            reply_text = getCurrentWeather(data)
       
        if do_forcast_weather:
            reply_text += getForcastWeather(data)

    # Ayamaru
    ran = random.uniform(0.0,1.0)
    if ran < ayamaru_rate:
        reply_text += "。ごめんなさい。"

    # Reply
    messages = TextSendMessage(
        text = reply_text
    )
    line_bot_api.reply_message(event.reply_token, messages=messages)

    # Sent info to developer
    headers = {"Authorization" : "Bearer "+ LINENOTIFY_TOKEN}

    profile = line_bot_api.get_profile(event.source.user_id)
    notify_text = ("\n"
            + "From: " + profile.display_name + "\n"
            + "userId: " + profile.user_id + "\n"
            + "message: " + event.message.text + "\n"
            + "reply: " + reply_text)
    payload = {"message" :  notify_text}

    #files = {"imageFile": open("test.jpg", "rb")} #バイナリで画像ファイルを開きます。対応している形式はPNG/JPEGです。
    #r = requests.post(url ,headers = headers ,params=payload, files=files)
    requests.post(linenotify_url, headers = headers, params=payload)



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
