#-----------------------------------------
# Default modules
#-----------------------------------------
import os, json, random, requests, datetime
import urllib.request, urllib.parse         # CURL


#-----------------------------------------
# Installed modules
#-----------------------------------------
# Flask
from flask import Flask, Blueprint, request, render_template

# Line
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

# Plotly
import plotly

# Translate
from googletrans import Translator

# XML to Dictionary for python
import xmltodict

# Link preview
from link_preview import link_preview
