from shiny import ui, render, reactive
from shiny.ui import TagList
from shiny.ui import update_navs

from shiny import ui



from shiny import ui

def landing_ui():
    return ui.nav_panel(
        "Startseite",
        ui.div(
            ui.h2("Willkommen im Monitoring Dashboard"),
            ui.p("Dieses Dashboard bietet Ihnen verschiedene Analysewerkzeuge:"),

            ui.div(style="margin-top: 2rem;"),  # ≈ 32px Abstand nach oben

    # Sensorenfrequenz
            ui.h4("Page1:"),
            ui.p("Hier  auf ihre aktuelle und historische Frequenz überprüft werden."),
            ui.input_action_button("to_input", "Zu input", class_="btn btn-primary"),

            ui.div(style="margin-top: 2rem;"),  # ≈ 32px Abstand nach oben

        )
    )



def landing_server(input, output, session):
    @reactive.Effect
    @reactive.event(input.to_input)
    def go_to_input():
        update_navs("page", "Input")