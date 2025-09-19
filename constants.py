from pathlib import Path

PATH = Path(__file__).resolve().parents[0]
DIRECTIONS = {"⬆️": "UP", "⬇️": "DOWN", "⬅️": "LEFT", "➡️": "RIGHT"}
COLORS = {
    "🟥": "RED", "🟩": "GREEN", "🟦": "BLUE", "🟨": "YELLOW",
    "⬜": "WHITE", "⬛": "BLACK", "🟧": "ORANGE", "🟪": "PURPLE"
}
PLAYER = "🤖"
ITEMS = {"🗝️": "KEY", "💣": "BOMB"}
VICTORY = "🏁"
NEGATION = "🚫"
THEN = "➤"
