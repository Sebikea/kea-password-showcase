from nicegui import ui
import header
import os
from pathlib import Path

path_to_chart = Path(os.getcwd() + "/assets/password-chart.png")
path_to_logo = Path(os.getcwd() + "/assets/kea-logo-dk-web.jpg")

@ui.page('/password-chart')
def page_layout():
    header.page_layout()
    middle_card = ui.card().classes('w-1/2 absolute left-0 right-0 mx-auto')
    with middle_card:
        ui.image(path_to_chart)
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
    