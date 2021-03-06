#!/usr/bin/env python3
# -*- coding: utf-8 -*

# ---------------------------------------
# Configs
# ---------------------------------------
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
chart_studio.tools.set_credentials_file(
    username=PLOTLY_USERNAME, api_key=PLOTLY_API_KEY
)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(MessageEvent)
def response_message(event):
    if event.reply_token == "00000000000000000000000000000000":
        return
    reply_text = ""
    message_type = 6  # 1: text, 2: image, 6: sticker, 10: template. Default is 6
    global nobyapi_persona

    # Seperate event treat by message type
    if event.message.type == "text":
        do_current_weather = False
        do_forecast_weather = False
        do_get_news = False
        # do_special_event = False
        do_takoyaki = False
        do_setting = False
        do_setting_reply = False
        message_type = 1
        location = ""

        # Through Noby API to get word list
        # Noby api
        noby_params = {
            "appkey": NOBYAPI_KEY,
            "text": event.message.text,
            "persona": nobyapi_persona,
        }
        noby_p = urllib.parse.urlencode(noby_params)
        noby_url = nobyapi_url + noby_p
        noby_response = urllib.request.urlopen(noby_url)
        noby_html = noby_response.read().decode("utf-8")
        noby_data = json.loads(noby_html)
        reply_text = noby_data["text"]

        for word in noby_data["wordList"]:
            if "地域" in word["feature"]:
                if location == "":
                    location = word["surface"]

            if "テンキ" in word["feature"] in word["feature"]:
                do_current_weather = True

            if "ヨホウ" in word["feature"]:
                do_forecast_weather = True
                alt_text = "Forecast"
                message_type = 2

            if "news" in word["feature"] or "ニュース" in word["feature"]:
                do_get_news = True
                alt_text = "News"
                message_type = 10

            # if "参加" in word["feature"] or "次会" in word["feature"]:
            #    do_special_event = True

            if "タコヤキ" in word["feature"]:
                do_takoyaki = True

            if "性格" in word["feature"]:
                do_setting = True
            if do_setting and "数" in word["feature"]:
                if 0 <= int(word["surface"]) and int(word["surface"]) <= 3:
                    nobyapi_persona = int(word["surface"])
            if do_setting and "教える" in word["feature"]:
                do_setting_reply = True

        if location == "":
            text_temp = event.message.text
            if "予報" in text_temp:
                location = text_temp.split("予報")[0]
            if "天気" in text_temp:
                location = text_temp.split("天気")[0]

        if do_current_weather:
            reply_text = getCurrentWeather(location)

        if do_forecast_weather:
            image_url = getForecastWeather(location)

        if do_get_news:
            capsules = getNews(noby_data)

        if do_setting_reply:
            reply_text = (
                "今のわっしーbotの性格は: "
                + str(nobyapi_persona)
                + "(# 0: normal, 1: tsundere-onna, 2: tsundere-otoko, 3: kami)"
            )

    # Create message
    if message_type == 1:  # Text message
        # if do_special_event:
        #    reply_text = "ご参加連絡ありがとうございます。担当者に繋ぎします。"

        if do_takoyaki:
            reply_text = "たこたこ！"

        # Ayamaru
        ran = random.uniform(0.0, 1.0)
        if ran < ayamaru_rate:
            reply_text += "。ごめんなさい。"

        messages = TextSendMessage(text=reply_text)
    elif message_type == 2:
        messages = ImageSendMessage(
            original_content_url=image_url, preview_image_url=image_url
        )
    elif message_type == 6:
        sticker_id = random.randint(1, 10)
        messages = StickerSendMessage(package_id="1", sticker_id=sticker_id)
    elif message_type == 10:  # Template message
        messages = TemplateSendMessage(
            alt_text=alt_text, template=CarouselTemplate(columns=capsules),
        )
    # Reply
    line_bot_api.reply_message(event.reply_token, messages=messages)

    ##
    # Sent info to developer
    headers = {"Authorization": "Bearer " + LINENOTIFY_TOKEN}

    profile = line_bot_api.get_profile(event.source.user_id)
    notify_text = (
        "\n"
        + "From: "
        + profile.display_name
        + "\n"
        + "userId: "
        + profile.user_id
        + "\n"
        + "message.type: "
        + event.message.type
        + "\n"
    )
    if event.message.type == "text":
        notify_text += "message: " + event.message.text + "\n" + "reply: " + reply_text
    payload = {"message": notify_text}

    # files = {"imageFile": open("test.jpg", "rb")} #バイナリで画像ファイルを開きます。対応している形式はPNG/JPEGです。
    # r = requests.post(url ,headers = headers ,params=payload, files=files)
    requests.post(linenotify_url, headers=headers, params=payload)

    ##
    # Sent special event message
    # if do_special_event:
    #    to = "U605ca892d67386c5139104d617ffb3e8" # Oku
    #    text = ("飲み会参加希望の方より連絡がありました。\n"
    #            + "From: " + profile.display_name + "\n"
    #            + "message: " + event.message.text)
    #    line_bot_api.push_message(to, TextSendMessage(text=text))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
