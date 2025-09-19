from game import interactive_game_loop, load_level
from level_generation import generate_level
from utils import save_level, solve_level, solve_level_dfs

def main():

    mode = input("Choisissez le mode de jeu (1: Test de niveau, 2: Génération de niveau) : ").strip()
    if mode == "1":
        level, rules, action_rules, victory_rules, solution = load_level("test.json")
        interactive_game_loop(level, rules, action_rules, victory_rules)
    elif mode == "2":

        grid = [["⬜", "", "⬜", "", "⬜"],
                ["", "⬜", "", "⬜", ""],
                ["⬜", "", "⬜", "", "⬜"],
                ["", "⬜", "", "⬜", ""],
                ["⬜", "", "⬜", "", "⬜"]]
 
        level, solution, emoji_rules = generate_level(5, 5, grid)  # Génération d'un niveau aléatoire
        save_level(level, emoji_rules, solution, "test.json")  # Sauvegarde du niveau généré
    else:
        level, rules, action_rules, victory_rules, solution = load_level("niveau_genere.json")
        print(solve_level_dfs(level, rules, action_rules, victory_rules, level.start, [], set()))
        level, rules, action_rules, victory_rules, solution = load_level("niveau_genere.json")
        print(solve_level(level, rules, action_rules, victory_rules, level.start))
        return

    return 0

main()
