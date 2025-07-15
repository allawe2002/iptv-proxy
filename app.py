
from flask import Flask, request, Response, send_file
import requests
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

PASSCODE = "372420"

login_form = '''
    <h2>🔒 Protected Page</h2>
    <form method="post">
        <input type="password" name="passcode" placeholder="Enter Passcode"/>
        <input type="submit" value="Access"/>
    </form>
'''

hls_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>TwinStreamTV Proxy</title>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background-color: #f0f0f0; }
        .logo { margin: 20px; }
        .title { color: #007BFF; }
        .description { font-size: 18px; margin-bottom: 20px; }
        .player-container { margin: 20px auto; width: 640px; }
        .stop-btn { margin-top: 5px; }
    </style>
</head>
<body>
    <h1 class="title">Welcome to TwinStreamTV Proxy</h1>
    <img class="logo" src="/logo" alt="TwinStreamTV Logo" width="200"/>
    <p class="description">Enjoy seamless streaming through our proxy service.</p>

    <h3>Live Oman TV:</h3>
    <div class="player-container">
        <video id="player1" width="640" height="360" controls></video>
        <br/>
        <button class="stop-btn" onclick="stopPlayer('player1')">Stop</button>
    </div>

    <h3>Sample Channel 2:</h3>
    <div class="player-container">
        <video id="player2" width="640" height="360" controls></video>
        <br/>
        <button class="stop-btn" onclick="stopPlayer('player2')">Stop</button>
    </div>

    <h3>Al Jazeera Live:</h3>
    <div class="player-container">
        <video id="player3" width="640" height="360" controls></video>
        <br/>
        <button class="stop-btn" onclick="stopPlayer('player3')">Stop</button>
    </div>

    <script>
        function setupHLS(playerId, streamUrl) {
            var video = document.getElementById(playerId);
            if (Hls.isSupported()) {
                var hls = new Hls();
                hls.loadSource(streamUrl);
                hls.attachMedia(video);
                video.hlsInstance = hls;  // store hls instance
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = streamUrl;
            }
        }

        function stopPlayer(playerId) {
            var video = document.getElementById(playerId);
            if (video.hlsInstance) {
                video.hlsInstance.destroy();
                video.hlsInstance = null;
            }
            video.pause();
            video.src = "";
        }

        setupHLS('player1', '/proxy/?url=https://partneta.cdn.mgmlcdn.com/omantv/smil:omantv.stream.smil/chunklist.m3u8');
        setupHLS('player2', '/proxy/?url=https://moiptvhls-i.akamaihd.net/hls/live/652107/xrtvi/index.m3u8');
        setupHLS('player3', '/proxy/?url=https://vo-live-media.cdb.cdn.orange.com/Content/Channel/EmiratesChannel/HLS/index.m3u8');
        setupHLS('player3', '/proxy/?url=https://live-hls-web-aje.getaj.net/AJE/index.m3u8');
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        code = request.form.get('passcode')
        if code == PASSCODE:
            return hls_template
        else:
            return login_form + '<p style="color:red;">❌ Incorrect Passcode</p>'
    return login_form

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

        return Response(resp.iter_content(chunk_size=8192), content_type=content_type)
    except Exception as e:
        return f"❌ Error fetching the URL: {e}", 500

@app.route('/logo')
def logo():
    return send_file('TwinStream_logo.png', mimetype='image/png')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
