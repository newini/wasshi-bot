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
nobyapi_persona = 0 # 0: normal, 1: tsundere-onna, 2: tsundere-otoko, 3: kami

# Wasshi value
ayamaru_rate = 0.8


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

    messages = TextSendMessage()

    #response = client.talk(event.message.text)
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
 
        messages = TextSendMessage(
            text=data["text"]
        )
    line_bot_api.reply_message(event.reply_token, messages=messages)

    # Ayamaru
    ran = random.uniform(0.0,1.0)
    if ran < ayamaru_rate:
        messages = TextSendMessage(
            text="ごめんなさい。"
        )
        line_bot_api.reply_message(event.reply_token, messages=messages)

    # Sent info to developer
    profile = line_bot_api.get_profile(event.source.user_id)
    messages = TextSendMessage(
        text="Text from: " + profile.display_name + ", userId: " + profile.user_id + ", pic: " + profile.picture_url + ". message: " + event.message.text
    )
    to = 'U85814e91847a0e3b73886a44cc1d181f'
    line_bot_api.push_message(to, messages)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
