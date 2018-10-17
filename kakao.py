import time
import sys
import os
import re
import threading
import random

import requests

from color_dic import color_dic
from database_wrapper_redis import DatabaseWrapperRedis
from send_mail import send_namecard, send_auth

from flask import Flask, jsonify, request, send_file
from card import create_namecard
from credentials import api_base, monitoring_room_id

import string_resources as sr

app = Flask(__name__)
db = DatabaseWrapperRedis(host='localhost', port=6380, db=0, namespace="namecard")

pat_alphabet = re.compile('^[a-zA-Z ]*$')
pat_number = re.compile('^[0-9]*$')

def report(text):
    t = threading.Thread(target = requests.post,
        args = (api_base + 'sendMessage', ),
        kwargs = {
            'data': {
                "chat_id" : monitoring_room_id,
                "text" : text
                }
            }
        )
    t.setDaemon(True)
    t.start()

def getset(user_key, key, value=None):
    if value is None:
        v = db.get("{user_key}:{key}".format(user_key=user_key, key=key))
        return '' if v is None else v
    else:
        db.set("{user_key}:{key}".format(user_key=user_key, key=key), value)

def user_state(user_key, value=None):
    return getset(user_key, 'userstate', value)

def to_valid_number(number):
    number = number.replace(" ", "").replace("-", "")
    if len(number) <= 9 or 12 <= len(number):
        return None
    if pat_number.match(number) is None:
        return None
    if len(number) == 10:
        number = number[:6] + ' ' + number[6:]
    return number

@app.route("/keyboard", methods=["GET"])
def keyboard():
    return jsonify({
        "type": "buttons",
        "buttons": ["명함 만들어주세요."]
    })

def send_msg(text, photo=None, buttons=None):
    ret = {
        "message": {"text": text},
        "keyboard": {"type": "text"} if buttons is None else {"type": "buttons", "buttons": buttons}
    }
    if photo is not None:
        ret["message"]["photo"] = photo

    return jsonify(ret)
    
