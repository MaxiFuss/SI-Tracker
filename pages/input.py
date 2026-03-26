from shiny import ui, render, reactive
import json
from pathlib import Path
import datetime



data_path = Path(__file__).parent.parent / "data" / "spirits.json"

with open(data_path, "r", encoding="utf-8") as f:
    spirits_data = json.load(f)

SPIRITS = spirits_data["spirits"]

adversaries_path = Path(__file__).parent.parent / "data" / "adversaries.json"

with open(adversaries_path, "r", encoding="utf-8") as f:
    adversaries_data = json.load(f)

ADVERSARIES = adversaries_data["adversaries"]

games_path = Path(__file__).parent.parent / "data" / "games.json"

def save_game(new_game):
    try:
        with open(games_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = []

    data.append(new_game)

    with open(games_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def input_ui():
    return ui.nav_panel(
        "Input",

        ui.h3("Spiel erfassen"),

        ui.input_slider("n_players", "Anzahl Spieler:", value=2, min=1, max=6),
        ui.input_select(
            "adversary",
            "Adversary:",
            choices=ADVERSARIES
        ),
        ui.hr(),

        # Dynamische UI für Spieler
        ui.output_ui("player_inputs"),

        ui.hr(),

        ui.input_action_button("submit", "Spiel speichern"),

        ui.h4("Ergebnis:"),
        ui.output_text_verbatim("result"),

       

        ui.hr(),
            )

# -------------------
# Server
# -------------------
def input_server(input, output, session):

    # -------------------
    # Dynamische Spielerfelder
    # -------------------
    @output
    @render.ui
    def player_inputs():
        n = input.n_players()

        players = []

        for i in range(n):
            players.append(
                ui.card(
                    ui.h5(f"Spieler {i+1}"),

                    ui.input_text(f"name_{i}", "Name:", value=f"Spieler {i+1}"),

                    ui.input_select(
                        f"spirit_{i}",
                        "Geist:",
                        choices=SPIRITS
                                    )
                    )
                )
            

        return ui.TagList(*players)

    # -------------------
    # Ergebnis sammeln
    # -------------------
    data_store = reactive.Value(None)
    @reactive.Effect
    @reactive.event(input.submit)
    def _():
        n = input.n_players()

        players = []

        for i in range(n):
            player = {
                "name": input[f"name_{i}"](),
                "spirit": input[f"spirit_{i}"]()
            }
            players.append(player)

        game_data = {
            "adversary": input.adversary(),
            "players": players
        }

        save_game(game_data)
        data_store.set(game_data)

    # -------------------
    # Ausgabe anzeigen
    # -------------------
    @output
    @render.text
    def result():
        data = data_store.get()

        if not data:
            return "Noch keine Daten."

        text = f"Adversary: {data['adversary']}\n\n"
        text += "Spieler:\n"

        for p in data["players"]:
            text += f"- {p['name']} ({p['spirit']})\n"

        return text