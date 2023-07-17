from flask import Flask, make_response, json as flaskJson
import requests

app = Flask(__name__)

@app.route('/health')
def sgx_health():
    ret = _post("http://localhost:1030", '{"jsonrpc":"2.0","id":1,"method":"getServerConfiguration","params":{}}')
    return make_response(flaskJson.jsonify(**ret), 200)

class HttpError(Exception):
    def __init__(self, code=None, reason=None):
        self.code = code
        self.reason = reason

def _post(url, payload=None):
    headers = {}
    headers['Content-Type'] = 'application/json'
    response = requests.post(url, headers=headers, data=payload)
    return _get_response(response)

def _get_response(response):
    if response.status_code != requests.codes.ok:
        raise HttpError(response.status_code, response.reason)
    result = response.json()

    return result

if __name__ == "__main__":
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(('0.0.0.0', 5000), app)
    http_server.serve_forever()
