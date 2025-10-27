from flask import Flask, request, render_template_string, jsonify
import requests
import time

app = Flask(__name__)
app.secret_key = 'randomsecretkey'

HTML_PAGE = '''
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Facebook Auto Comment Bot सही वर्शन</title>
    <style>
        body {
            background: #f7f9fc;
            font-family: Arial, sans-serif;
            padding: 20px; max-width: 480px; margin: 50px auto;
            color: #222;
        }
        label { font-weight: bold; margin-top: 10px; display: block;}
        input, button { width: 100%; padding: 8px; margin-top: 6px; border-radius: 5px; border: 1px solid #ccc; }
        button { background-color: #1877f2; color: white; border: none; cursor: pointer; }
        button:disabled { background-color: #999; cursor: not-allowed; }
        #log { margin-top: 20px; min-height: 150px; background: #eee; padding: 10px; border-radius: 6px; overflow-y: auto; }
        #status { margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Facebook Auto Comment Bot</h2>
    <form id="commentForm" onsubmit="return sendComments(event)" autocomplete="off">
        <label>Facebook Access Token:</label>
        <input type="text" id="token" required placeholder="अपना Access Token डालें">
        
        <label>Facebook Post ID:</label>
        <input type="text" id="post_id" required placeholder="जैसे: 1234567890123456">
        
        <label>Post Owner Name:</label>
        <input type="text" id="owner_name" required placeholder="पोस्ट मालिक का नाम">
        
        <label>Delay (सेकंड):</label>
        <input type="number" id="delay" required value="4" min="2" max="30">
        
        <label>Comments TXT File (हर लाइन में एक कमेंट):</label>
        <input type="file" id="comments_file" accept=".txt" required>
        
        <button type="submit" id="startBtn">Comments भेजें</button>
        <button type="button" id="stopBtn" onclick="stopComments()" disabled>रोकें</button>
    </form>
    <div id="status"></div>
    <div id="log"></div>

<script>
    let sending = false;
    let stopRequested = false;

    async function sendComments(e) {
        e.preventDefault();
        if (sending) return;
        sending = true;
        stopRequested = false;

        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
        document.getElementById('status').textContent = "शुरू हो रहा है...";
        document.getElementById('log').innerHTML = "";

        const token = document.getElementById('token').value.trim();
        const post_id = document.getElementById('post_id').value.trim();
        const owner_name = document.getElementById('owner_name').value.trim();
        const delay = Number(document.getElementById('delay').value.trim());
        const fileInput = document.getElementById('comments_file');
        if (!fileInput.files.length) {
            alert("कृपया TXT फ़ाइल चुनें");
            reset();
            return;
        }
        const file = fileInput.files[0];
        const text = await file.text();
        const comments = text.split('
').map(x => x.trim()).filter(x => x.length > 0);

        for (let i = 0; i < comments.length; i++) {
            if (stopRequested) {
                logMsg("टास्क रोका गया।");
                updateStatus("टास्क बंद कर दिया गया। कुल भेजे गए कमेंट्स: " + i);
                reset();
                return;
            }
            const comment = owner_name + ": " + comments[i];
            logMsg("कमेन्ट भेजा जा रहा है: " + comment);
            try {
                let response = await fetch('/send_comment', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({token, post_id, comment})
                });
                let data = await response.json();
                logMsg("Response: " + JSON.stringify(data));
            } catch (error) {
                logMsg("Error: " + error.message);
            }
            updateStatus(`कुल भेजे गए कमेंट्स: ${i+1} / ${comments.length}`);
            await new Promise(r => setTimeout(r, delay * 1000));
        }

        updateStatus("सभी कमेंट्स भेज दिए गए!");
        sending = false;
        reset();
    }

    function stopComments() {
        if (sending) {
            stopRequested = true;
        }
    }

    function logMsg(msg) {
        let logDiv = document.getElementById('log');
        logDiv.innerHTML += `<div>${msg}</div>`;
        logDiv.scrollTop = logDiv.scrollHeight;
    }

    function updateStatus(msg) {
        document.getElementById('status').textContent = msg;
    }

    function reset() {
        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
        sending = false;
        stopRequested = false;
    }
</script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/send_comment', methods=['POST'])
def send_comment():
    data = request.get_json()
    token = data.get('token')
    post_id = data.get('post_id')
    comment = data.get('comment')

    if not token or not post_id or not comment:
        return jsonify({'error': 'सभी पैरामीटर आवश्यक हैं'}), 400

    url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
    payload = {
        'message': comment,
        'access_token': token
    }

    response = requests.post(url, data=payload)
    try:
        return jsonify(response.json())
    except:
        return jsonify({'error': 'रिस्पॉन्स पढ़ने में समस्या'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
