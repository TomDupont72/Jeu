from typing import List, Tuple
import random
from constants import COLORS, DIRECTIONS, ITEMS
from game import Level
from utils import solve_level, compile_rules

def generate_tile_condition_rule() -> str:
    tiles = list(COLORS.keys())
    tile_emojis = random.sample(tiles, k=random.randint(1, 3))
    return ''.join(tile_emojis)

def generate_direction_condition_rule() -> str:
    directions = list(DIRECTIONS.keys())
    dir_emojis = random.sample(directions, k=random.randint(1, 2))
    return ''.join(dir_emojis)

def generate_player_condition_rule() -> str:
    player_conditions = []
    if random.random() < 0.5:  # 50% chance to include color
        colors = list(COLORS.keys())
        color_emojis = random.sample(colors, k=random.randint(1, 2))
        player_conditions.append(''.join(color_emojis))
    if random.random() < 0.5:  # 50% chance to include direction
        directions = list(DIRECTIONS.keys())
        dir_emojis = random.sample(directions, k=random.randint(1, 2))
        player_conditions.append(''.join(dir_emojis))
    if random.random() < 0.5 or player_conditions == []:  # 50% chance to include item
        items = list(ITEMS.keys())
        item_emojis = random.sample(items, k=random.randint(1, 2))
        player_conditions.append(''.join(item_emojis))
    
    return '🤖' + ''.join(player_conditions)

def generate_random_rules(n: int) -> List[str]:
    rule_set = []

    for _ in range(n):
        rule_type = random.choice(["A", "B", "C"])  # Type A (⬆️🟥) ou B (🟦⬅️➡️)
        negation = random.choice([True, False])
        if rule_type == "A":
            if random.random() < 0.5:  # 50% de chance d'avoir une direction
                rule = generate_direction_condition_rule()
            else:
                rule = generate_tile_condition_rule()
        elif rule_type == "B":
            rule = generate_player_condition_rule()
        else:
            if random.random() < 1/3:
                rule = f"🏁{generate_tile_condition_rule()}"
            elif random.random() < 1/2:
                rule = f"🏁{generate_direction_condition_rule()}"
            else:
                rule = f"🏁{generate_player_condition_rule()}"

        if rule_type != "C":
            rule += "➤"
            rule_type = random.choice(["A", "B"])
            if rule_type == "A":
                rule += generate_direction_condition_rule()
            else:
                rule += generate_player_condition_rule()

        if negation:
            rule = "🚫" + rule
        rule_set.append(rule)

    return rule_set

def generate_random_grid(tiles: List[str], grid: List[List[str]]) -> List[List[str]]:
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == "":
                grid[i][j] = random.choice(tiles)
    return grid

def generate_valid_level(tiles: List[str], rules: List[str], action_rules: List[str], victory_rules: List[str], grid: List[List[str]], max_attempts: int = 10) -> Tuple[Level, List[str]]:
    for _ in range(max_attempts):
        grid = generate_random_grid(tiles, grid)
        start = (0, 0)
        level = Level(grid, start)
        path = solve_level(level, rules, action_rules, victory_rules, start)

        if path:
            return level, path  # Valid level found

    raise ValueError("Impossible de générer un niveau faisable avec ces règles.")

def generate_level(num_rules: int, min_length_solution: int, grid: List[List[str]]) -> Tuple[Level, List[str]]:
    while True:
        try:
            emoji_rules = generate_random_rules(num_rules)
            
            rules, action_rules, victory_rules = compile_rules(emoji_rules)

            level, solution = generate_valid_level(list(COLORS.keys()), rules, action_rules, victory_rules, grid)
            if len(solution) >= min_length_solution and len(set(solution)) >= 3:
                return level, solution, emoji_rules
        except ValueError as e:
            print(f"Erreur lors de la génération du niveau : {e}. Réessayer...")
