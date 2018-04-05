from configparser import ConfigParser
from collections import deque
from datetime import datetime

from flask import Flask, request, current_app, jsonify
from flask_basicauth import BasicAuth
import request

cfg = ConfigParser()
cfg.read('config.ini')
app = Flask(__name__)
basic_auth = BasicAuth(app)
app.config['BASIC_AUTH_USERNAME'] = cfg['auth']['username']
app.config['BASIC_AUTH_PASSWORD'] = cfg['auth']['password']
notification_buffer = deque(maxlen=int(cfg['relay']['buffersize']))

@app.route('/webhook', methods=['POST'])
def dispatch_json():
    global notification_buffer
    content = request.json
    content['time'] = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    notification_buffer.append(content)
    print('%s\n' % content)

    forward_url = cfg['relay']['forward']
    if forward_url:
        r = requests.post(forward_url, json=content)
        try:
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("[!] Webhook forward error: %s" % e)

    return "ok", 200

@app.route('/poll', methods=['GET'])
@basic_auth.required
def notify_client():
    global notification_buffer
    response = {
        'count': len(notification_buffer),
        'content': list(notification_buffer),
    }
    notification_buffer = deque()
    return jsonify(response)

if __name__ == '__main__':
    app.run(
        host=cfg['server']['host'],
        port=int(cfg['server']['port'])
    )
