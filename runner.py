from flask import Flask, make_response, json as flaskJson
import requests
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(fmt="%(asctime)s %(name)s.%(levelname)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
app.logger = logger

@app.route('/health')
def sgx_health():
    try:
        ret = _post("http://localhost:1030", '{"jsonrpc":"2.0","id":1,"method":"getServerConfiguration","params":{}}')
        app.logger.info("well monitored...")
    except Exception as e:
        app.logger.error(e)
        return make_response(flaskJson.jsonify(errorMsg=e), 400)

    return make_response(flaskJson.jsonify(**ret), 200)

class HttpError(Exception):
    def __init__(self, code=None, reason=None):
        self.code = code
        self.reason = reason

def _post(url, payload=None):
    headers = {}
    headers['Content-Type'] = 'application/json'
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    return _get_response(response)

def _get_response(response):
    if response.status_code != requests.codes.ok:
        raise HttpError(response.status_code, response.reason)
    result = response.json()

    return result

if __name__ == "__main__":
    from gevent.pywsgi import WSGIServer

    http_server = WSGIServer(('0.0.0.0', 5000), app)
    app.logger.info("Monitoring server started...")
    http_server.serve_forever()
