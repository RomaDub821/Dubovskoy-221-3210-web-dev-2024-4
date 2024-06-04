def validate_password(password):
    errors = []
    if not (8 <= len(password) <= 128):
        errors.append("Пароль должен содержать от 8 до 128 символов")
    if not any(char.isupper() for char in password):
        errors.append("Пароль должен содержать как минимум одну заглавную букву")
    if not any(char.islower() for char in password):
        errors.append("Пароль должен содержать как минимум одну строчную букву")
    if not any(char.isdigit() for char in password):
        errors.append("Пароль должен содержать как минимум одну цифру")
    if ' ' in password:
        errors.append("Пароль не должен содержать пробелы")
    allowed_symbols = r"~!?\@#\$%\^&\*_\-\+\(\)\[\]\{\}<>\\/\"'\.,:;"
    if not all(char.isalnum() or char in allowed_symbols for char in password):
        errors.append("Пароль может содержать только латинские или кириллические буквы, цифры "
                      "и следующие символы: ~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \\ | \" ' . , : ;")
    return errors

def validate_user_data(user_data):
    errors = {}
    required_fields = ['login', 'password', 'last_name', 'first_name']
    for field in required_fields:
        if not user_data.get(field):
            errors[field] = "Это поле не может быть пустым"
    if len(user_data.get('login', '')) < 5:
        errors['login'] = "Логин должен содержать не менее 5 символов"
    password_errors = validate_password(user_data.get('password', ''))
    if password_errors:
        errors['password'] = ", ".join(password_errors)
    return errors