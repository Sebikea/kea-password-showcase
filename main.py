from fastapi import FastAPI
from nicegui import ui
import header
import os
import hashlib
import bcrypt
import subprocess
import threading
import queue
from password_chart import page_layout
from password_helpers import *
from pathlib import Path
app = FastAPI()


line_queue = queue.Queue()


path_to_wordlist = Path(os.getcwd() + "/wordlists/rockyou.txt")
path_to_logo = Path(os.getcwd() + "/assets/kea-logo-dk-web.jpg")
path_to_johnpot = Path(os.getcwd() + "/.pot")


@ui.page('/')
def main_page():

    def update_ui():
        # Check the queue and update the UI if new lines are available.
        while not line_queue.empty():
            line = line_queue.get()
            # Append each line as a new label inside the container.
            ui.label(line).move(output_container)
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
            start_button = ui.button("Try to break my password!",on_click=lambda: (break_password(password_input.value, radio1.value, radio2.value, radio3.value)))

        #Middle content is here
        middle_card = ui.card().classes('w-1/2 absolute left-0 right-0 mx-auto')
        with middle_card:
            status = ui.label("Enter password to begin").classes('font-bold')
            output_container = ui.column()
        right_card = ui.card().classes('w-max absolute right-10 mx-auto')

        #Right card for controls are here
        with right_card:
            ui.label("Choose hashing algorithm").classes('text-lg')
            radio1 = ui.radio(["MD5", "SHA2-256", "bcrypt"],value="MD5").props('inline')
            ui.label("Choose cracker").classes('text-lg')
            radio2 = ui.radio(["john", "hashcat"],value="john").props('inline')
            ui.label("Choose cracking method").classes('text-lg')
            radio3 = ui.radio(["dictionary", "brute-force", "Rules (best64)"],value="dictionary")
            ui.label("Full output").classes('text-lg')
            radio4 = ui.radio(["yes", "no"],value="no")


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
        timer = ui.timer(interval=0.5, callback=update_ui)
        

    def break_password(password, hash, program, method):
        output_container.clear()
        status.set_text("Processing...")
        status.classes('font-bold')
        start_button.disable()
        
        
        with output_container:
            ui.separator()
            if "bcrypt" not in radio1.value: 
                password_hash = get_hash_value(password, hash)
                ui.label("Your hash digest in {0} is {1}".format(hash, password_hash))
            else:
                password_hash, salt = get_hash_value(password, hash)
                password_hash = password_hash.decode()
                salt = salt.decode()
                ui.label("I have generated a random salt for you: {0}".format(salt))
                ui.label("Your hash digest in {0} is {1}:".format(hash, password_hash))

        command = generate_command(password, hash, password_hash, program, method)
            
        threading.Thread(target=start_cracking, args=(command, password_hash), daemon=True).start()
        #start_cracking(command, password_hash)

    def start_cracking(command, password_hash):
        with middle_card:
            spinner = ui.spinner(size='lg').classes('fixed-center')
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                if "no" in radio4.value:
                    if password_hash in line or "(?)" in line:
                        line_queue.put("Your password got cracked! " + line)
                        break
                else:
                    line_queue.put(line)
            for line in p.stderr:
                if "yes" in radio4.value:
                    line_queue.put(line)
            spinner.delete()
        status.set_text("Done!")
        start_button.enable()
        
        
def get_hash_value(password, hash):
    if "MD5" in hash:
        hash_digest = hashlib.md5(password.encode()).hexdigest()
        return hash_digest
    elif "SHA2" in hash:
        hash_digest = hashlib.sha256(password.encode()).hexdigest()
        return hash_digest
    elif "bcrypt" in hash:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        return (password_hash, salt)
    



def callback_for_password_input(e):
    password = e.value
    strength = calc_password_strength(password)
    return strength



if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8080)