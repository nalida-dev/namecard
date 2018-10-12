import time
import sys
import os
import re
import threading
from flask import Flask, jsonify, request, send_file
from card import create_namecard

app = Flask(__name__)

@app.route("/keyboard", methods=["GET"])
def keyboard():
    return jsonify({
        "type": "buttons",
        "buttons": ["명함 만들어주세요.", "명함 안 만들어주세요."]
    })

@app.route("/message", methods=["POST"])
def message():
    params = request.get_json()
    if params["type"] == 'photo':
        return jsonify({
            "message": {"text": "사진 ㄴㄴ"},
            "keyboard": {"type": "text"},
        })
    if params["content"] == '명함 만들어주세요.':
        return jsonify({
            "message": {"text": "번호"},
            "keyboard": {"type": "text"},
        })
    if params["content"] == '명함 안 만들어주세요.':
        return jsonify({
            "message": {"text": "그래"},
            "keyboard": {
                "type": "buttons",
                "buttons": ["명함 만들어주세요.", "명함 안 만들어주세요."]
            }
        })

    def is_valid_number(number):
        number = number.replace(" ", "").replace("-", "")
        if len(number) != 11:
            return False
        for c in number:
            if c not in "0123456789":
                return False
        return True

    if not is_valid_number(params["content"]):
        return jsonify({
            "message": {"text": "제대로"},
            "keyboard": {"type": "text"},
        })

    filename = 'tempfiles/{user_key}_{time}.png'.format(user_key=params["user_key"], time=time.time())
    create_namecard(params["content"] ,'C', '최길웅', '꾼', '안녕하세요', 220, 63, 144, filename)

    return jsonify({
        "message": {
            "text": "여기",
            "photo": {
                "url": "http://13.124.13.85/photo?filename={filename}".format(filename=filename),
                "width": 588,
                "height": 976
            }
        },
        "keyboard": {
            "type": "buttons",
            "buttons": ["명함 만들어주세요.", "명함 안 만들어주세요."]
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
