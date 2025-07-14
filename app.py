
from flask import Flask, request, Response
import requests

app = Flask(__name__)

@app.route('/proxy/')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "❌ Missing 'url' query parameter", 400

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
            'Referer': 'https://adtv.ae/'
        }
        resp = requests.get(target_url, headers=headers, stream=True)

        return Response(resp.iter_content(chunk_size=8192),
                        content_type=resp.headers.get('Content-Type'))
    except Exception as e:
        return f"❌ Error fetching the URL: {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
