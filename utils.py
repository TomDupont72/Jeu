from typing import List, Dict, Callable, Tuple
import regex
from collections import deque
import json
from constants import COLORS, DIRECTIONS, ITEMS, THEN, NEGATION, VICTORY, PLAYER
import time 

def add_to_result(tokens: List[str], result: Dict[str, List[Dict]], type: str, name: str, container: Dict, context: str):
    if type == "player_condition":
        if result[context] == {}:
            result[context] = {"type": type, name: [container[tokens[1]]]}
        else:
            if name not in result[context]:
                result[context][name] = [container[tokens[1]]]
            else:
                result[context][name].append(container[tokens[1]])
    else:
        if result[context] == {}:
            result[context] = {"type": type, name: [container[tokens[0]]]}
        else:
            if name not in result[context]:
                result[context][name] = [container[tokens[0]]]
            else:
                result[context][name].append(container[tokens[0]])
    

# Tokenizer using extended grapheme clusters
def tokenize(rule: str) -> List[str]:
    return regex.findall(r"\X", rule)

def parse_recursive(tokens: List[str], context: str = "if", result: Dict[str, List[Dict]] = None) -> Dict:
    if result is None:
        result = {"win": False, "negation": False, "if": {}, "then": {}}
    
    if len(tokens) == 0:
        return result
    elif tokens[0] == THEN:
        return parse_recursive(tokens[1:], context="then", result=result)
    elif tokens[0] == NEGATION:
        result["negation"] = True
        return parse_recursive(tokens[1:], context=context, result=result)
    elif tokens[0] == VICTORY:
        result["win"] = True
        return parse_recursive(tokens[1:], context=context, result=result)
    elif tokens[0] == PLAYER:
        if len(tokens) == 1:
            return result
        if tokens[1] in COLORS:
            add_to_result(tokens, result, "player_condition", "colors", COLORS, context)
            return parse_recursive([tokens[0]] + tokens[2:], context=context, result=result)
        elif tokens[1] in DIRECTIONS:
            add_to_result(tokens, result, "player_condition", "directions", DIRECTIONS, context)
            return parse_recursive([tokens[0]] + tokens[2:], context=context, result=result)
        elif tokens[1] in ITEMS:
            add_to_result(tokens, result, "player_condition", "items", ITEMS, context)
            return parse_recursive([tokens[0]] + tokens[2:], context=context, result=result)
        elif tokens[1] == THEN:
            return parse_recursive(tokens[2:], context="then", result=result)
    elif tokens[0] in COLORS:
        add_to_result(tokens, result, "tile_condition", "colors", COLORS, context)
        return parse_recursive(tokens[1:], context=context, result=result)
    elif tokens[0] in DIRECTIONS:
        add_to_result(tokens, result, "direction_condition", "directions", DIRECTIONS, context)
        return parse_recursive(tokens[1:], context=context, result=result)

    return result

def compile_rule(rule: Dict) -> Callable[[str, str], bool]:
    def compiled_rule(level, direction: str, tile: str, rules: List[Callable[[str, str], bool]]) -> bool:
        test_if = True
        if rule["if"]["type"] == "tile_condition":
            test_if = test_if and tile in rule["if"]["colors"]
        elif rule["if"]["type"] == "direction_condition":
            test_if = test_if and direction in rule["if"]["directions"]
        elif rule["if"]["type"] == "player_condition":
            if "colors" in rule["if"]:
                test_if = test_if and level.player_color in rule["if"]["colors"]
            if "directions" in rule["if"]:
                test_if = test_if and direction in rule["if"]["directions"]
            if "items" in rule["if"]:
                test_if = test_if and any(item in level.player_inventory for item in rule["if"]["items"])

        if rule["negation"]:
            test_if = not test_if

        if rule["then"] == {}:
            return test_if

        if rule["then"]["type"] == "direction_condition":
            if not test_if and direction in rule["then"]["directions"]:
                return False
            else:
                return True
        elif rule["then"]["type"] == "player_condition":
            if test_if:
                level.player_inventory = level.player_inventory + rule["then"].get("items", [])
                for dir in rule["then"].get("directions", []):
                    move_player_if_allowed(level, dir, rules)
                level.player_color = rule["then"].get("colors", [level.player_color])[0]
            return True

    return compiled_rule

def get_allowed_moves(position: Tuple[int, int], rules: List[Callable[[str, str], bool]], level) -> List[str]:
    possible_directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    tile = COLORS.get(level.get_tile(position), None)
    allowed = []

    for direction in possible_directions:
        if tile is None:
            continue
        if all(rule(level, direction, tile, rules) for rule in rules):
            # Check if move is within bounds
            dx, dy = {
                "UP": (0, -1),
                "DOWN": (0, 1),
                "LEFT": (-1, 0),
                "RIGHT": (1, 0)
            }[direction]
            new_x, new_y = position[0] + dx, position[1] + dy
            if 0 <= new_y < len(level.grid) and 0 <= new_x < len(level.grid[0]):
                allowed.append(direction)

    return allowed

