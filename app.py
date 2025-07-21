from flask import Flask, request, Response, send_file
import requests
from urllib.parse import urljoin, urlencode
import os

app = Flask(__name__)

PASSCODE = "372420"

login_form = '''
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; background-color: #1e1e1e; color: white;">
        <img src="/static/logos/TwinStream.png" alt="TwinStreamTV Logo" style="width: 300px; margin-bottom: 20px;">
        <h2>🆆🅴🅻🅲🅾🅼🅴 🆃🅾 🆃🆆🅸🅽🆂🆃🆁🅴🅰🅼🆃🆅</h2>

        <form method="post" style="text-align: center;">
            <input type="password" name="passcode" placeholder="Enter Passcode"
                   style="width: 300px; height: 45px; font-size: 18px; padding: 5px; margin-bottom: 15px;
                   border: 2px solid #007BFF; border-radius: 5px; box-shadow: 0px 0px 10px rgba(0,0,0,0.3);"/>
            <br>
            <input type="submit" value="Access"
                   style="width: 150px; height: 45px; font-size: 18px; background-color: #007BFF; color: white; border: none; border-radius: 5px; cursor: pointer;"/>
        </form>
    </div>
'''

hls_template = '''
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>

<script>
    function proxyIfHttp(url) {
        return url.startsWith('http://') ? `/proxy/?url=${encodeURIComponent(url)}` : url;
    }

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
        let finalUrl = proxyIfHttp(streamUrl);

        if (video.hlsInstance || !video.paused) {
            if (video.hlsInstance) {
                video.hlsInstance.destroy();
                video.hlsInstance = null;
            }
            video.pause();
            video.src = "";
        } else {
            setupHLS(video, finalUrl);
            video.play();
        }
    }
</script>

<h1 class="main-title">░W░e░l░c░o░m░e░ ░t░o░ ░T░w░i░n░S░t░r░e░a░m░T░V░ ░P░r░o░x░y░</h1>

<div>
    <h2>🍫 ⋆ 🍭 🎀 𝒜𝐿 𝒜𝑅𝒜𝐵𝒴 𝒩𝐸𝒲𝒮 🎀 🍭 ⋆ 🍫</h2>
    <video id="player1" width="320" height="180" controls poster="/static/logos/alaraby.png"></video>
    <button onclick="toggleStream('player1', 'https://live.kwikmotion.com/alaraby1live/alaraby_abr/alaraby1publish/alaraby1_source/chunks.m3u8')">Play/Stop</button>
</div>

<div>
    <h2>🐋 🎀 𝒜𝐿 𝒥𝒶𝒹𝑒𝑒𝒹 𝒯𝒱 🎀 🐋</h2>
    <video id="player2" width="320" height="180" controls poster="/static/logos/aljadeed.png"></video>
    <button onclick="toggleStream('player2', 'https://samaflix.com:12103/channel7/tracks-v2a1/mono.m3u8')">Play/Stop</button>
</div>

<div>
    <h2>🐙 🎀 𝑀𝐵𝒞-𝟤 🎀 🐙</h2>
    <video id="player3" width="320" height="180" controls poster="/static/logos/mbc2.png"></video>
    <button onclick="toggleStream('player3', 'https://edge66.magictvbox.com/liveApple/MBC_2/index.m3u8')">Play/Stop</button>
</div>

<div>
    <h2>🍭 ⋆ 🍭 🎀 𝒜𝐿 𝒥𝒜𝒵𝐸𝐸𝑅𝒜 𝒩𝐸𝒲𝒮 🎀 🍭 ⋆ 🍭</h2>
    <video id="player4" width="320" height="180" controls poster="/static/logos/aljazeera.png"></video>
    <button onclick="toggleStream('player4', 'https://live-hls-apps-aja-fa.getaj.net/AJA/index.m3u8')">Play/Stop</button>
</div>

<div>
    <h2>🐖 ⋆ 🐭 🎀 𝒜𝓁 𝑀𝒶𝓎𝒶𝒹𝑒𝑒𝓃 🎀 🐭 ⋆ 🐖</h2>
    <video id="player5" width="320" height="180" controls poster="/static/logos/almayadeen.png"></video>
    <button onclick="toggleStream('player5', 'https://mdnlv.cdn.octivid.com/almdn/smil:mpegts.stream.smil/chunklist_b2000000.m3u8')">Play/Stop</button>
</div>

<div>
    <h2>⚛🌌 🎀 𝑀𝒯𝒱 𝐿𝐸𝐵𝒜𝒩🍩𝒩 𝒯𝒱 🎀 🌌⚛</h2>
    <video id="player6" width="320" height="180" controls poster="/static/logos/mtv.png"></video>
    <button onclick="toggleStream('player6', 'https://hms.pfs.gdn/v1/broadcast/mtv/playlist.m3u8')">Play/Stop</button>
</div>

<div>
    <h2>⋆` 🎀 𝒩𝐵𝒩 𝒯𝒱 🎀 `⋆</h2>
    <video id="player7" width="320" height="180" controls poster="/static/logos/nbn.png"></video>
    <button onclick="toggleStream('player7', '/proxy/?url=http://5.9.119.146:8883/nbn/index.m3u8')">Play/Stop</button>
</div>

<div>
    <h2>🍑 ⋆ 🍉 🎀 𝒯𝐿𝒞 🍩𝒮𝒩 🎀 🍉 ⋆ 🍑</h2>
    <video id="player8" width="320" height="180" controls poster="/static/logos/tlc.png"></video>
    <button onclick="toggleStream('player8', '/static/playlists/TLC.m3u8')">Play/Stop</button>
</div>
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
        'User-Agent': 'Mozilla/5.0',
        'Referer': target_url,
    }

    try:
        resp = requests.get(target_url, headers=headers, stream=True)
        content_type = resp.headers.get('Content-Type', '')

        if '.m3u8' in target_url or 'application/vnd.apple.mpegurl' in content_type:
            original_content = resp.text
            base_url = target_url.rsplit('/', 1)[0] + '/'

            def rewrite_line(line):
                if line.strip().startswith('#') or line.strip() == '':
                    return line + '\n'
                absolute_url = urljoin(base_url, line.strip())
                if absolute_url.startswith('http://'):
                    absolute_url = absolute_url.replace('http://', 'https://')
                proxied_url = f"/proxy/?{urlencode({'url': absolute_url})}"
                return proxied_url + '\n'

            rewritten_content = ''.join(rewrite_line(line) for line in original_content.splitlines())
            return Response(rewritten_content, content_type='application/vnd.apple.mpegurl')

        return Response(resp.iter_content(chunk_size=8192), content_type=content_type)

    except Exception as e:
        return f"❌ Error fetching the URL: {e}", 500

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/logo')
def logo():
    return send_file('TwinStream_logo.png', mimetype='image/png')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
