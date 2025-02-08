from nicegui import ui
import header
import sqlite3
from pathlib import Path
import os

DB_FILENAME = "history.db"
path_to_logo = Path(os.getcwd() + "/assets/kea-logo-dk-web.jpg")

def init_db():

    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS cracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_hash TEXT NOT NULL,
            cracked_password TEXT,
            tool_used TEXT,
            time_to_crack TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_crack_result(target_hash, cracked_password, tool_used, time_to_crack):
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO cracks (target_hash, cracked_password, tool_used, time_to_crack)
        VALUES (?, ?, ?, ?)
    ''', (target_hash, cracked_password, tool_used, time_to_crack))
    conn.commit()
    conn.close()

def get_all_crack_results():
    conn = sqlite3.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute('SELECT * FROM cracks ORDER BY timestamp ASC')
    results = cur.fetchall()
    conn.close()
    return results


init_db()

@ui.page('/history')
def page_layout():
    header.page_layout()
    ui.page_title("KEA Password Showcase")
    middle_card = ui.card().classes('w-2/3 absolute left-0 right-0 mx-auto')
    with middle_card:
        with ui.grid(columns='auto auto auto auto auto auto').classes('w-full gap-0'):
            ui.label("id").classes('font-bold border p-1')
            ui.label("hash").classes('font-bold border p-1')
            ui.label("password").classes('font-bold border p-1')
            ui.label("tool used").classes('font-bold border p-1')
            ui.label("time to crack (in seconds)").classes('font-bold border p-1')
            ui.label("time").classes('font-bold border p-1')
            for r in get_all_crack_results():
                ui.label(r[0]).classes('border p-1')
                ui.label(r[1]).classes('border p-1')
                ui.label(r[2]).classes('border p-1')
                ui.label(r[3]).classes('border p-1')
                ui.label(r[4]).classes('border p-1')
                ui.label(r[5]).classes('border p-1')





    #External resources
    with ui.row().classes('w-1/6 left-2 bottom-2 border-2 fixed'):   
        ui.label("Useful resources about passwords").classes('font-bold')
        ui.link("Bitwarden best practices for passwords", "https://bitwarden.com/password-strength/#Password-Strength-Testing-Tool")
        ui.link("Test your e-mail against known breaches", "https://haveibeenpwned.com")

    #KEA logo and credits
    with ui.row().classes('w-22 right-2 bottom-2 border-2 fixed'):
        ui.image(path_to_logo)
        ui.label("Credit: Dany (daka@kea.dk)")
        ui.label("Sebastian (sebi@kea.dk)")
    