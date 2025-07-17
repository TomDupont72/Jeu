from typing import List, Tuple, Callable
from utils import move_player_if_allowed, print_level
import json
from utils import compile_rules

class Level:
    def __init__(self, grid: List[List[str]], start: Tuple[int]):
        self.grid = grid
        self.start = start
        self.player_color = "WHITE"
        self.player_inventory = []
        self.player_pos = start

    def get_tile(self, position: Tuple[int, int]) -> str:
        x, y = position
        if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
            return self.grid[y][x]
        return None  # Out of bounds

    def move_player(self, direction: str) -> bool:
        dx, dy = {
            "UP": (0, -1),
            "DOWN": (0, 1),
            "LEFT": (-1, 0),
            "RIGHT": (1, 0)
        }[direction]

        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        new_pos = (new_x, new_y)

        if 0 <= new_y < len(self.grid) and 0 <= new_x < len(self.grid[0]):
            self.player_pos = new_pos
            return True
        return False  # Invalid move

def interactive_game_loop(level: Level, rules: List[Callable[[str, str], bool]], action_rules: List[Callable[[str, str], bool]], victory_rules: List[Callable[[str, str], bool]]):
    print("Bienvenue dans le test de niveau !")
    print("Commandes : UP / DOWN / LEFT / RIGHT / QUIT")
    print_level(level)

    while True:
        cmd = input("Déplacement ? ").strip().upper()
        if cmd == "QUIT":
            print("Fin de la partie.")
            break
        elif cmd in ["UP", "DOWN", "LEFT", "RIGHT"]:
            moved = move_player_if_allowed(level, cmd, rules)
            if moved:
                print(f"Action : {cmd} → {'✔️'}")
                print_level(level)
                # Appliquer les règles d'action
                for action_rule in action_rules:
                    action_rule(level, cmd, level.get_tile(level.player_pos), rules)
                    if all(rule(level, cmd, level.get_tile(level.player_pos), rules) for rule in victory_rules):
                        
                        print("🎉 Bravo, vous avez gagné !")
                        return 0
            else:
                print(f"Action : {cmd} → {'❌'}")
                print_level(level)
            
        else:
            print("Commande invalide. Essayez : UP, DOWN, LEFT, RIGHT, QUIT.")

# Fonction pour lire un niveau depuis un fichier .json
def load_level(filename: str) -> Tuple:
    with open(f"C:\\Users\\FlowUP\\Desktop\\Jeu\\Levels\\{filename}", "r", encoding="utf-8") as f:
        data = json.load(f)
    grid = data["grid"]
    start = tuple(data["start"])
    emoji_rules = data["emoji_rules"]

    rules, action_rules, victory_rules = compile_rules(emoji_rules)

    solution = data["solution"]
    level = Level(grid, start)
    
    print(emoji_rules)

    return level, rules, action_rules, victory_rules, solution