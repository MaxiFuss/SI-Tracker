from shiny import ui, render, reactive
import json
from pathlib import Path
import datetime



data_path = Path(__file__).parent.parent / "data" / "spirits.json"

with open(data_path, "r", encoding="utf-8") as f:
    spirits_data = json.load(f)

SPIRITS = [s["name"] for s in spirits_data["spirits"]]

SPIRIT_ASPECTS = {
    s["name"]: s["aspects"]
    for s in spirits_data["spirits"]
}

adversaries_path = Path(__file__).parent.parent / "data" / "adversaries.json"

with open(adversaries_path, "r", encoding="utf-8") as f:
    adversaries_data = json.load(f)

ADVERSARIES = adversaries_data["adversaries"]

games_path = Path(__file__).parent.parent / "data" / "games.json"

def save_game(new_game):
    try:
        with open(games_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                data = json.loads(content)
            else:
                data = []
    except:
        data = []

    data.append(new_game)

    with open(games_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def input_ui():
    return ui.nav_panel(
        "Input",

        ui.layout_columns(

            ui.input_slider(
                "n_players",
                "Anzahl Spieler:",
                value=2,
                min=1,
                max=6,
                ticks=True
            ),

            ui.input_select(
                "adversary",
                "Adversary:",
                choices=ADVERSARIES
            ),
            ui.input_slider(
                "adversary_level",
                "Adversary Level:",
                min=1,
                max=6,
                value=6,
                ticks=True
            ),
        ),
        ui.layout_columns(
            ui.input_checkbox(
                "use_support_adversary",
                "Supporting Adversary aktivieren?"
            ),

            
            ui.output_ui("support_adversary_ui"),
        ),

        ui.layout_columns(

            ui.input_checkbox("won", "Gewonnen?"),

            ui.input_checkbox("blight_card_flipped", "Ödnis-Karte umgedreht?"),

            ui.input_numeric(
                "invader_cards",
                "Invasorenkarten übrig:",
                value=0,
                min=0
            ),

            ui.input_numeric(
                "dahan",
                "Dahan auf der Insel:",
                value=0,
                min=0
            ),

            ui.input_numeric(
                "blight",
                "Ödnis auf der Insel:",
                value=0,
                min=0
            ),
        ),
        
        ui.hr(),

        # Dynamische UI für Spieler
        ui.output_ui("player_inputs"),

        ui.hr(),

        ui.input_action_button("submit", "Spiel speichern"),

        ui.h4("Ergebnis:"),
        ui.output_text_verbatim("result"),
    )
#Score
def calculate_score(game):
    difficulty = game["adversary_level"]
    won = game["won"]

    invader_cards = game["invader_cards_left"]
    dahan = game["dahan"]
    blight = game["blight"]
    n_players = len(game["players"])

    # -----------------------
    # Base Score
    # -----------------------
    if won:
        score = 5 * difficulty + 10 + 2 * invader_cards
    else:
        score = 2 * difficulty + invader_cards

    # -----------------------
    # Board state modifier
    # -----------------------
    score += (dahan // n_players)   # +1 per X living Dahan
    score -= (blight // n_players)  # -1 per X Blight

    return score

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

                    ui.layout_columns(

                        ui.input_text(
                            f"name_{i}",
                            "Name:",
                            value=f"Spieler {i+1}"
                        ),

                        ui.input_select(
                            f"spirit_{i}",
                            "Geist:",
                            choices=SPIRITS
                        ),
                    ),

                    # Platzhalter für Aspekte
                    ui.output_ui(f"aspect_ui_{i}")
                )
            )
            

        return ui.TagList(*players)
    for i in range(6):  # max Spielerzahl
        def make_aspect_ui(i):
            @output(id=f"aspect_ui_{i}")
            @render.ui
            def _():
                spirit = input[f"spirit_{i}"]()

                if spirit is None:
                    return None

                aspects = SPIRIT_ASPECTS.get(spirit, [])

                if not aspects:
                    return None

                return ui.input_select(
                    f"aspect_{i}",
                    "Aspekt:",
                    choices=aspects
                )

        make_aspect_ui(i)
    @output
    @render.ui
    def support_adversary_ui():

        if not input.use_support_adversary():
            return None

        return ui.layout_columns(

            ui.input_select(
                "support_adversary",
                "Supporting Adversary:",
                choices=ADVERSARIES
            ),
            ui.input_slider(
                "support_adversary_level",
                "Support Level:",
                min=1,
                max=6,
                value=6,
                ticks=True
            ),
        )


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
            spirit = input[f"spirit_{i}"]()
            aspects = SPIRIT_ASPECTS.get(spirit, [])

            player = {
                "name": input[f"name_{i}"](),
                "spirit": spirit
            }

            if aspects:
                aspect_value = input[f"aspect_{i}"]()
                if aspect_value:
                    player["aspect"] = aspect_value
            players.append(player)


        game_data = {
            "adversary": input.adversary(),
            "adversary_level": input.adversary_level(),
            "won": input.won(),
            "blight_card_flipped": input.blight_card_flipped(),
            "invader_cards_left": input.invader_cards(),
            "dahan": input.dahan(),
            "blight": input.blight(),
            "players": players,
            "timestamp": datetime.datetime.now().isoformat()
        }

        if input.use_support_adversary():
            game_data["support_adversary"] = input.support_adversary()
            game_data["support_adversary_level"] = input.support_adversary_level()


        game_data["score"] = calculate_score(game_data)
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

        text = f"Adversary: {data['adversary']}(Level: {data['adversary_level']})\n"
        if data.get("support_adversary"):
            text += f"Support: {data['support_adversary']} (Level: {data['support_adversary_level']})\n"
        text += f"Gewonnen: {'Ja' if data['won'] else 'Nein'}\n"
        text += f"Ödnis-Karte umgedreht: {'Ja' if data['blight_card_flipped'] else 'Nein'}\n"
        text += f"Invasorenkarten übrig: {data['invader_cards_left']}\n"
        text += f"Dahan: {data['dahan']}\n"
        text += f"Ödnis: {data['blight']}\n\n"
        text += "Spieler:\n"

        for p in data["players"]:
            if p.get("aspect"):
                text += f"- {p['name']} ({p['spirit']} - {p['aspect']})\n"
            else:
                text += f"- {p['name']} ({p['spirit']})\n"
        text += f"Score: {data['score']}\n\n"
        return text