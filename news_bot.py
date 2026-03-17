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

# ページ取得
res = requests.get(URL)
soup = BeautifulSoup(res.text, "html.parser")

items = []

# 最新10件取得
for dt in soup.select("dl dt")[:10]:

    dd = dt.find_next_sibling("dd")
    a = dd.find("a")

    date = dt.text.strip()
    title = a.text.strip()
    link = BASE + a["href"]

    items.append((date, title, link))

# 前回記事読み込み
try:
    with open("latest.txt") as f:
        old = f.read().strip()
except:
    old = ""

# 初回実行判定
if old == "":
    newest = f"{items[0][0]} {items[0][1]}"

    with open("latest.txt", "w") as f:
        f.write(newest)

    print("初回実行：通知なし")
    exit()

# 新記事検出
new_articles = []

for date, title, link in items:

    key = f"{date} {title}"

    if key == old:
        break

    new_articles.append((date, title, link))

# 最大5件に制限
new_articles = new_articles[:5]

# 通知
if new_articles:

    message = "東大教養学部ニュース更新！\n\n"

    for date, title, link in reversed(new_articles):

        message += f"{date}\n{title}\n{link}\n\n"

    line_bot_api.push_message(
        GROUP_ID,
        TextSendMessage(text=message)
    )

    print("通知送信")

    # 最新記事保存
    newest = f"{items[0][0]} {items[0][1]}"

    with open("latest.txt", "w") as f:
        f.write(newest)

else:
    print("更新なし")
