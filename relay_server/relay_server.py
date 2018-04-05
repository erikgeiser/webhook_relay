from flask import Flask, request, current_app, jsonify
from flask_basicauth import BasicAuth
from configparser import ConfigParser
from collections import deque

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
    notification_buffer.append(content)
    print('%s\n' % content)
    return "ok", 200

@app.route('/fetch', methods=['GET'])
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
