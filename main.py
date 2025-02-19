from fastapi import FastAPI
from nicegui import ui
import header
import os
import hashlib
import bcrypt
import subprocess
import threading
import queue
import time
import signal
import history
from password_chart import page_layout

from password_helpers import *
from pathlib import Path
app = FastAPI()

line_output_counter = 0
line_queue = queue.Queue()

MAXIMUM_CRACK_TIME = 120

path_to_wordlist = Path(os.getcwd() + "/wordlists/rockyou.txt")
path_to_logo = Path(os.getcwd() + "/assets/kea-logo-dk-web.jpg")
path_to_johnpot = Path(os.getcwd() + "/.pot")
path_to_johnrec = Path("/home/kali/.john/john.rec")
path_to_best64hc = Path(os.getcwd() + "/wordlists/hc64.rule")


@ui.page('/')
def main_page():

    def update_ui():

        # Check the queue and update the UI if new lines are available.
        while not line_queue.empty():
            global line_output_counter
            line_output_counter+=1

            #Clear the screen if we have too many output lines
            if line_output_counter >= 100:
                output_container.clear()
                line_output_counter = 0
          
            # Append each line as a new label inside the container.
            line = line_queue.get()
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
            advice_container = ui.column()
        right_card = ui.card().classes('w-max absolute right-2 mx-auto')

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
        with ui.row().classes('w-1/6 fixed left-2 bottom-2 border-2'):   
            ui.label("Useful resources about passwords").classes('font-bold')
            ui.link("Bitwarden best practices for passwords", "https://bitwarden.com/password-strength/#Password-Strength-Testing-Tool")
            ui.link("Test your e-mail against known breaches", "https://haveibeenpwned.com")

        #KEA logo and credits
        with ui.row().classes('w-1/6 fixed right-2 bottom-2 border-2'):
            ui.image(path_to_logo)
            ui.label("Credit: Dany (daka@kea.dk)")
            ui.label("Sebastian (sebi@kea.dk)")
        timer = ui.timer(interval=0.5, callback=update_ui)
        

    def break_password(password, hash, program, method):
        output_container.clear()
        advice_container.clear()
        global line_output_counter
        line_output_counter = 0
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

        #Spawn separate thread for cracking
        threading.Thread(target=start_cracking, args=(command, password_hash, password), daemon=True).start()


    def start_cracking(command, password_hash, password):
        start_time = time.time()
        cracked = False
        with middle_card:
            spinner = ui.spinner(size='lg').classes('fixed-center')

        #Start subprocess with cracking command, we can send signals for status and add it to our queue. The queue will get empited by the timer every .5 seconds
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, errors="backslashreplace")
        with left_card:
            stop_button = ui.button("Stop cracking",on_click=lambda: (kill_thread(p)))
        try:
            while True:
                    #Truncates the output if we dont want the full debug
                    t = p.stdout.readline()
                    if password_hash+":" in t or "(?)" in t:
                        line_queue.put("Your password got cracked! - " + t)
                        cracked = True
                    if "yes" in radio4.value:
                        line_queue.put(t)

                    if p.poll() == None:
                        if "john" in radio2.value: 
                            p.send_signal(signal.SIGUSR1)
                        if "hashcat" in radio2.value:
                            p.stdin.write("s")
                        time.sleep(1)
                    #Polls the subprocess if it still exists or not. Handles cleanup if its done
                    if p.poll() != None:
                        status.set_text("Done!")
                        spinner.delete()
                        start_button.enable()
                        stop_button.delete()
                        break
                    #Maximum cracktime checker, defined by the constant. Kills the subprocess 
                    timeout = int(time.time() - start_time)
                    print(timeout)
                    if timeout > MAXIMUM_CRACK_TIME:
                        kill_thread(p)
                        status.set_text("Failed...")
                        spinner.delete()
                        start_button.enable()
                        stop_button.delete()
                        line_queue.put(f"Sorry, I couldn't crack your password within timelimit, which is currently {MAXIMUM_CRACK_TIME} seconds.")
                        break

            #If there's anything remaining in the pipe after the process ends, print it out
            for line in p.stdout:
                line = line.encode('utf-8')
                line = line.decode('utf-8')
                if password_hash+":" in line or "(?)" in line:
                    cracked = True
                    line_queue.put("Your password got cracked! - " + line)
                if "yes" in radio4.value:
                    line_queue.put(line)
            if cracked:
                time_to_crack = int(time.time() - start_time)
                line_queue.put(f"It took {time_to_crack} seconds to crack your password.")
                history.insert_crack_result(password_hash, password, radio2.value + " - " + radio3.value, time_to_crack)
                if "no" in radio4.value:
                    with advice_container:
                        ui.separator()
                        ui.label("Follow these practices to increase your password security:").classes('font-bold')
                        with ui.column().classes('w-full border'):
                            with ui.card().classes('justify-left').style('background-color: #2E8B57'):
                                ui.label("Always use long passwords, with a mix of special characters, upper and lowercase letters and numbers.").classes('font-bold')
                            with ui.card().classes('justify-center').style('background-color: #228B22'):
                                ui.label("Never use the same password for multiple accounts.").classes('font-bold')
                            with ui.card().classes('justify-center').style('background-color: #008000'):
                                ui.label("Consider using a password manager, to help you generate long and random passwords.").classes('font-bold')
                            with ui.card().classes('justify-center').style('background-color: #006400'):  
                                ui.link("Have a look at the password chart for more information", "/password-chart").classes('font-bold text-blue')
            elif not cracked and "no" in radio4.value:
                with advice_container:
                        ui.separator()
                        ui.label("I couldn't crack your password with the current rules or wordlist.").classes('font-bold')
        except UnicodeDecodeError as e:
            print(e)
            with advice_container:
                ui.separator()
                ui.label("I couldn't crack your password with the current rules or wordlist.").classes('font-bold')
                    

        



def kill_thread(p):
    p.send_signal(signal.SIGKILL)
    line_queue.put("Process stopped prematurely")
       
        
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