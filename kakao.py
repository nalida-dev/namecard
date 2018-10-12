import time
import sys
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


    filename = '{user_key}_{time}.png'.format(user_key=params["user_key"], time=time.time())
    create_namecard(params["content"] ,'C', '최길웅', '꾼', '안녕하세요', 120, 120, 120, filename)

    return jsonify({
        "message": {
            "text": "여기",
            "photo": {
                "url": "http://13.124.13.85/photo?filename={filename}".format(filename=filename),
                "width": 480,
                "height": 640
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
    return send_file(filename, mimetype='image/png')

@app.route("/")
def root():
    return "Hello"

app.run(host=sys.argv[1], port=sys.argv[2])
