import os, json, random

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

app = Flask(__name__)

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
LINENOTIFY_TOKEN = os.eviron["LINENOTIFY_TOKEN"]
linenotify_url = "https://notify-api.line.me/api/notify"

# Wasshi value
ayamaru_rate = 0.5


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

    text = ""

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
        text = text=data["text"]

    # Ayamaru
    ran = random.uniform(0.0,1.0)
    if ran < ayamaru_rate:
        text += "。ごめんなさい。"

    # Reply
    messages = TextSendMessage(
        text=text
    )
    line_bot_api.reply_message(event.reply_token, messages=messages)

    # Sent info to developer
    headers = {"Authorization" : "Bearer "+ LINENOTIFY_TOKEN}

    profile = line_bot_api.get_profile(event.source.user_id)
    text = "From: " + profile.display_name + "\n"
            + "userId: " + profile.user_id + "\n"
            + "message: " + event.message.text
    payload = {"message" :  message}

    #files = {"imageFile": open("test.jpg", "rb")} #バイナリで画像ファイルを開きます。対応している形式はPNG/JPEGです。
    #r = requests.post(url ,headers = headers ,params=payload, files=files)
    requests.post(linenotify_url, headers = headers, params=payload)



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
