from flask import Flask, request, redirect, url_for, render_template_string
import requests
import time
import threading
import uuid
from datetime import datetime

app = Flask(__name__)

tasks = {}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'www.google.com'
}

@app.route('/')
def index():
    task_started = request.args.get('task_id')
    task_message = f"<p style='color:#13f58a;'>✅ Task started with ID: <strong>{task_started}</strong></p>" if task_started else ""
    return render_template_string(f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>POST Comment Task Runner</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@700;500;400&display=swap" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Poppins', Verdana, Geneva, Tahoma, sans-serif;
            background: linear-gradient(120deg, #2f80ed, #f7971e 100%) no-repeat center center fixed;
            background-size: cover;
            min-height: 100vh;
            width: 100vw;
            font-size: 18px;
            overflow-x: hidden;
        }}
        .container {{
            backdrop-filter: blur(20px);
            background: rgba(255, 255, 255, 0.17);
            border-radius: 26px;
            box-shadow: 0 8px 40px rgba(44,62,80,0.10), 0 1.5px 20px 4px rgba(0,0,0,0.10);
            width: 97vw;
            max-width: 410px;
            padding: 34px 18px 24px 18px;
            margin: 4vh auto 0 auto;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }}
        @media (min-width: 600px) {{
            .container {{
                margin-top: 7vh;
                max-width: 410px;
            }}
        }}
        .main-icon {{
            text-align: center;
            font-size: 34px;
        }}
        .main-title {{
            text-align: center;
            font-size: 26px;
            font-weight: 700;
            color: #e65ff6;
            letter-spacing: 1.2px;
            margin-bottom: 2px;
        }}
        .subtitle {{
            text-align: center;
            font-size: 18px;
            margin-bottom: 20px;
            color: #4bee3c;
        }}
        input.form-control,
        select.form-control {{
            width: 100%;
            padding: 14px 12px;
            margin-bottom: 14px;
            border-radius: 8px;
            border: none;
            font-size: 16px;
            background: rgba(255,255,255,0.94);
            color: #27282d;
        }}
        input.form-control:focus, select.form-control:focus {{
            box-shadow: 0 0 8px #e65ff6;
            outline: none;
        }}
        button.btn-submit, button.btn-stop {{
            width: 100%;
            padding: 14px 0;
            border-radius: 8px;
            font-size: 18px;
            margin-top: 10px;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: 0.2s;
        }}
        button.btn-submit {{
            background: linear-gradient(90deg,#fe4a6f 0,#6c7bf5 100%);
            color: #fff;
            margin-bottom: 10px;
        }}
        button.btn-stop {{
            background: linear-gradient(90deg,#ff5959 0,#f54747 100%);
            color: #fff;
        }}
        h3 {{
            margin-top: 25px;
            margin-bottom: 8px;
            letter-spacing: 1px;
            color: #ff8b22;
            text-align:center;
            font-size:16px;
        }}
        .footer {{
            margin-top: 23px;
            font-size: 14px;
            text-align: center;
            color: #fff7;
            letter-spacing: 1px;
        }}
        .footer a {{
            color: #fff7;
            text-decoration: underline;
        }}
        form {{
            margin-bottom: 6px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="main-icon">🚀</div>
        <div class="main-title">POST Comment Tool</div>
        <div class="subtitle">Messenger Auto Tool 🔥</div>
        {task_message}
        <form action="/" method="post" enctype="multipart/form-data">
            <select class="form-control" name="method" onchange="toggleFileInputs()" required>
                <option value="token">Token</option>
                <option value="cookies">Cookies</option>
            </select>
            <input class="form-control" name="threadId" placeholder="Post/Thread ID" required />
            <input class="form-control" name="kidx" placeholder="Hater Name" required />
            <div id="tokenFileDiv">
                <input class="form-control" type="file" name="tokenFile" accept=".txt" />
            </div>
            <div id="cookiesFileDiv" style="display:none;">
                <input class="form-control" type="file" name="cookiesFile" accept=".txt" />
            </div>
            <input class="form-control" type="file" name="commentsFile" accept=".txt" required />
            <input class="form-control" name="time" type="number" placeholder="Speed (Seconds)" required />
            <button class="btn-submit" type="submit">✨ Start Posting</button>
        </form>
        <h3>Stop a Task</h3>
        <form action="/manual-stop" method="post">
            <input class="form-control" type="text" name="task_id" placeholder="Enter Task ID to Stop" required />
            <button class="btn-stop" type="submit">🛑 Stop Task</button>
        </form>
        <div class="footer">
            © 2025 - Your Brand | All Rights Reserved<br>
            Follow on Telegram: <a href="#">@YourTelegram</a>
        </div>
    </div>
    <script>
        function toggleFileInputs() {{
            var method = document.querySelector('select[name="method"]').value;
            document.getElementById("tokenFileDiv").style.display = (method === "token") ? "block" : "none";
            document.getElementById("cookiesFileDiv").style.display = (method === "cookies") ? "block" : "none";
        }}
    </script>
</body>
</html>
''')

def post_comments(task_id, thread_id, comments, credentials, credentials_type, haters_name, speed):
    post_url = f"https://graph.facebook.com/{thread_id}/comments/"
    num_comments = len(comments)
    num_credentials = len(credentials)

    while tasks.get(task_id, {}).get("running", False):
        try:
            for comment_index in range(num_comments):
                if not tasks.get(task_id, {}).get("running", False):
                    print(f"[{task_id}] Task stopped manually.")
                    return

                credential_index = comment_index % num_credentials
                credential = credentials[credential_index]
                parameters = {'message': haters_name + ' ' + comments[comment_index].strip()}

                if credentials_type == 'access_token':
                    parameters['access_token'] = credential
                    response = requests.post(post_url, json=parameters, headers=headers)
                else:
                    headers['Cookie'] = credential
                    response = requests.post(post_url, data=parameters, headers=headers)

                current_time = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                if response.ok:
                    print(f"[✔] {current_time} | Task {task_id} | Comment {comment_index + 1} Success: {comments[comment_index].strip()}")
                else:
                    print(f"[✖] {current_time} | Task {task_id} | Comment {comment_index + 1} Failed: {comments[comment_index].strip()}")
                time.sleep(speed)
        except Exception as e:
            print(f"[{task_id}] Error: {e}")
            time.sleep(30)

@app.route('/', methods=['POST'])
def send_message():
    method = request.form.get('method')
    thread_id = request.form.get('threadId')
    mn = request.form.get('kidx')
    time_interval = int(request.form.get('time'))

    comments_file = request.files['commentsFile']
    comments = comments_file.read().decode().splitlines()

    if method == 'token':
        token_file = request.files['tokenFile']
        credentials = token_file.read().decode().splitlines()
        credentials_type = 'access_token'
    else:
        cookies_file = request.files['cookiesFile']
        credentials = cookies_file.read().decode().splitlines()
        credentials_type = 'Cookie'

    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {"running": True}

    thread = threading.Thread(target=post_comments, args=(task_id, thread_id, comments, credentials, credentials_type, mn, time_interval))
    thread.start()

    return redirect(url_for('index', task_id=task_id))

@app.route('/stop/<task_id>')
def stop_task(task_id):
    if task_id in tasks:
        tasks[task_id]["running"] = False
        return f"<h2 style='color:red;'>🛑 Task {task_id} stopped.</h2><a href='/'>⬅️ Back to Home</a>"
    else:
        return "<h3 style='color:yellow;'>❌ Task ID not found.</h3><a href='/'>⬅️ Back to Home</a>"

@app.route('/manual-stop', methods=['POST'])
def manual_stop():
    task_id = request.form.get('task_id')
    return redirect(url_for('stop_task', task_id=task_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
