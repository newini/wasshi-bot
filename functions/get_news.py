#!/usr/bin/env python3
#coding:UTF-8

from linebot.models import CarouselColumn

import requests, xmltodict
from link_preview import link_preview

yahoonews_url = "https://news.yahoo.co.jp/{category}/rss.xml"
category = "pickup"

def getNews(data):
    news_url = yahoonews_url.format(category = category)
    
    response = requests.get(news_url)
    
    data_dict = xmltodict.parse(response.text)

    capsules = []
    for item in data_dict["rss"]["channel"]["item"]:
        dict_elem = link_preview.generate_dict(item["link"])
        capsules.append(
            CarouselColumn(
                thumbnail_image_url=dict_elem["image"],
                title=dict_elem["title"][0:39],
                text=dict_elem["description"][0:59],
                actions=[{"type": "uri", "label": "URI", "uri": item["link"]}]
            )
        )

    return capsules
