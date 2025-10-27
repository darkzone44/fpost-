from flask import Flask, request, render_template_string, flash
import requests
import time

app = Flask(__name__)
app.secret_key = 'randomsecretkey'

# HTML content को इस variable में रखेंगे ताकि पूरा कोड एक ही फाइल में रहे
HTML_PAGE = '''
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Facebook Auto Comment Bot</title>
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
            background: rgba(255,255,255,0.85);
            border-radius: 12px;
            padding: 40px 28px;
            max-width: 420px;
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
        .btn {
            background: #1877f2;
            color: white;
            padding: 9px 25px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: background .15s;
            width: 100%;
        }
        .btn:hover {
            background: #1353ae;
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
            max-height: 200px;
            overflow-y: auto;
            background: #f0f0f0;
            border-radius: 8px;
            padding: 10px;
            list-style-type: none;
        }
        ul.log li {
            margin-bottom: 6px;
            font-size: 14px;
        }
    </style>
</head>
<body>
<div class="container animate__animated animate__fadeIn">
    <h1>Facebook ऑटो कमेंट बॉट 🚀</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="flash flash-{{ category }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    <form method="POST" enctype="multipart/form-data" autocomplete="off">
        <label>Facebook Access Token</label>
        <input type="text" name="token" required placeholder="Access Token लिखें" value="">
        <label>Facebook Post ID</label>
        <input type="text" name="post_id" required placeholder="जैसे: 1234567890123456">
        <label>Post Owner Name</label>
        <input type="text" name="owner_name" required placeholder="पोस्ट मालिक का नाम">
        <label>Delay (सेकंड में)</label>
        <input type="number" name="delay" value="4" min="2" max="30" required>
        <label>Comments TXT फ़ाइल (एक कमेंट प्रति लाइन)</label>
        <input type="file" name="comments" accept=".txt" required>
        <button type="submit" class="btn">Comments भेजें</button>
    </form>
    {% if log %}
        <h3 style="margin-top:30px;">लॉग:</h3>
        <ul class="log">
        {% for comment, resp in log %}
            <li><strong>{{ comment }}</strong> - {{ resp }}</li>
        {% endfor %}
        </ul>
    {% endif %}
</div>
</body>
</html>
'''

def send_comment(token, post_id, comment):
    url = f"https://graph.facebook.com/v18.0/{post_id}/comments"
    payload = {
        'message': comment,
        'access_token': token
    }
    response = requests.post(url, data=payload)
    # JSON response को string में बदलकर लौटाएं, ताकि error या success info दिखा सकें
    try:
        return response.json()
    except Exception:
        return response.text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        token = request.form['token'].strip()
        post_id = request.form['post_id'].strip()
        owner_name = request.form['owner_name'].strip()
        delay = int(request.form.get('delay', 4))
        if 'comments' not in request.files:
            flash("TXT फ़ाइल अपलोड नहीं हुई।", "danger")
            return render_template_string(HTML_PAGE)
        comments_file = request.files['comments']
        try:
            comments_text = comments_file.read().decode('utf-8')
        except Exception:
            flash("TXT फ़ाइल पढ़ने में समस्या आई।", "danger")
            return render_template_string(HTML_PAGE)
        comments = [line.strip() for line in comments_text.splitlines() if line.strip()]
        if not comments:
            flash("TXT फ़ाइल में कोई कमेंट नहीं है।", "danger")
            return render_template_string(HTML_PAGE)
        
        log = []
        for comment in comments:
            full_comment = f"{owner_name}: {comment}"
            resp = send_comment(token, post_id, full_comment)
            log.append((full_comment, resp))
            time.sleep(delay)
        flash("सभी कमेंट्स भेज दिए गए!", "success")
        return render_template_string(HTML_PAGE, log=log)
    return render_template_string(HTML_PAGE, log=None)

if __name__ == "__main__":
    app.run(debug=True)
