from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify
import requests
import threading
import time

app = Flask(__name__)
app.secret_key = 'randomsecretkey'

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Facebook Auto Comment Bot लाइव स्टेटस</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
        body {
            background-image: url('https://images.unsplash.com/photo-1506744038136-46273834b3fb');
            background-size: cover;
            font-family: Arial, sans-serif;
            color: #222;
            min-height: 100vh;
            margin: 0;
            padding: 0;
        }
        .container {
            margin: 6% auto;
            background: rgba(255,255,255,0.95);
            border-radius: 12px;
            padding: 30px 20px;
            max-width: 480px;
            box-shadow: 0 0 20px #33333344;
        }
        h1 {
            text-align: center;
            margin-bottom: 12px;
            animation: bounceInDown 1.4s;
        }
        label {
            margin-top: 14px;
            display: inline-block;
            font-weight: bold;
        }
        input, select {
            width: 100%;
            margin: 7px 0 17px;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #bbb;
            font-size: 16px;
        }
        input[type="file"] {
            padding: 3px;
        }
        button {
            background: #1877f2;
            color: white;
            padding: 9px 25px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: background .15s;
            width: 48%;
            margin-right: 4%;
        }
        button:hover {
            background: #1353ae;
        }
        #stop-btn {
            background: #d9534f;
        }
        #stop-btn:hover {
            background: #b52b27;
        }
        .flash {
            margin: 10px 0;
            padding: 7px 20px;
            border-radius: 6px;
            font-weight: bold;
            text-align: center;
        }
        .flash-success { background: #c4f7cf; color: #008512; }
        .flash-danger { background: #ffd9d9; color: #cc1111; }
        ul.log {
            max-height: 220px;
            overflow-y: auto;
            background: #f0f0f0;
            border-radius: 8px;
            padding: 10px;
            list-style-type: none;
            font-size: 14px;
        }
        ul.log li {
            margin-bottom: 6px;
        }
        #status {
            font-weight: bold;
            margin-top: 15px;
            font-size: 16px;
            text-align: center;
        }
    </style>
</head>
<body>
<div class="container animate__animated animate__fadeIn">
    <h1>Facebook ऑटो कमेंट 🚀</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="flash flash-{{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    <form id="commentForm" method="POST" enctype="multipart/form-data" autocomplete="off" onsubmit="startComments(event)">
        <label>Facebook Access Token</label>
        <input type="text" name="token" id="token" required placeholder="Access Token लिखें" value="">
        <label>Facebook Post ID</label>
        <input type="text" name="post_id" id="post_id" required placeholder="जैसे: 1234567890123456">
        <label>Post Owner Name</label>
        <input type="text" name="owner_name" id="owner_name" required placeholder="पोस्ट मालिक का नाम">
        <label>Delay (सेकंड में)</label>
        <input type="number" name="delay" id="delay" value="4" min="2" max="30" required>
        <label>Comments TXT फ़ाइल (एक कमेंट प्रति लाइन)</label>
        <input type="file" name="comments" id="comments" accept=".txt" required>
        <div style="margin-top:20px;">
            <button type="submit" id="start-btn">Comments भेजें</button>
            <button type="button" id="stop-btn" onclick="stopComments()" disabled>बंद करें</button>
        </div>
    </form>
    <div id="status"></div>
    <ul id="log" class="log"></ul>
</div>

<script>
    let stopFlag = false;
    let taskId = null;

    async function startComments(e) {
        e.preventDefault();
        stopFlag = false;
        taskId = Date.now(); // task id generate

        document.getElementById('status').innerText = 'Comments भेजना शुरू...';
        document.getElementById('start-btn').disabled = true;
        document.getElementById('stop-btn').disabled = false;
        document.getElementById('log').innerHTML = '';

        const form = e.target;
        const token = form.token.value.trim();
        const post_id = form.post_id.value.trim();
        const owner_name = form.owner_name.value.trim();
        const delay = form.delay.value.trim();
        const fileInput = form.comments;
        if (!fileInput.files.length) {
            alert("कृपया TXT फ़ाइल चुनें।");
            resetButtons();
            return;
        }
        const file = fileInput.files[0];
        const text = await file.text();
        const comments = text.split('
').map(s => s.trim()).filter(s => s.length > 0);

        for (let i = 0; i < comments.length; i++) {
            if (stopFlag) {
                appendLog("टास्क रोका गया।");
                document.getElementById('status').innerText = "टास्क रोका गया। कुल भेजे गए कमेंट: " + i;
                resetButtons();
                return;
            }
            const comment = `${owner_name}: ${comments[i]}`;
            appendLog(`कमेंट भेजा जा रहा है: "${comment}"`);
            try {
                const response = await fetch('/send_comment', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token, post_id, comment})
                });
                const data = await response.json();
                appendLog(`Response: ${JSON.stringify(data)}`);
            } catch (error) {
                appendLog("Error: " + error.message);
            }
            document.getElementById('status').innerText = `कुल भेजे गए कमेंट: ${i + 1} / ${comments.length}`;
            await new Promise(res => setTimeout(res, delay * 1000));
        }
        appendLog("सभी कमेंट्स भेज दिए गए!");
        document.getElementById('status').innerText = "सभी कमेंट्स भेज दिए गए!";
        resetButtons();
    }

    function stopComments() {
        stopFlag = true;
    }

    function appendLog(msg) {
        const logEl = document.getElementById('log');
        let li = document.createElement('li');
        li.textContent = msg;
        logEl.appendChild(li);
        logEl.scrollTop = logEl.scrollHeight;
    }

    function resetButtons() {
        document.getElementById('start-btn').disabled = false;
        document.getElementById('stop-btn').disabled = true;
    }
</script>
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE)

@app.route('/send_comment', methods=['POST'])
def send_comment_api():
    data = request.get_json()
    token = data.get('token')
    post_id = data.get('post_id')
    comment = data.get('comment')
    if not (token and post_id and comment):
        return jsonify({'error': 'Invalid input parameters'}), 400
    url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
    payload = {
        'message': comment,
        'access_token': token
    }
    resp = requests.post(url, data=payload)
    try:
        return jsonify(resp.json())
    except Exception:
        return jsonify({'error': 'Failed to parse response'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
