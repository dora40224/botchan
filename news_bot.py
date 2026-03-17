import requests
import os
from bs4 import BeautifulSoup
from linebot import LineBotApi
from linebot.models import TextSendMessage

URL = "https://www.c.u-tokyo.ac.jp/zenki/news/index.html"
BASE = "https://www.c.u-tokyo.ac.jp/zenki/news/"

CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
GROUP_ID = os.environ["LINE_GROUP_ID"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

res = requests.get(URL)
soup = BeautifulSoup(res.text, "html.parser")

items = []

# ニュース一覧取得
for dt in soup.select("dl dt"):

    dd = dt.find_next_sibling("dd")
    a = dd.find("a")

    date = dt.text.strip()
    title = a.text.strip()
    link = BASE + a["href"]

    items.append((date, title, link))

# 前回チェック
try:
    with open("latest.txt") as f:
        old = f.read().strip()
except:
    old = ""

new_articles = []

for date, title, link in items:

    key = f"{date} {title}"

    if key == old:
        break

    new_articles.append((date, title, link))

# 新着があれば通知
if new_articles:

    message = "東大教養学部ニュース更新！\n\n"

    for date, title, link in reversed(new_articles):

        message += f"{date}\n{title}\n{link}\n\n"

    line_bot_api.push_message(
        GROUP_ID,
        TextSendMessage(text=message)
    )

    # 最新記事保存
    newest = f"{items[0][0]} {items[0][1]}"

    with open("latest.txt", "w") as f:
        f.write(newest)

else:
    print("更新なし")
