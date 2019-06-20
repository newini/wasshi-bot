#!/usr/bin/env python3
#coding:UTF-8

import requests, xmltodict

yahoonews_url = "https://news.yahoo.co.jp/{category}/rss.xml"
category = "pickup"

def getNews(data):
    news_url = yahoonews_url.format(category = category)
    
    response = requests.get(news_url)
    
    data_dict = xmltodict.parse(response.text)

    text = ""
    for item in data_dict["rss"]["channel"]["item"]:
        text += "\n" + item["title"] + "\n" + item["link"] + " "

    return text