def move_player_if_allowed(level, direction: str, rules: List[Callable[[str, str], bool]]) -> bool:
    allowed = get_allowed_moves(level.player_pos, rules, level)
    if direction in allowed:
        level.move_player(direction)
        return True
    return False

def print_level(level):
    output = ""
    for y, row in enumerate(level.grid):
        for x, tile in enumerate(row):
            if (x, y) == level.player_pos:
                output += "🤖"  # joueur
            else:
                output += tile
        output += "\n"
    print(output)

def solve_level(level, rules, action_rules, victory_rules, start_pos, max_length=15):
    
    # État initial
    start_state = (
        start_pos,
        level.player_color,
        tuple(sorted(level.player_inventory))
    )
    
    # File BFS (position, état du level, chemin)
    queue = deque()
    queue.append((start_pos, level.player_color, tuple(level.player_inventory), []))
    
    # Visited pour éviter les boucles
    visited = set([start_state])
    
    while queue:
        pos, player_color, inventory, path = queue.popleft()

        if len(path) > max_length:
            return None
        
        # Mettre à jour le level temporaire
        level.player_pos = pos
        level.player_color = player_color
        level.player_inventory = list(inventory)
        
        # Vérif victoire
        if path and all(victory(level, path[-1], level.get_tile(pos), rules) for victory in victory_rules):
            return path  # ✅ BFS : premier trouvé = plus court
        
        # Moves possibles
        for direction in get_allowed_moves(pos, rules, level):
            dx, dy = {
                "UP": (0, -1),
                "DOWN": (0, 1),
                "LEFT": (-1, 0),
                "RIGHT": (1, 0)
            }[direction]
            new_pos = (pos[0] + dx, pos[1] + dy)
            
            # Sauvegarder avant d'appliquer effets
            tmp_color = level.player_color
            tmp_inv = list(level.player_inventory)
            
            # Appliquer règles d’action
            for action_rule in action_rules:
                action_rule(level, direction, level.get_tile(pos), rules)
            
            # Nouvel état
            new_state = (
                new_pos,
                level.player_color,
                tuple(sorted(level.player_inventory))
            )
            
            # Si jamais vu → ajouter à la queue
            if new_state not in visited:
                visited.add(new_state)
                queue.append((
                    new_pos,
                    level.player_color,
                    tuple(level.player_inventory),
                    path + [direction]
                ))
            
            # Restaurer état (pas besoin car BFS garde tout en queue)
            level.player_color = tmp_color
            level.player_inventory = tmp_inv
    
    return None  # Pas de solution

def solve_level_dfs(level, rules, action_rules, victory_rules, position, path, visited):
    if len(path) > 50:
        return None
    # Créer un état unique (position + couleur + inventaire)
    state = (
        position,
        level.player_color,
        tuple(sorted(level.player_inventory))
    )

    # Victoire ?
    if path and all(victory(level, path[-1], level.get_tile(level.player_pos), rules) for victory in victory_rules):
        return path

    # Boucle infinie : on a déjà vu EXACTEMENT cet état
    if state in visited:
        return None
    visited.add(state)

    # Essayer tous les moves possibles
    for direction in get_allowed_moves(position, rules, level):
        dx, dy = {
                "UP": (0, -1),
                "DOWN": (0, 1),
                "LEFT": (-1, 0),
                "RIGHT": (1, 0)
            }[direction]
        new_pos = (position[0] + dx, position[1] + dy)

        # Sauvegarder l'état avant d'appliquer les action_rules
        saved_color = level.player_color
        saved_inventory = list(level.player_inventory)
        saved_pos = level.player_pos

        # Appliquer les effets de l'action
        for action_rule in action_rules:
            action_rule(level, direction, level.get_tile(level.player_pos), rules)

        # Explorer en profondeur
        result = solve_level(level, rules, action_rules, victory_rules, new_pos, path + [direction], visited)

        if result:  # solution trouvée
            return result

        # Restaurer l'état (backtrack)
        level.player_color = saved_color
        level.player_inventory = saved_inventory
        level.player_pos = saved_pos

    return None


# Fonction pour sauvegarder un niveau dans un fichier .json
def save_level(level, rules: List[str], solution: List[str], filename: str):
    data = {
        "grid": level.grid,
        "start": level.start,
        "emoji_rules": rules,
        "solution": solution
    }
    with open(f"C:\\Users\\FlowUP\\Desktop\\Jeu\\Levels\\{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def compile_rules(emoji_rules: List[str]):
    parsed_rules = []
    for rule in emoji_rules:
        tokens = tokenize(rule)
        parsed = parse_recursive(tokens)
        parsed_rules.append(parsed)

    rules = [compile_rule(rule) for rule in parsed_rules if not rule["win"] and rule["then"]["type"] != "player_condition"]
    action_rules = [compile_rule(rule) for rule in parsed_rules if not rule["win"] and rule["then"]["type"] == "player_condition"]
    victory_rules = [compile_rule(rule) for rule in parsed_rules if rule["win"]]

    return rules, action_rules, victory_rules