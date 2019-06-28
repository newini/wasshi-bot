#!/usr/bin/env python3
# -*- coding: utf-8 -*

#---------------------------------------
# Configs
#---------------------------------------
from configs.production import *


##########################################################################
#                               Main Body
##########################################################################
# App
app = Flask(__name__)

# Regist Blue-Prints
app.register_blueprint(plot_graph_api)
app.register_blueprint(send_from_tmp_api)

# Line
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Plotly authentication
plotly.tools.set_credentials_file(username=PLOTLY_USERNAME, api_key=PLOTLY_API_KEY)


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


@handler.add(MessageEvent)
def response_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    reply_text = ""
    message_type = 6 # 1: text, 2: image, 6: sticker, 10: template. Default is 6

    # Seperate event treat by message type
    if event.message.type == "text":
        do_current_weather = False
        do_forecast_weather = False
        do_get_news = False
        do_get_time = False
        message_type = 1

        if "天気" in event.message.text or "気温" in event.message.text:
            do_current_weather = True

        if "時間" in event.message.text:
            do_get_time = True

        if "予報" in event.message.text:
            do_forecast_weather = True
            alt_text = "Forecast"
            message_type = 2

        if "news" in event.message.text or "ニュース" in event.message.text:
            do_get_news = True
            alt_text = "News"
            message_type = 10

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
            data = json.loads(html)
            reply_text = data["text"]

            if do_current_weather:
                reply_text = getCurrentWeather(data)
           
            if do_forecast_weather:
                image_url = getForecastWeather(data)

            if do_get_news:
                capsules = getNews(data)

    # Create message
    if message_type == 1: # Text message
        # Ayamaru
        ran = random.uniform(0.0, 1.0)
        if ran < ayamaru_rate:
            reply_text += "。ごめんなさい。"

        messages = TextSendMessage(
            text = reply_text
        )
    elif message_type == 2:
        messages = ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )
    elif message_type == 6:
        sticker_id = random.randint(1, 10)
        messages = StickerSendMessage(
            package_id='1',
            sticker_id=sticker_id
            )
    elif message_type == 10: # Template message
        messages = TemplateSendMessage(
            alt_text=alt_text,
            template=CarouselTemplate(columns=capsules),
        )

    print(messages)
    # Reply
    line_bot_api.reply_message(event.reply_token, messages=messages)


    ##
    # Sent info to developer
    headers = {"Authorization" : "Bearer "+ LINENOTIFY_TOKEN}

    profile = line_bot_api.get_profile(event.source.user_id)
    notify_text = ("\n"
            + "From: " + profile.display_name + "\n"
            + "userId: " + profile.user_id + "\n"
            + "message.type: " + event.message.type + "\n")
    if event.message.type == "text":
        notify_text += ("message: " + event.message.text + "\n"
            + "reply: " + reply_text)
    payload = {"message" :  notify_text}

    #files = {"imageFile": open("test.jpg", "rb")} #バイナリで画像ファイルを開きます。対応している形式はPNG/JPEGです。
    #r = requests.post(url ,headers = headers ,params=payload, files=files)
    requests.post(linenotify_url, headers = headers, params=payload)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
