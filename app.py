from flask import Flask, request, Response, send_file
import requests
from urllib.parse import urljoin, urlencode

app = Flask(__name__)

PASSCODE = "372420"

@app.route('/proxy/')
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return "❌ Missing 'url' query parameter", 400

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Referer': target_url
    }

    try:
        resp = requests.get(target_url, headers=headers, stream=True, timeout=10)
        content_type = resp.headers.get('Content-Type', '')

        if '.m3u8' in target_url or 'application/vnd.apple.mpegurl' in content_type:
            original_content = resp.text
            base_url = target_url.rsplit('/', 1)[0] + '/'

            def rewrite_line(line):
                if line.strip().startswith('#') or line.strip() == '':
                    return line + '\n'

                absolute_url = urljoin(base_url, line.strip())

                if target_url.startswith('https://') and absolute_url.startswith('http://') and 'iptvplatinum.net' not in absolute_url:
                    absolute_url = absolute_url.replace('http://', 'https://')

                proxied_url = f"/proxy/?{urlencode({'url': absolute_url})}"
                return proxied_url + '\n'

            rewritten_content = ''.join(rewrite_line(line) for line in original_content.splitlines())
            return Response(rewritten_content, content_type='application/vnd.apple.mpegurl')

        return Response(resp.iter_content(chunk_size=8192), content_type=content_type)

    except Exception as e:
        return f"❌ Error fetching the URL: {e}", 500



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



