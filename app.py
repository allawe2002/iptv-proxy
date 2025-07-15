from flask import Flask, request, Response
import requests
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

@app.route('/proxy/')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "❌ Missing 'url' query parameter", 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
        'Referer': 'https://adtv.ae/'
    }

    try:
        resp = requests.get(target_url, headers=headers, stream=True)
        content_type = resp.headers.get('Content-Type', '')

        if 'application/vnd.apple.mpegurl' in content_type or '.m3u8' in target_url:
            original_content = resp.text
            base_url = target_url.rsplit('/', 1)[0] + '/'

            def rewrite_line(line):
                if line.strip().startswith('#') or line.strip() == '':
                    return line + '\n'
                absolute_url = urljoin(base_url, line.strip())
                proxied_url = f"/proxy/?{urlencode({'url': absolute_url})}"
                return proxied_url + '\n'

            rewritten_content = ''.join(rewrite_line(line) for line in original_content.splitlines())
            return Response(rewritten_content, content_type=content_type)

        return Response(resp.iter_content(chunk_size=8192),
                        content_type=content_type)
    except Exception as e:
        return f"❌ Error fetching the URL: {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
