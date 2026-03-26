from shiny import App, ui
from pages.landing import landing_ui, landing_server
from pages.input import input_ui, input_server

from pathlib import Path

www_dir = Path(__file__).parent / "www"

# Logo top right (fixed position)
logo_div = ui.tags.div(
    ui.tags.img(src="/logo.png", height="100px"),
    style="""
        position: fixed;
        top: 10px;
        right: 20px;
        z-index: 1000;
    """
)

# app_ui defines the entire user interface of the Shiny app.
app_ui = ui.page_navbar(
    landing_ui(),
    input_ui(),
    title="Dashboard",
    id="page",
)

# server registers all reactive callbacks and application logic.
def server(input, output, session):
    landing_server(input, output, session)
    input_server(input,output,session)

app = App(ui.TagList(logo_div, app_ui), server, static_assets=www_dir)