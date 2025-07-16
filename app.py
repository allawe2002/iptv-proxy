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
        body { font-family: Arial, sans-serif; background-color: #f0f0f0; }
        .channel-container { display: flex; align-items: center; background: #333; color: #fff; margin: 10px; padding: 10px; border-radius: 8px; }
        .channel-container video { margin-right: 15px; border: 2px solid #007BFF; }
        .channel-info { display: flex; flex-direction: column; }
        .channel-info h3 { margin: 0 0 10px 0; }
        .control-btn { margin-top: 5px; margin-right: 5px; }
    </style>
</head>
<body>
    

    <h1 class="main-title">░W░e░l░c░o░m░e░ ░t░o░ ░T░w░i░n░S░t░r░e░a░m░T░V░ ░P░r░o░x░y░</h1>

    <img src="/logo" alt="TwinStreamTV Logo" class="logo-banner"/>


<div class="channel-container">
        <video id="player1" width="320" height="180" controls></video>
        <div class="channel-info">
            <h3>Oman TV</h3>
            <button class="control-btn" onclick="toggleStream('player1', '/proxy/?url=https://partneta.cdn.mgmlcdn.com/omantv/smil:omantv.stream.smil/chunklist.m3u8')">Play/Stop</button>
        </div>
    </div>

    <div class="channel-container">
        <video id="player2" width="320" height="180" controls></video>
        <div class="channel-info">
            <h3>🐋  🎀  𝒜𝐿 𝒥𝒶𝒹𝑒𝑒𝒹 𝒯𝒱  🎀  🐋</h3>
            <button class="control-btn" onclick="toggleStream('player2', '/proxy/?url=https://samaflix.com:12103/channel7/tracks-v2a1/mono.m3u8')">Play/Stop</button>
        </div>
    </div>

    <div class="channel-container">
        <video id="player3" width="320" height="180" controls></video>
        <div class="channel-info">
            <h3>Al Jazeera Live</h3>
            <button class="control-btn" onclick="toggleStream('player3', '/proxy/?url=https://live-hls-apps-aja-fa.getaj.net/AJA/index.m3u8')">Play/Stop</button>
        </div>
    </div>

    <div class="channel-container">
        <video id="player4" width="320" height="180" controls></video>
        <div class="channel-info">
            <h3>Al Mayadeen</h3>
            <button class="control-btn" onclick="toggleStream('player4', '/proxy/?url=https://mdnlv.cdn.octivid.com/almdn/smil:mpegts.stream.smil/chunklist_b2000000.m3u8')">Play/Stop</button>
        </div>
    </div>

    <script>
        function setupHLS(video, streamUrl) {
            if (video.hlsInstance) {
                video.hlsInstance.destroy();
            }
            if (Hls.isSupported()) {
                var hls = new Hls();
                hls.loadSource(streamUrl);
                hls.attachMedia(video);
                video.hlsInstance = hls;
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = streamUrl;
            }
        }

        function toggleStream(playerId, streamUrl) {
            var video = document.getElementById(playerId);
            if (video.hlsInstance || !video.paused) {
                if (video.hlsInstance) {
                    video.hlsInstance.destroy();
                    video.hlsInstance = null;
                }
                video.pause();
                video.src = "";
            } else {
                setupHLS(video, streamUrl);
                video.play();
            }
        }
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
