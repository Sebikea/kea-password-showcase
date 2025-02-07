from fastapi import FastAPI
from nicegui import ui
import re
import header
import os
from pathlib import Path
app = FastAPI()


header.page_layout()

path_to_wordlist = Path(os.getcwd() + "/wordlists")
path_to_logo = Path(os.getcwd() + "/assets/kea-logo-dk-web.jpg")

@ui.page('/')
def main_page():
    header.page_layout()
    ui.page_title("KEA Password Showcase")
    #Divide the main content into 3 sections, left section for password stuff, right for controls and middle for information
    with ui.row().classes('flex justify-stretch'):

        #Left card and content is here
        left_card = ui.card().classes('w-max justify-center mx-auto')
        with left_card:
            ui.label("How important is password strength?").classes('text-lg')
            password_input = ui.input(label='Password', placeholder='Start typing password',
                on_change=lambda e: strength_label.set_text("Password strength: " + callback_for_password_input(e)),
                validation={'Input too long': lambda value: len(value) < 30})
            strength_label = ui.label("Password strength:")
            ui.button("Try to break my password!",on_click=break_password(password_input._text))

        #Middle content is here
        middle_card = ui.card().classes('w-max absolute left-0 right-0 flex mx-auto')
        with middle_card:
            ui.label("Middle content")
        right_card = ui.card().classes('w-max absolute right-10 mx-auto')

        #Right card for controls are here
        with right_card:
            ui.label("Choose hashing algorithm").classes('text-lg')
            radio1 = ui.radio(["MD5", "SHA2-256", "bcrypt"],value="MD5").props('inline')

        #External resources
        with ui.row().classes('w-1/6 absolute left-2 bottom-2 border-2'):   
            ui.label("Useful resources about passwords").classes('font-bold')
            ui.link("Bitwarden best practices for passwords", "https://bitwarden.com/password-strength/#Password-Strength-Testing-Tool")
            ui.link("Test your e-mail against known breaches", "https://haveibeenpwned.com")

        #KEA logo and credits
        with ui.row().classes('w-1/6 absolute right-2 bottom-2 border-2'):
            ui.image(path_to_logo)
            ui.label("Credit: Dany (daka@kea.dk)")
            ui.label("Sebastian (sebi@kea.dk)")
    
        
def break_password(password):
    print(password)

def calc_password_strength(password):
    score = 0
    if len(password) >= 8:
        score +=1
    if len(password) >= 16:
        score +=1
    if len(password) >= 20:
        score +=1
    if len(password) >= 25:
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