<!DOCTYPE html>
<html>
<head>
<title>TwinStreamTV</title>
<link rel="icon" href="/static/favicon.ico" type="image/x-icon">
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<style>
        body { font-family: Arial, sans-serif; background-color: #f0f0f0; }
        .channel-container { display: flex; align-items: center; background: #333; color: #fff; margin: 10px; padding: 10px; border-radius: 8px; }
        .channel-container video { margin-right: 15px; border: 2px solid #007BFF; }
        .channel-info { display: flex; flex-direction: column; }
        .channel-info h3 { margin: 0 0 10px 0; }
        .control-btn {
    margin-top: 5px;
    margin-right: 5px;
    padding: 10px 20px;  /* Adjusts vertical & horizontal size */
    font-size: 16px;     /* Increases text size */
    height: 50px;        /* Directly controls button height */
    background-color: #007BFF;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

    </style>
</head>
<body>
    

    <h1 class="main-title">░W░e░l░c░o░m░e░ ░t░o░ ░T░w░i░n░S░t░r░e░a░m░T░V░ ░P░r░o░x░y░</h1>

     <img src="/logo" alt="TwinStreamTV Logo" class="logo-banner" 
     style="display: block; margin-left: auto; margin-right: auto; width: 60%; height: auto; margin-bottom: 20px;">

<div class="channel-container">
        <img src="/static/logos/alaraby.png" alt="Alaraby Logo" width="100">
        <video id="player1" width="320" height="180" controls poster="/static/logos/alaraby.png"></video>
        <div class="channel-info">
            <h3>  🎀  𝒜𝐿 𝒜𝑅𝒜𝐵𝒴 𝒩𝐸𝒲𝒮  🎀  </h3>
            <button class="control-btn" onclick="toggleStream('player1', '/proxy/?url=https://live.kwikmotion.com/alaraby1live/alaraby_abr/alaraby1publish/alaraby1_source/chunks.m3u8')">Play/Stop</button>
        </div>
    </div>

    <div class="channel-container">
        <img src="/static/logos/aljadeed.png" alt="Al jadeed Logo" width="100">
        <video id="player2" width="320" height="180" controls poster="/static/logos/aljadeed.png"></video>
        <div class="channel-info">
            <h3>  🎀  𝒜𝐿 𝒥𝒶𝒹𝑒𝑒𝒹 𝒯𝒱  🎀 </h3>
            <button class="control-btn" onclick="toggleStream('player2', '/proxy/?url=https://samaflix.com:12103/channel7/tracks-v2a1/mono.m3u8')">Play/Stop</button>
        </div>
    </div>
    <div class="channel-container">
        <img src="/static/logos/mbc2.png" alt="MBC2 Logo" width="100">
        <video id="player3" width="320" height="180" controls poster="/static/logos/mbc2.png"></video>
        <div class="channel-info">
            <h3>🐙  🎀  𝑀𝐵𝒞-𝟤  🎀  🐙</h3>
            <button class="control-btn" onclick="toggleStream('player3', 'https://edge66.magictvbox.com/liveApple/MBC_2/index.m3u8')">Play/Stop</button>
        </div>
    </div>

    <div class="channel-container">
        <img src="/static/logos/aljazeera.png" alt="Al jazeera Logo" width="100">
        <video id="player4" width="320" height="180" controls poster="/static/logos/aljazeera.png"></video>
        <div class="channel-info">
            <h3>  🎀  𝒜𝐿 𝒥azeera 𝒩ews  🎀  </h3>
            <button class="control-btn" onclick="toggleStream('player4', '/proxy/?url=https://live-hls-apps-aja-fa.getaj.net/AJA/index.m3u8')">Play/Stop</button>
        </div>
    </div>

    <div class="channel-container">
        <img src="/static/logos/almayadeen.png" alt="Almayadeen Logo" width="100">
        <video id="player5" width="320" height="180" controls poster="/static/logos/almayadeen.png"></video>
       <div class="channel-info">
            <h3>⋆ 🎀  𝒜𝓁 𝑀𝒶𝓎𝒶𝒹𝑒𝑒𝓃  🎀 </h3>
            <button class="control-btn" onclick="toggleStream('player5', 'https://mdnlv.cdn.octivid.com/almdn/smil:mpegts.stream.smil/chunklist_b2000000.m3u8')">Play/Stop</button>
        </div>
    </div>

        <div class="channel-container">
        <img src="/static/logos/mtv.png" alt="MTV Lebanon Logo" width="100">
        <video id="player6" width="320" height="180" controls poster="/static/logos/mtv.png"></video>
        <div class="channel-info">
            <h3>  🎀  𝑀𝒯𝒱 𝐿𝐸𝐵𝒜𝒩🍩𝒩 𝒯𝒱  🎀  </h3>
            <button class="control-btn" onclick="toggleStream('player6', 'https://hms.pfs.gdn/v1/broadcast/mtv/playlist.m3u8')">Play/Stop</button>
       </div>
     </div>
    
    <div class="channel-container">
        <img src="/static/logos/nbn.png" alt="NBN Logo" width="100">
        <video id="player7" width="320" height="180" controls poster="/static/logos/nbn.png"></video>
        <div class="channel-info">
            <h3> 🎀  𝒩𝐵𝒩 𝒯𝒱  🎀 </h3>
            <button class="control-btn" onclick="toggleStream('player7', 'https://samaflix.com:12103/channel5/tracks-v2a1/mono.m3u8')">Play/Stop</button>
     </div>
     </div>

     <div class="channel-container">
    <img src="/static/logos/tlc.png" alt="TLC Logo" width="100">
    <video id="player8" width="320" height="180" controls poster="/static/logos/tlc.png"></video>
    <div class="channel-info">
        <h3>🎀 𝒯𝐿𝒞 O𝒮𝒩 🎀 </h3>
        <button class="control-btn" onclick="toggleStream('player8', 'https://v4.thetvapp.to/hls/TLCEast/tracks-v2a1/mono.m3u8?token=ycQvL8FArNfxOG3WIX8W0w&expires=1753277350&user_id=NHd4UFJLM3ZqWFByU21WTGhhQ1FPUkI1bm5UR2QzSkdlTjE3NGtkbw==')">Play/Stop</button>

 </div>
</div>

<div class="channel-container">
        <img src="/static/logos/dhafra.png" alt="Dhafra Tv Logo" width="100">
        <video id="player9" width="320" height="180" controls poster="/static/logos/dhafra.png"></video>
        <div class="channel-info">
            <h3> 🎀  DHAFRA 𝒯𝒱  🎀 </h3>
            <button class="control-btn" onclick="toggleStream('player9', '/proxy/?url=https://rtmp-live-ingest-eu-west-3-universe-dacast-com.akamaized.net/transmuxv1/streams/dbb8ac05-a020-784c-3a95-6ed027941532.m3u8')">Play/Stop</button>
     </div>
     </div>
     <div class="channel-container">
        <img src="/static/logos/dubaizaman.png" alt="Dubai Zaman Logo" width="100">
        <video id="player10" width="320" height="180" controls poster="/static/logos/dubaizaman.png"></video>
        <div class="channel-info">
            <h3> 🎀  𝒟𝓊𝒷𝒶𝒾 𝒵𝒶𝓂𝒶𝓃  🎀 </h3>
            <button class="control-btn" onclick="toggleStream('player10', '/proxy/?url=https://dmiffthftl.cdn.mangomolo.com/dubaizaman/smil:dubaizaman.stream.smil/chunklist_b725000.m3u8')">Play/Stop</button>
     </div>
     </div>
      <div class="channel-container">
        <img src="/static/logos/manartv.png" alt="Al Manar TV Logo" width="100">
        <video id="player11" width="320" height="180" controls poster="/static/logos/manartv.png"></video>
        <div class="channel-info">
            <h3>  🎀  𝒜𝓁 𝑀𝒶𝓃𝒶𝓇 𝒯𝒱  🎀 </h3>
            <button class="control-btn" onclick="toggleStream('player11', 'https://edge.fastpublish.me/live/index.fmp4.m3u8')">Play/Stop</button>
     </div>
     </div>
     <div class="channel-container">
        <img src="/static/logos/hgtv.png" alt="HGTV Logo" width="100">
        <video id="player12" width="320" height="180" controls poster="/static/logos/hgtv.png"></video>
        <div class="channel-info">
            <h3>  🎀  𝐻𝒢𝒯𝒱 𝒰𝒮𝒜  🎀  </h3>
            <button class="control-btn" onclick="toggleStream('player12', 'https://v13.thetvapp.to/hls/HGTVEast/tracks-v2a1/mono.m3u8?token=9LmbymoAF5sm_LfX_oW12Q&expires=1753277219&user_id=NHd4UFJLM3ZqWFByU21WTGhhQ1FPUkI1bm5UR2QzSkdlTjE3NGtkbw==')">Play/Stop</button>
     </div>
     </div>
     <div class="channel-container">
        <img src="/static/logos/cbc.png" alt="CBC NEWS Logo" width="100">
        <video id="player13" width="320" height="180" controls poster="/static/logos/cbc.png"></video>
        <div class="channel-info">
            <h3>  🎀  𝒞𝐵𝒞 𝒩𝐸𝒲𝒮  🎀 </h3>
            <button class="control-btn" onclick="toggleStream('player13', 'https://apollo.production-public.tubi.io/live/ac-cbc2.m3u8')">Play/Stop</button>
     </div>
     </div>
    <div class="channel-container">
        <img src="/static/logos/cnn.png" alt="CNN USA Logo" width="100">
        <video id="player14" width="320" height="180" controls poster="/static/logos/cnn.png"></video>
        <div class="channel-info">
            <h3>  🎀  𝒞𝒩𝒩  🎀 </h3>
            <button class="control-btn" onclick="toggleStream('player14', 'https://fl3.moveonjoy.com/CNN/tracks-v1a1/mono.ts.m3u8')">Play/Stop</button>
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


@app.route('/logo')
def logo():
    return send_file('TwinStream_logo.png', mimetype='image/png')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
