from fastapi import FastAPI
from nicegui import ui
import re
import header
app = FastAPI()

header.page_layout()


@ui.page('/')
def main_page():
    header.page_layout()
    ui.page_title("KEA Password Showcase")
    with ui.splitter() as splitter:
        with splitter.before():
            ui.input(label='Password', placeholder='Start typing password',
                on_change=lambda e: strength_label.set_text("Password strength: " + callback_for_password_input(e)),
                validation={'Input too long': lambda value: len(value) < 30}).props('clearable')
            strength_label = ui.label("Password strength:")
            ui.button("Try to break my password!")
        with splitter.after():
            ui.label("Choose hashing algorithm")
            radio1 = ui.radio(["MD5", "SHA2", "bcrypt"], value=1).props('inline')
        

def calc_password_strength(password):
    score = 0
    if len(password) >= 16:
        score +=1
    if re.search(r'[A-Z]', password):
        score += 1

    # Check for lowercase letters
    if re.search(r'[a-z]', password):
        score += 1

    # Check for digits
    if re.search(r'\d', password):
        score += 1

    # Check for special characters
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    
    if score <= 1:
        return "Very Weak"
    elif score == 2:
        return "Weak"
    elif score == 3:
        return "Moderate"
    elif score == 4:
        return "Strong"
    elif score >= 5:
        return "Very Strong"

def callback_for_password_input(e):
    password = e.value
    strength = calc_password_strength(password)
    return strength



if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080)