@app.route("/message", methods=["POST"])
def message():
    params = request.get_json()
    if params["type"] == 'photo':
        return send_msg(sr.PHOTO_NONO)
    user_key = params["user_key"]
    content = params["content"]
    state = user_state(user_key)
    if state == '':
        user_state(user_key, 'greetings')
        return send_msg(sr.HELLO, buttons=["반가워!"])
    
    if state == 'greetings':
        user_state(user_key, 'pro_namecarder')
        return send_msg(sr.I_AM_PRO_NAMECARDER,
            buttons=["그렇구나! 명함 어서 만들어 줘!"])
    
    if state == 'pro_namecarder':
        user_state(user_key, 'asked_tmi')
        return send_msg(sr.DO_YOU_WANT_NALIDA_DETAIL,
                buttons=["네!", "아니요!"])

    if state == 'asked_tmi':
        user_state(user_key, 'tmi_done')
        if content == '네!':
            return send_msg(sr.NALIDA_TMI,
                buttons=["고마워! 그래서 명함은 언제 주는 거야?"])
        elif content == '아니요!':
            return send_msg(sr.OKAY_BYE,
                buttons=["고마워! 그래서 명함은 언제 주는 거야?"])
        else:
            return send_msg(sr.NALIDA_TMI,
                buttons=["고마워! 그래서 명함은 언제 주는 거야?"])

    if state == 'tmi_done':
        user_state(user_key, 'asked_personal_okay')
        return send_msg(sr.PERSONAL_INFO_OKAY,
                buttons=["응!"])

    if state == 'asked_personal_okay':
        user_state(user_key, 'asked_if_agree')
        return send_msg(sr.AGREE_STATEMENT)

    if state == 'asked_if_agree':
        if content.strip() == '1':
            user_state(user_key, 'asked_name')
            return send_msg(sr.ASK_NAME)
        elif content.strip() == '2':
            user_state(user_key, '')
            return send_msg(sr.OKAY_BYE_2)
        else:
            return send_msg(sr.WRONG_RESPONSE)

    if state == 'asked_name':
        if len(content) > 8:
            return send_msg("8자 이내의 한글, 영문, 숫자로 입력해주세요.")
        getset(user_key, 'name', content)
        user_state(user_key, 'asked_nick')
        return send_msg(sr.ASK_NICK)

    if state == 'asked_nick':
        if len(content) > 8:
            return send_msg("띄어쓰기 포함 8자 이내의 한글, 영문, 숫자로 입력해주세요.")
        if content.strip() == '없음':
            getset(user_key, 'nick', '')
            user_state(user_key, 'asked_initial')
            return send_msg(sr.ASK_INITIAL_NO_NICK)
        else:
            getset(user_key, 'nick', content)
            user_state(user_key, 'asked_initial')
            return send_msg(sr.ASK_INITIAL)

    if state == 'asked_initial':
        if len(content) != 1 or pat_alphabet.match(content) is None:
            return send_msg("1글자의 영문 알파벳만 입력해주세요.")
        getset(user_key, 'initial', content.upper())
        user_state(user_key, 'asked_number')
        return send_msg(sr.ASK_NUMBER)

    if state == 'asked_number':
        content = to_valid_number(content)
        if content is None:
            return send_msg("전화번호를 올바르게 입력해주세요")
        getset(user_key, 'number', content)
        user_state(user_key, 'asked_intro')
        return send_msg(sr.ASK_INTRO)

    if state == 'asked_intro':
        if len(content) > 40:
            return send_msg("40자 이내로 입력해주세요.")
        getset(user_key, 'intro', content.replace('\n', ' '))
        user_state(user_key, 'asked_color')
        photo = {
            "url": "http://13.124.13.85/photo?filename={filename}".format(filename='pallete.png'),
            "width": 1148,
            "height": 610
        }
        return send_msg(sr.ASK_COLOR, photo)

    if state == 'asked_color':
        try:
            print(content)
            r, g, b = color_dic[content]
            getset(user_key, 'color-r', r) 
            getset(user_key, 'color-g', g) 
            getset(user_key, 'color-b', b) 
        except Exception:
            return send_msg("1부터 18 사이의 번호로 골라주세요.")

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
        photo = {
            "url": "http://13.124.13.85/photo?filename={filename}".format(filename=filename),
            "width": 589,
            "height": 975
        }
        report("{user_key}/{name}/{nick}/{initial}/{intro}/({r},{g},{b})".format(
            user_key=user_key, name=name, nick=nick, initial=initial, intro=intro, r=color_r, g=color_g, b=color_b))
        return send_msg(sr.HAO_MA, photo, ["응!", "아니 괜찮아!"])

    if state == 'asked_to_confirm':
        if content == '응!':
            user_state(user_key, 'asked_email')
            return send_msg(sr.EMAIL_PLEASE)
        else:
            user_state(user_key, '')
            return send_msg(sr.OKAY_BYE_2)
    
    if state == 'asked_email':
        user_state(user_key, 'asked_auth')
        auth_key = "%06d" % random.randint(0, 999999)
        getset(user_key, 'email', content)
        getset(user_key, 'auth_key', auth_key)
        threading.Thread(target=send_auth, args=(content, auth_key), daemon=True).start()
        return send_msg(sr.AUTH_PLEASE)

    if state == 'asked_auth':
        auth_key = getset(user_key, 'auth_key')
        if content.strip() == auth_key:
            filename = getset(user_key, 'filename')
            email = getset(user_key, 'email')
            try:
                threading.Thread(target=send_namecard, args=(email, filename), daemon=True).start()
                msg = sr.CHECK_YOUR_MAIL
            except Exception:
                msg = '파일 유효기간이 만료되었거나 메일 주소에 문제가 있는 것 같아요. 처음부터 다시 진행해주세요 ㅠㅠ'
        else:
            msg = '인증코드가 잘못되었습니다. 처음부터 다시 진행해주세요 ㅠㅠ'

        user_state(user_key, '')
        return send_msg(msg, buttons=["명함 만들어주세요."])

    # This code shouldn't be reached in normal cases
    user_state(user_key, 'greetings')
    return send_msg(sr.HELLO, buttons=["반가워!"])

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
    period = 600 # in seconds
    pat = re.compile("^([a-zA-Z0-9]+)_([0-9.]+)\.png")

    while True:
        filenames = sorted([(-float(pat.match(filename).group(2)), filename) for filename in os.listdir('tempfiles') if pat.match(filename) is not None])
        while len(filenames) > 1000:
            filename = filenames.pop()[1]
            os.remove('tempfiles/' + filename)
            print("[auto_delete] deleted {filename}".format(filename=filename))
        time.sleep(period)
threading.Thread(target=auto_delete, args=(), daemon=True).start()

app.run(host=sys.argv[1], port=sys.argv[2])
