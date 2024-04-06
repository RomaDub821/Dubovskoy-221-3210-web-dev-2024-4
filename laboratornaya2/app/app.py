from flask import Flask, render_template, request
import re

app = Flask(__name__)

@app.route("/")
def index():
    title = "ЛР №2"
    return render_template("index.html", title=title, url=request.url)

@app.route('/request_data')
def request_data():
    return render_template('request_data.html',
                           url_params=request.args,
                           headers=request.headers,
                           cookies=request.cookies,
                           form_data=request.form)

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    error = None
    formatted_number = None
    if request.method == 'POST':
        phone_number = request.form.get('phone_number', '')
        error = validate_phone_number(phone_number)
        if not error:
            formatted_number = format_phone_number(phone_number)
    return render_template('phone_form.html', error=error, formatted_number=formatted_number)

def validate_phone_number(phone_number):
    cleaned_number = ''.join(filter(str.isdigit, phone_number))
    length = len(cleaned_number)
    
    if not cleaned_number:
        return "Введите номер телефона"
    elif length not in [10, 11]:
        return "Недопустимый ввод. Неверное количество цифр."
    elif length == 11 and not (cleaned_number.startswith(('7', '8'))):
        return "Недопустимый ввод. Номер должен начинаться с '+7' или '8'."
    elif not phone_number.replace('+', '').replace('-', '').replace('(', '').replace(')', '').replace('.', '').replace(' ', '').isdigit():
        return "Недопустимый ввод. В номере телефона встречаются недопустимые символы."
    else:
        return None

def format_phone_number(phone_number):
    cleaned_number = ''.join(filter(str.isdigit, phone_number))
    length = len(cleaned_number)
    
    if length == 11 and cleaned_number.startswith('7'):
        cleaned_number = '8' + cleaned_number[1:]
    
    if length == 10:
        formatted_number = f'8-{cleaned_number[:3]}-{cleaned_number[3:6]}-{cleaned_number[6:8]}-{cleaned_number[8:]}'
    elif length == 11:
        formatted_number = f'{cleaned_number[:1]}-{cleaned_number[1:4]}-{cleaned_number[4:7]}-{cleaned_number[7:9]}-{cleaned_number[9:]}'
    else:
        return "Недопустимый ввод. Неверное количество цифр или некорректный формат номера."
    
    return formatted_number

if __name__ == '__main__':
    app.run(debug=True)