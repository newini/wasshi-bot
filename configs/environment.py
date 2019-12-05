import os

# Line messange api
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

# Talk api
NOBYAPI_KEY = os.environ["NOBYAPI_KEY"]
nobyapi_url = "https://www.cotogoto.ai/webapi/noby.json?"
nobyapi_persona = 3 # 0: normal, 1: tsundere-onna, 2: tsundere-otoko, 3: kami

# Line notify
LINENOTIFY_TOKEN = os.environ["LINENOTIFY_TOKEN"]
linenotify_url = "https://notify-api.line.me/api/notify"

# Wasshi value
ayamaru_rate = 0.5

# Plotly
PLOTLY_USERNAME = os.environ["PLOTLY_USERNAME"]
PLOTLY_API_KEY = os.environ["PLOTLY_API_KEY"]

# Open Weather Map
OWM_KEY = os.environ["OWM_KEY"]
owm_current_url = "http://api.openweathermap.org/data/2.5/weather?units=metric&q={city}&APPID={key}&lang=ja"
owm_forcast_url = "http://api.openweathermap.org/data/2.5/forecast?units=metric&q={city}&APPID={key}&lang=ja"
forcast_day = 1 # 1 day
