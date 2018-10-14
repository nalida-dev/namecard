import time
import sys
import os
import re
import threading

from color_dic import color_dic
from database_wrapper_redis import DatabaseWrapperRedis
from send_mail import send_namecard

from flask import Flask, jsonify, request, send_file
from card import create_namecard

app = Flask(__name__)
db = DatabaseWrapperRedis(host='localhost', port=6380, db=0, namespace="namecard")

@app.route("/keyboard", methods=["GET"])
def keyboard():
    return jsonify({
        "type": "buttons",
        "buttons": ["명함 만들어주세요."]
    })

def getset(user_key, key, value=None):
    if value is None:
        v = db.get("{user_key}:{key}".format(user_key=user_key, key=key))
        return '' if v is None else v
    else:
        db.set("{user_key}:{key}".format(user_key=user_key, key=key), value)

def user_state(user_key, value=None):
    return getset(user_key, 'userstate', value)

def is_valid_number(number):
    number = number.replace(" ", "").replace("-", "")
    if len(number) != 11:
        return False
    for c in number:
        if c not in "0123456789":
            return False
    return True

def free_text(text):
    return jsonify({
        "message": {"text": text},
        "keyboard": {"type": "text"},
    })


@app.route("/message", methods=["POST"])
def message():
    params = request.get_json()
    if params["type"] == 'photo':
        return free_text("사진 업로드는 지원되지 않습니다.")
    user_key = params["user_key"]
    content = params["content"]
    state = user_state(user_key)
    if state == '':
        user_state(user_key, 'asked_number')
        return free_text("번호")

    if state == 'asked_number':
        if not is_valid_number(content):
            return free_text("제대로")
        getset(user_key, 'number', content)
        user_state(user_key, 'asked_name')
        return free_text("이름 (8자 이내)")

    if state == 'asked_name':
        if len(content) > 8:
            return free_text("8자 이내")
        getset(user_key, 'name', content)
        user_state(user_key, 'asked_initial')
        return free_text("이니셜 (영문 1자)")

    if state == 'asked_initial':
        if len(content) != 1:
            return free_text("1자")
        getset(user_key, 'initial', content)
        user_state(user_key, 'asked_nick')
        return free_text("별명 (8자 이내)")

    if state == 'asked_nick':
        if len(content) > 8:
            return free_text("8자 이내")
        getset(user_key, 'nick', content)
        user_state(user_key, 'asked_intro')
        return free_text("한줄 자기소개 (40자 이내)")

    if state == 'asked_intro':
        if len(content) > 40:
            return free_text("40자 이내")
        getset(user_key, 'intro', content)
        user_state(user_key, 'asked_color')
        return jsonify({
            "message": {
                "text": "색깔 (1-18)",
                "photo": {
                    "url": "http://13.124.13.85/photo?filename={filename}".format(filename='pallete.png'),
                    "width": 1148,
                    "height": 610
                }
            },
            "keyboard": {
                "type": "text"
            }
        })

    if state == 'asked_color':
        try:
            print(content)
            r, g, b = color_dic[content]
            getset(user_key, 'color-r', r) 
            getset(user_key, 'color-g', g) 
            getset(user_key, 'color-b', b) 
        except Exception:
            return free_text("제대로")

        number = getset(user_key, 'number')
        initial = getset(user_key, 'initial')
        name = getset(user_key, 'name')
        nick = getset(user_key, 'nick')
        intro = getset(user_key, 'intro')
        color_r = getset(user_key, 'color-r')
        color_g = getset(user_key, 'color-g')
        color_b = getset(user_key, 'color-b')
            
        filename = 'tempfiles/{user_key}_{time}.png'.format(user_key=params["user_key"], time=time.time())
        getset(user_key, 'filename', filename)

        create_namecard(number, initial, name, nick, intro, color_r, color_g, color_b, filename)

        user_state(user_key, 'asked_to_confirm')

        return jsonify({
            "message": {
                "text": "여기",
                "photo": {
                    "url": "http://13.124.13.85/photo?filename={filename}".format(filename=filename),
                    "width": 589,
                    "height": 975
                }
            },
            "keyboard": {
                "type": "buttons",
                "buttons": ["메일로 보내주세요!", "다시 만들어 주세요."]
            }
        })

    if state == 'asked_to_confirm':
        if content == '메일로 보내주세요!':
            user_state(user_key, 'asked_email')
            return free_text('메일')
        else:
            user_state(user_key, 'asked_number')
            return free_text("번호")
    
    if state == 'asked_email':
        filename = getset(user_key, 'filename')
        try:
            threading.Thread(target=send_namecard, args=(content, filename), daemon=True).start()
            msg = '보냈음'
        except Exception:
            msg = '파일 유효기간이 만료되었거나 메일 주소에 문제가 있는 모양입니다. 다시 진행해주세요.'

        user_state(user_key, '')

        return jsonify({
            "message": {
                "text": msg,
            },
            "keyboard": {
                "type": "buttons",
                "buttons": ["명함 만들어주세요."]
            }
        })

@app.route("/photo", methods=["GET"])
def photo():
    filename = request.args.get("filename")
    try:
        return send_file(filename, mimetype='image/png')
    except FileNotFoundError as e:
        return send_file('expired.png', mimetype='image/png')

@app.route("/")
def root():
    return "Hello"

if 'tempfiles' not in os.listdir():
    os.mkdir('tempfiles')

def auto_delete():
    threshold = 60 # in seconds
    pat = re.compile("^([a-zA-Z0-9]+)_([0-9.]+)\.png")
    while True:
        for filename in os.listdir('tempfiles'):
            m = pat.match(filename)
            if m is None:
                continue
            user_key, then = m.group(1), float(m.group(2))
            now = time.time()
            if now - then > threshold:
                os.remove('tempfiles/' + filename)
                print("[auto_delete] deleted {filename}".format(filename=filename))
        time.sleep(threshold)
threading.Thread(target=auto_delete, args=(), daemon=True).start()

app.run(host=sys.argv[1], port=sys.argv[2])
