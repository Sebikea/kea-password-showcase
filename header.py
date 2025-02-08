from nicegui import ui

@ui.page('/page_layout')
def page_layout():
    with ui.header(elevated=True).style('background-color: #CBC3E3').classes('items-left font-bold text-sm'):
        ui.link('Main', "/")
        ui.link("Password chart", "/password-chart")
        ui.link("Crack history", "/history")
ui.link('show page with fancy layout', page_layout)