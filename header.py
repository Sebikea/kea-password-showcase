from nicegui import ui

@ui.page('/page_layout')
def page_layout():
    with ui.header(elevated=True).style('background-color: #CBC3E3').classes('items-left'):
        ui.link('Main', "/")
ui.link('show page with fancy layout', page_layout)