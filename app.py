
from flask import Flask, request, Response, send_file
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <h1>Welcome to <span style="color:blue">TwinStreamTV</span> Proxy</h1>
        <img src="/logo" alt="TwinStreamTV Logo" width="300"/>
        <p>Enjoy seamless streaming through our proxy service.</p>
    '''

@app.route('/proxy/')
def proxy():
    url = request.args.get('url')
    if not url:
        return 'Missing url parameter', 400

    try:
        resp = requests.get(url, stream=True)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(resp.iter_content(chunk_size=8192), headers=headers, status=resp.status_code)
    except Exception as e:
        return f'Error fetching URL: {str(e)}', 500

@app.route('/logo')
def logo():
    return send_file('TwinStream_logo.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
