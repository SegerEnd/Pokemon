import os
import random
import time

from config import TextStyles
from map import display_map, create_maps
from player import Player, initialize_new_player, load_existing_player
from pokemon import encounter_pokemon, get_wild_grass_pokemon_list, save_wild_grass_pokemon_list

# Create a new player
player = Player()

def clear_screen():
    """Fake clear the screen"""
    is_pycharm = "PYCHARM_HOSTED" in os.environ
    if is_pycharm:
        print("\n" * 100)
    else:
        os.system('cls' if os.name == 'nt' else 'clear')


def handle_move_input():
    """Handle player move input and game interactions."""
    display_map(player)
    move = input("Move to: (w/a/s/d) (b)ag (q)uit (m)enu (h)elp ").strip().lower()

    if not ',' in move:  # If input is not a coordinate like 1,1, just take the first character
        move = move[0] if len(move) > 0 else move

    print("\n" * 2)

    return move


def execute_move_action(move):
    """Perform actions based on the player's move."""
    if move == 'q':
        quit_game()
        return False
    elif move == 'm':
        clear_screen()
        return main_menu()
    elif move == 'b':
        player.show_bag()
    elif move == 'e':
        player.interact_if_possible(player.get_position())
    elif move == 'p':
        player.plant_a_seed()
    elif move == 'h':
        clear_screen()
        player.show_help_menu()
    elif player.move(move):
        if player.get_current_map_name() == 'beach':
            handle_water_encounter()
        else:
            handle_grass_encounter()

    return True

def random_encounter():
    """Randomly determine if a wild Pokémon encounter occurs in the grass."""
    encounter_chance = random.randint(1, 100)
    return encounter_chance <= 30  # 30% chance to encounter a Pokémon

def handle_grass_encounter():
    """Check for grass encounter and trigger Pokémon battle if applicable."""
    if player.is_grass() and random_encounter():
        clear_screen()
        time.sleep(0.4)
        encounter_pokemon(player, get_wild_grass_pokemon_list())

def handle_water_encounter():
    """Check for water encounter and trigger Pokémon battle if applicable."""
    if player.is_water() and random_encounter():
        clear_screen()
        time.sleep(0.4)
        encounter_pokemon(player, get_wild_grass_pokemon_list(), 'water')

def quit_game():
    """Save the game and quit."""
    clear_screen()
    print("Thanks for playing, Goodbye!")
    save_wild_grass_pokemon_list()
    player.save()


def game_loop():
    """Main game loop that continuously checks for player input and actions."""
    game_session = True
    while game_session:
        move = handle_move_input()
        game_session = execute_move_action(move)

def main_menu():
    """Main menu for the game with 3 different functionalities."""
    print(f"\n{TextStyles.blue}{TextStyles.bold}Main Menu{TextStyles.reset}")
    print("1/(S)ave game")
    print("2/(N)ew game")
    print("3/(L)oad existing game")
    print("4/(G)Generate new map")
    print("5/(H)elp, instructions")
    print("6/(Q)uit game")
    print("7/(B)ack continue playing\n")

    choice = input("Enter your choice: ").strip().lower()
    try:
        if choice.isdigit(): # If the input is a number, convert it to an integer
            choice = int(choice)
        else:
            choice = choice[0] # get the first character of the input
    except (ValueError, IndexError):
        print("Please enter a valid choice.")
        return main_menu()

    if choice in [1, 's']:
        player.save()
        return True
    elif choice in [2, 'n']:
        initialize_new_player(player)
    elif choice in [3, 'l']:
        load_existing_player(player)
    elif choice in [4, 'g']:
        create_maps(player)
        return True
    elif choice in [5, 'h']:
        clear_screen()
        player.show_help_menu()
        return True
    elif choice in [6, 'q']:
        quit_game()
        return False
    elif choice in [7, 'b', 'c']:
        return True
    else:
        print("Invalid choice. Please try again.")
        return main_menu()

    create_maps(player) # Generate new maps for the new game

    return True

def main():
    """Main function that starts the game."""
    if player.is_first_time_playing():
        print("\nIt looks like you're playing for the first time!")
        initialize_new_player(player)
    else:
        load_existing_player(player)

    create_maps(player)

    print("\nYou can move using W/A/S/D. B to open your bag, H for help, M to open the main menu. and Q to quit the game.\n")

    game_loop()

# Start the game
if __name__ == "__main__":
    main()