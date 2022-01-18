from __future__ import unicode_literals
import os
import requests
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import face_recognition
import gspread # google api

import configparser

# import random

app = Flask(__name__)

# LINE 聊天機器人的基本資料
config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line_bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line_bot', 'channel_secret'))

# connect to google sheet api service
gc = gspread.service_account(filename='./iotelevator-777800473560.json')
sh = gc.open("智慧電梯管理系統") # google sheet name
worksheet = sh.worksheet("工作表1")

# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        print(body, signature)
        handler.handle(body, signature)

    except InvalidSignatureError:
        abort(400)

    return 'OK'



@handler.add(MessageEvent, message=TextMessage)
def get_number_of_person_in_elevator(event):
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":

        if event.message.text.find("人數") >= 0:

            # message = ImageSendMessage(
            #     original_content_url=str(sh.sheet1.acell('A1').value),
            #     preview_image_url=str(sh.sheet1.acell('A1').value)
            # )
            # url_img = str(sh.sheet1.acell('A1').value) # get url from sheet
            os.makedirs('./img/', exist_ok=True)  # create file to save image

            # download the image
            url = sh.sheet1.acell('A1').value
            r = requests.get(str(url))
            with open('./img/img.png', 'wb') as f:
                f.write(r.content)

            # load image
            image = face_recognition.load_image_file('./img/img.png')
            # image = face_recognition.load_image_file("img/222.jpg")

            face_locations = face_recognition.face_locations(image)
            print("face location: ", face_locations)

            # count = random.randrange(10)
            # bot_text = "目前電梯人數 (隨機) " + str(count) + " 人\n其實是 " + str(len(face_locations)) + " 人"
            if len(face_locations) >= 3:
                bot_text = "目前電梯人數 " + str(len(face_locations)) + " 人  \n目前電梯已額滿，請等待下一班電梯 \n圖片網址: " + str(sh.sheet1.acell('A1').value)
            else:
                bot_text = "目前電梯人數 " + str(len(face_locations)) + " 人  \n圖片網址: " + str(sh.sheet1.acell('A1').value)
        else:
            bot_text = "請輸入含有'人數'的句子!!!"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=bot_text)
        )
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     message
        # )

if __name__ == "__main__":
    app.run(host="0.0.0.0")