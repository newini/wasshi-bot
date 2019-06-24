#!/usr/bin/env python3
#coding:UTF-8
from configs.imports import *

#---------------------------------------
# Configs
#---------------------------------------
# Variables
from configs.production import *

# Pages, fuctions route
from configs.route import *

# Python logging
# https://stackoverflow.com/questions/17743019/flask-logging-cannot-get-it-to-write-to-a-file
import logging, logging.config
logging.config.dictConfig(yaml.load(open('./configs/logging.yml')))


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


@handler.add(MessageEvent, message=TextMessage)
def response_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    reply_text = ""
    do_current_weather = False
    do_forecast_weather = False
    do_get_news = False
    message_type = 1 # 1: text, 2: image, 3: template. Default is 1

    if "天気" in event.message.text or "気温" in event.message.text:
        do_current_weather = True

    if "予報" in event.message.text:
        do_forecast_weather = True
        alt_text = "Forecast"
        message_type = 2

    if "news" in event.message.text or "ニュース" in event.message.text:
        do_get_news = True
        alt_text = "News"
        message_type = 3
        

    print(event)
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
       
        if do_forecast_weather:
            image_url = getForecastWeather(data)

        if do_get_news:
            capsules = getNews(data)

    if message_type == 1:
        # Ayamaru
        ran = random.uniform(0.0,1.0)
        if ran < ayamaru_rate:
            reply_text += "。ごめんなさい。"

        # Text message
        messages = TextSendMessage(
            text = reply_text
        )
    elif message_type == 2:
        messages = ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )
    elif message_type == 3:
        # Template message
        messages = TemplateSendMessage(
            alt_text=alt_text,
            template=CarouselTemplate(columns=capsules),
        )


    # Send
    line_bot_api.reply_message(event.reply_token, messages=messages)

    ##
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
