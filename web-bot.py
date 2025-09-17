from flask import Flask, render_template_string, request, redirect, url_for, flash, get_flashed_messages
import requests
import urllib.parse
import time

app = Flask(__name__)
app.secret_key = "my_super_secret_key_12345"  # нужно для flash сообщений

# Токен бота
TOKEN = "8396535024:AAHPf96vJlBvtSIdg3CfFs1WpPy3c_v22UY"

# Словарь: факультет -> список chat_id
CHAT_GROUPS = {
    "Факультет 1": ["-1002926909436", "-4876180185", "-1003041528826" ,"-1003011395231", "-1002178824233", "-1002934052519", "-1002927882263"],
    "Факультет 2": ["-1002500188374", "-4825429649", "-4974455521", "-4986770512", "-4929891772", "-4635818948", "-4843964710","-4847397460","-4977730143","-1003025080417"],
    "Факультет 3": ["-4874359559", "-4904670915", "-4645257708"],
    "Факультет 4": ["-4968520827", "-4956014609", "-4919217055", "-4813750477"],
    "Факультет 5": ["-4782407490", "-4811814351", "-4884539225", "-4976952805", "-4888639441", "-4864323588", "-4966185457"]  #
}

# HTML-шаблон
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Создание опроса</title>
    <style>
        body {
            font-family: "Gill Sans", sans-serif;
            background: #e6f4ea;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 500px;
            margin: 50px auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        h2 {
            text-align: center;
            color: #333;
        }
        label {
            display: block;
            margin-top: 15px;
            font-weight: bold;
            font-size: 18px;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border: 1px solid #bbb;
            border-radius: 5px;
            font-size: 14px;
        }
        input[type="submit"] {
            width: 100%;
            background: #007BFF;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 5px;
            margin-top: 20px;
            cursor: pointer;
            font-size: 16px;
            transition: 0.3s;
        }
        input[type="submit"]:hover {
            background: #0056b3;
        }

        .faculty-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin-top: 10px;
        }
        .faculty-box {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: row;
            background: #e6f4ea;
            border: 2px solid #2e7d32;
            border-radius: 8px;
            padding: 8px 10px;
            margin: 5px;
            text-align: center;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
            flex: 1 1 45%;
        }
        .faculty-box:hover {
            background: #2e7d32;
            color: white;
            transform: scale(1.05);
        }
        .faculty-text {
            font-style: italic;
            letter-spacing: 1px;
        }

        .result {
            margin-top: 20px;
            background: #e9ffe9;
            border: 1px solid #a6d8a8;
            padding: 15px;
            border-radius: 8px;
        }
        .error {
            background: #ffe9e9;
            border: 1px solid #d8a6a6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Создать опрос для Telegram</h2>
        <form method="POST" autocomplete="off">
            <label>Опрос:</label>
            <input type="text" name="question" required>

            <label>Варианты ответов (через запятую):</label>
            <input type="text" name="options" required>

            <label>Выберите факультет:</label>
            <div class="faculty-container">
                <div class="faculty-box" onclick="selectFaculty('Факультет 1', event)">
                    <span class="faculty-text">МШИ</span>
                </div>
                <div class="faculty-box" onclick="selectFaculty('Факультет 2', event)">
                    <span class="faculty-text">ШНоЗ</span>
                </div>
                <div class="faculty-box" onclick="selectFaculty('Факультет 3', event)">
                    <span class="faculty-text">БШ</span>
                </div>
                <div class="faculty-box" onclick="selectFaculty('Факультет 4', event)">
                    <span class="faculty-text">ШЦТиИИ</span>
                </div>
                <div class="faculty-box" onclick="selectFaculty('Факультет 5', event)">
                    <span class="faculty-text">ШНоЗ</span>
                </div>
            </div>
            <input type="hidden" name="faculty" id="faculty">

            <input type="submit" value="Отправить опрос">
        </form>

        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="result">
              <ul>
              {% for msg in messages %}
                <li>{{ msg }}</li>
              {% endfor %}
              </ul>
            </div>
          {% endif %}
        {% endwith %}
    </div>

    <script>
        function selectFaculty(name, event) {
            document.getElementById('faculty').value = name;
            document.querySelectorAll('.faculty-box').forEach(box => {
                box.style.background = '#e6f4ea';
                box.style.color = '#2e7d32';
            });
            event.currentTarget.style.background = '#2e7d32';
            event.currentTarget.style.color = 'white';
        }
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        question = request.form.get("question")
        options = [opt.strip() for opt in request.form.get("options").split(",")]
        faculty = request.form.get("faculty")
        chat_ids = CHAT_GROUPS.get(faculty, [])

        encoded_options = urllib.parse.quote_plus(str(options).replace("'", '"'))

        for chat_id in chat_ids:
            encoded_question = urllib.parse.quote_plus(question)
            url = f"https://api.telegram.org/bot{TOKEN}/sendPoll?chat_id={chat_id}&question={encoded_question}&options={encoded_options}"
            response = requests.get(url)
            if response.status_code == 200:
                flash(f"Опрос отправлен в чат {chat_id}")
            else:
                flash(f"Ошибка отправки в чат {chat_id}: {response.text}") 
        
            time.sleep(5) 

        return redirect(url_for('index'))

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
