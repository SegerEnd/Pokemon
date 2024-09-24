import json
import os
import random
import time
from cgitb import reset
from time import sleep

from config import COLLISION_OBJECTS, INTERACTION_OBJECTS, TextStyles, ITEM_EMOJIS, GROWABLE_BERRIES, WATER_OBJECTS, \
    GRASS_OBJECTS, POKEBALLS
from map import plant_seed, generate_map
from pokemon import type_emoji, fetch_random_pokemon
from shop import show_pokemart_menu, show_pokecenter_menu, show_professor_house_menu


class Player:
    # Skin options for the player
    skins = {
        "🧍": "Person",
        "🧍‍♀️": "Girl",
        "🧍‍♂️": "Boy",
    }

    player_info = {}

    maps = {}

    consumed_pinap_berry = False

    def reset_info(self):
        """Reset the player's information to default values."""
        self.player_info = {
            "name": "",
            "skin": "🧍",
            "current_map": "grassland",
            "position": [1, 1],
            "coins": 0,
            "shiny_rate": 100,
            "inventory": {
                "Poké Balls": 5, # Start the journey with 5 normal Poké Balls
            },
            "pokemon": []
        }

    def __init__(self):
        self.reset_info() # Initialize the player's information with default values


    def get_maps(self):
        """Get the full dictionary of maps."""
        return self.maps

    def get_current_map(self):
        """Get the current map the player is on."""
        try:
            return self.maps[self.get_current_map_name()]
        except KeyError:
            print("The current map doesn't exist.")
            self.switch_map("grassland")
            return self.maps["grassland"]

    def get_current_map_name(self):
        """Get the name of the current map the player is on."""
        return self.player_info["current_map"]

    def set_map(self, name, map):
        """Place a map in the dictionary of maps."""
        try:
            self.maps[name] = map
        except KeyError:
            print("An error occurred while trying to set the map.")

    def switch_map(self, map_name):
        """Switch the player to a different map."""
        if map_name not in self.maps:
            # generate the map if it doesn't exist
            self.set_map(map_name, generate_map(7, 20, map_name, 0.4, self))
            self.player_info["current_map"] = map_name
            return
        self.player_info["current_map"] = map_name

    def add_pokemon_to_bag(self, pokemon):
        """Add a Pokémon list to the player's information."""
        self.player_info["pokemon"].append(pokemon)

    def choose_skin(self):
        print("Choose a skin for your player:")
        for number, (skin, name) in enumerate(self.skins.items()):
            print(f"{number + 1}. {skin} - {name}")
        choice = input("Enter the number of the skin you want: ")
        try:
            choice = int(choice)
            if choice < 1 or choice > len(self.skins):
                raise ValueError()
            skin = list(self.skins.keys())[choice - 1]
        except ValueError:
            print("\nInvalid choice, please choose a valid skin.\n")
            return self.choose_skin()
        self.player_info["skin"] = skin

    def get_info(self):
        """Get the player's information."""
        return self.player_info

    def set_info(self, info):
        """Set the player's information."""
        self.player_info.update(info)

    def get_inventory_item(self, item):
        """Get the quantity of an item from the player's inventory."""
        return self.player_info["inventory"].get(item, 0)

    def set_inventory_item(self, item, quantity, operation="add"):
        """Set the quantity of an item in the player's inventory."""
        if item not in self.player_info["inventory"]:
            self.player_info["inventory"][item] = quantity
        else:
            if operation in ["add", "+"]:
                self.player_info["inventory"][item] += quantity
            elif operation in ["subtract", "-"]:
                self.player_info["inventory"][item] -= quantity

            if self.player_info["inventory"][item] < 0:
                self.player_info["inventory"][item] = 0

    def has_all_pokemon(self):
        """Check if the player has caught all the Pokémon."""
        # Check by the id of the Pokémon if all 151 Pokémon are in the player's pokemon list
        if len(self.player_info['pokemon']) < 151: # The player hasn't even caught 151 Pokémon so they can't have all
            return False
        return all(pokemon['id'] in [monster['id'] for monster in self.player_info['pokemon']] for pokemon in range(1, 151))

    def get_shiny_rate(self):
        """Get the shiny rate of the player."""
        return self.player_info["shiny_rate"]

    def reset_shiny_rate(self):
        """Reset the shiny rate of the player."""
        self.player_info["shiny_rate"] = 100

    def increase_shiny_rate(self):
        """Increase the shiny rate of the player. For example when the player uses a pinap berry for the next encounter."""
        self.player_info["shiny_rate"] -= 25

        if self.player_info["shiny_rate"] < 45:
            self.player_info["shiny_rate"] = 45 # Prevent too easy shiny encounters

    def decrease_shiny_rate(self):
        """Decrease the shiny rate of the player."""
        self.player_info["shiny_rate"] += 5 # Slowly increase the shiny rate back to 100

        if self.player_info["shiny_rate"] >= 100:
            self.reset_shiny_rate()

    def get_coins(self):
        """Get the number of coins the player has."""
        return self.player_info["coins"]

    def set_coins(self, amount, operation="add"):
        """Add or subtract coins from the player's wallet."""
        if operation in ["add", "+"]:
            self.player_info["coins"] += amount
        elif operation in ["subtract", "-"]:
            self.player_info["coins"] -= amount

        if self.player_info["coins"] < 0:
            self.player_info["coins"] = 0 # Prevent negative value

    def set_name(self, name):
        """Set the player's name. And check if the name already exists in the saves folder."""
        # Check if the name already exists in the saves folder
        if os.path.exists(f"saves/player_{name.lower()}.json"):
            # Load the player's information from the saved file
            print(f"Your name already exists in the saves folder, loading your previous game...")
            self.load(name)
            return False

        self.player_info["name"] = name.strip().capitalize()
        return True

    def get_name(self):
        """Get the name of the player."""
        return self.player_info["name"]

    def ask_name(self):
        """Ask the player for their name and validate the input."""
        name = input("What is your name?: ").strip().capitalize()
        if len(name) < 1:
            print("The name you entered is too short")
            return self.ask_name()
        elif len(name) > 20:
            print("Name can't be longer than 20 characters!")
            return self.ask_name()
        elif name.isdigit():
            print("The name you entered only contains numbers, please enter your name.")
            return self.ask_name()

        print(f"Your name is, {name}!")
        time.sleep(0.6)
        return name

    def get_position(self):
        """Get the player's position on the map."""
        return self.player_info["position"]

    def get_previous_player_name(self):
        """Get the name of the player from the latest saved file."""
        try:
            # get the latest saved file
            files = os.listdir("saves")
            paths = [os.path.join("saves", basename) for basename in files]
            latest_file = max(paths, key=os.path.getmtime)
            with open(f"{latest_file}", "r") as file:
                data = json.load(file)
                return data["name"]
        except FileNotFoundError:
            return False

    def save(self):
        """Save the player's information to a JSON file in the folder saves. To load it later."""

        try:
            if not os.path.exists("saves"):
                os.makedirs("saves")

            with open(f"saves/player_{self.player_info['name'].lower()}.json", "w") as file:
                json.dump(self.player_info, file, indent=4)
                print("\nSaved the player's data")
        except FileNotFoundError:
            print("An error occurred while saving the player's information.")


    def load(self, player_name):
        """Load the player's information from the saved JSON file."""

        try:
            # Load the player's information from a JSON file
            with open(f"saves/player_{player_name.lower()}.json", "r") as file:
                # overwrite the player's information with the loaded data but keep new keys when adding new features
                self.player_info.update(json.load(file))
                return True
        except FileNotFoundError:
            return False

    def load_from_saves(self):
        """Ask the user from which save they want to load the game."""
        files = os.listdir("saves")

        # Check if there are any saved files
        if not files:
            print("There are no saved files to load from.")
            self.reset_info()
            self.set_name(self.ask_name())
            self.show_help_menu()
            return False

        print("Choose a save to load:")
        for number, file in enumerate(files, 1):
            file = file.split("_")[1].split(".")[0].capitalize() # Remove the 'player_' and '.json' from name for display
            print(f"{number}. {file}")

        choice = input("Enter the number of the save you want to load: ")
        try:
            choice = int(choice)
            player_name = files[choice - 1].split("_")[1].split(".")[0]
            self.load(player_name)
        except (ValueError, IndexError) as e:
            print("Invalid choice, please enter a valid number.")
            return self.load_from_saves()

    def is_first_time_playing(self):
        """Check if the player is playing for the first time."""
        previous_player_name = self.get_previous_player_name()
        if not previous_player_name:
            return True

        return not self.load(previous_player_name)

    def move(self, direction):
        """Move the player on the map based on the direction they choose."""
        i, j = self.player_info["position"]
        new_i, new_j = i, j

        map = self.get_current_map()

        if direction == 'w':
            new_i = i - 1
        elif direction == 's':
            new_i = i + 1
        elif direction == 'a':
            new_j = j - 1
        elif direction == 'd':
            new_j = j + 1
        else:
            if ',' in direction:
                try:
                    print("Teleporting to custom coordinates...")
                    split_coords = direction.split(',')
                    new_i, new_j = int(split_coords[0]), int(split_coords[1])
                    print(f"Teleported to {new_i}, {new_j}")
                except ValueError:
                    print("Invalid coordinates! Please enter the coordinates as 'i,j'.")
                    return False
            else:
                print("Invalid direction! Use w/a/s/d to move, or 'q' to quit.")
                return False

        if 0 <= new_i < len(map) and 0 <= new_j < len(map[0]):
            if self.is_collision(map, [new_i, new_j]):
                print(f"Can't move there, it's a {map[new_i][new_j]}!")
                return False
            else:
                self.player_info["position"] = [new_i, new_j]

                if self.is_interaction(map, [new_i, new_j]):
                    self.interact(map, [new_i, new_j])

                return True
        else:
            print("Can't move outside the map boundaries!")

        return True

    def multiple_choice_question(self, question, options, show_numbers=True):
        """Ask a multiple choice question and return the string of the selected option."""
        print(question)

        if show_numbers:
            for number, option in enumerate(options, 1):
                print(f"{number}. {option}")

            choice = input("Choose an option: ")

            try:
                choice = int(choice)

                if choice < 1 or choice > len(options):
                    print("That's not a valid option")
                    return self.multiple_choice_question(question, options)

                return options[choice - 1]

            except ValueError:
                print("That's not a valid option")
                return self.multiple_choice_question(question, options)
        else:
            for option in options:
                first_letter = option[0].lower() if len(option) > 0 else ''
                print(f"({first_letter}) {option}")

            choice = input("Choose an option: ").strip().lower()

            try:
                choice = choice[0].lower()

                if choice not in [option[0].lower() for option in options]:
                    print("That's not a valid option")
                    raise IndexError

                # Get the full choice name from the options list
                full_choice = [option for option in options if option[0].lower() == choice][0]

                return full_choice
            except IndexError:
                return self.multiple_choice_question(question, options, False)

    def yes_no_question(self, question):
        """Ask a yes/no question and return the answer. If the answer is wrong, ask again."""
        answer = input(f"{question} (y/n): ").strip().lower()

        try:
            # if the answer is not 'y' or 'n', it will raise an Error
            if answer[0] == 'y':
                return True
            elif answer[0] == 'n':
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
                raise IndexError

        except IndexError:
            return self.yes_no_question(question)

    def interact(self, map, position):
        """Interact with the object on the map."""
        i, j = position
        if map[i][j] == '🏪':
            print("You entered the Poké Mart! \n")
            time.sleep(1)
            show_pokemart_menu(self)
        elif map[i][j] == '⛑️':
            print("You entered the Pokémon Center!")
            time.sleep(1)
            show_pokecenter_menu(self)
        elif map[i][j] == '🏠':
            show_professor_house_menu()
        elif map[i][j] in GROWABLE_BERRIES:
            try:
                berry = [key for key, value in ITEM_EMOJIS.items() if value == map[i][j]][0]
                print(f"You found {berry}!")
                # ask if player wants to pick it up
                if self.yes_no_question("Do you want to pick this berry up?"):
                    self.set_inventory_item(berry, 1, "add")
                    map[i][j] = '  '
                else:
                    print("The berry disappeared...")
                    map[i][j] = '  '
            except IndexError:
                print("There was an error while trying to pick up the berry.")
        elif map[i][j] == '🥚':
            print("You found an egg!")
            # ask if player wants to pick it up
            if self.yes_no_question("Do you want to pick it up?"):
                self.set_inventory_item("Eggs", 1)
                map[i][j] = '  '
            else:
                print("The egg disappeared...")
                map[i][j] = '  '
        elif map[i][j] == '💰':
            coins = random.randint(25, 250)
            print(f"You found a bag with {coins} coins!")
            # ask if player wants to pick it up
            if self.yes_no_question("Do you want to pick it up?"):
                self.set_coins(coins, "add")
                map[i][j] = '  '
            else:
                print("The bag of coins disappeared...")
                map[i][j] = '  '
        elif map[i][j] == '🏝️':
            # ask if player wants to travel to the beach
            if self.yes_no_question("Do you want to travel to the beach?"):
                self.switch_map("beach")
        elif map[i][j] == '🌲':
            if self.yes_no_question("Do you want to travel to the grassland?"):
                self.switch_map("grassland")

    def is_interaction(self, map, position):
        """Check if the coordinates are an interaction object on the map."""
        i, j = position
        return map[i][j] in INTERACTION_OBJECTS

    def interact_if_possible(self, position):
        """Interact with the object on the map if it's possible."""
        if self.is_interaction(self.get_current_map(), position):
            self.interact(self.get_current_map(), position)
            return True
        return False

    def is_collision(self, map, position):
        """Check if the coordinates are a collision object on the map."""
        i, j = position
        return map[i][j] in COLLISION_OBJECTS

    def is_grass(self, position=None):
        """Check if the coordinates are grass on the map. Can be used for wild encounters."""
        if position is None:
            position = self.player_info["position"]
        i, j = position
        return self.get_current_map()[i][j] in GRASS_OBJECTS

    def is_water(self, position=None):
        """Check if the coordinates are water on the map. Can be used for wild encounters."""
        if position is None:
            position = self.player_info["position"]
        i, j = position
        return self.get_current_map()[i][j] in WATER_OBJECTS

    def get_emoji_for_item(self, item):
        """Get the emoji for an item from the ITEM_EMOJIS dictionary."""
        try:
            return ITEM_EMOJIS.get(item, "")
        except KeyError:
            return ""

    def clean_bag(self):
        """Remove the empty (0) items from the inventory."""
        self.player_info["inventory"] = {item: quantity for item, quantity in self.player_info["inventory"].items() if quantity > 0}

    def sort_bag(self):
        """Sort the inventory by the item names."""
        self.player_info["inventory"] = dict(sorted(self.player_info["inventory"].items(), key=lambda x: x[0].split()[-1]))
        # Sort the poké balls based on the POKEBALLS list
        self.player_info["inventory"] = dict(sorted(self.player_info["inventory"].items(), key=lambda x: list(POKEBALLS.keys()).index(x[0]) if x[0] in POKEBALLS else -1))
        # Place the Poké Balls at the start of the inventory
        self.player_info["inventory"] = dict(sorted(self.player_info["inventory"].items(), key=lambda x: x[0] not in POKEBALLS))

    def show_bag(self):
        """Show the list of items in the player's bag."""
        self.clean_bag()
        self.sort_bag()

        print(f"\n{TextStyles.bold}Bag from {self.get_name()}{TextStyles.reset}")
        for item, quantity in self.player_info["inventory"].items():
            item_emoji = self.get_emoji_for_item(item)
            print(f"{item} {item_emoji}: {quantity}")

        # Number of coins the player has
        print(f"{TextStyles.yellow}Coins:{TextStyles.reset} {self.get_coins()}")

        # check if player has seeds
        has_seeds = self.get_inventory_item("Berry Seeds") > 0

        choice = input(f"\nPress Enter to go back or S to save {'or P to plant your seeds' if has_seeds else ''} -> ").strip().lower()
        if len(choice) > 0:
            if len(choice) > 0 and choice[0] == 's':
                self.save()
            elif has_seeds and len(choice) > 0 and choice[0] == 'p':
                self.plant_a_seed()

    def plant_a_seed(self):
        """Plant a berry seed on the current player position if possible."""
        if self.get_inventory_item("Berry Seeds") < 1:
            print("You don't have any seeds to plant.")
            return

        plant_seed(self)

    def select_item_from_bag(self):
        """Select an item from the player's bag and return the chosen item."""
        self.clean_bag()
        self.sort_bag()

        print(f"{TextStyles.bold}Bag from {self.get_name()}{TextStyles.reset}")
        number = 0
        for number, (item, quantity) in enumerate(self.player_info["inventory"].items(), 1):
            item_emoji = self.get_emoji_for_item(item)
            print(f"{number}. {item} {item_emoji}: {quantity}")

        print(f"{number + 1}. Exit")
        choice = input("Choose an item from your bag: ")

        try:
            if choice == "e" or choice == "exit":
                return None

            choice = int(choice)

            if choice == number + 1:
                return None

            if choice < 1 or choice > len(self.player_info["inventory"]):
                raise ValueError()

            item = list(self.player_info["inventory"].keys())[choice - 1]
            return item
        except ValueError:
            print("That's not a valid item")
            return self.select_item_from_bag()

    def pokemon_nickname(self, pokemon):
        """Return the nickname of the Pokémon if it has one, otherwise return the name."""
        return pokemon.get('nickname', pokemon['name'])

    def pokemon_set_nickname(self, index, nickname):
        """Set a nickname for a Pokémon in the player's list."""
        nickname = nickname.strip().capitalize()
        if nickname == '':
            print(f"The nickname for {self.pokemon_nickname(self.player_info['pokemon'][index])} can't be empty.")

            # Ask the player to give a nickname again or keep the default name
            choice = self.yes_no_question("Do you still want to give a nickname?")
            if choice:
                return self.pokemon_set_nickname(index, input("Enter a nickname: ").strip().capitalize())
            else:
                return False

        elif nickname == self.player_info['pokemon'][index]['name']:
            return False
        else:
            if type(nickname) != str:
                return self.pokemon_set_nickname(index, input("Enter a nickname: ").strip().capitalize())

            self.player_info['pokemon'][index]['nickname'] = nickname
            return True

    def pokemon_has_nickname(self, pokemon):
        """Check if the Pokémon has a nickname. Return a boolean."""
        if 'nickname' in pokemon:
            if pokemon['nickname'] == '' or pokemon['nickname'] == pokemon['name']:
                return False
        return 'nickname' in pokemon

    def is_pokemon_shiny(self, pokemon):
        """Check if the Pokémon is shiny.
        :return: True if the Pokémon is shiny, otherwise False
        """
        try:
            if pokemon['shiny']:
                return True
        except KeyError:
            pass
        return False

    def show_pokemon_list(self):
        """Show the list of Pokémon the player has caught."""
        print(f"\n{TextStyles.bold}Pokémon List{TextStyles.reset}")
        print(f"Total Pokémon: {len(self.player_info['pokemon'])}")
        for number, pokemon in enumerate(self.player_info["pokemon"], 1): # Start the numbering from 1
            time.sleep(0.01)
            is_shiny = "✨" if self.is_pokemon_shiny(pokemon) else ""

            # if the pokemon has a nickname the player gave show it, otherwise show only the name
            print(f"{number}. {is_shiny}{TextStyles.green + self.pokemon_nickname(pokemon) + TextStyles.reset + ' - ' if self.pokemon_has_nickname(pokemon) else ''}{ TextStyles.grey + pokemon['name'] + TextStyles.reset} - ID: {pokemon['id']}")
        number = input("\nPress Enter to go back, select a Pokémon to view or type 'release all' to release all double Pokémon: ").strip()
        try:
            if number == "":
                return
            if number.isdigit():
                number = int(number)
                if number < 1 or number > len(self.player_info["pokemon"]):
                    raise ValueError()
                self.view_pokemon(number - 1)
            elif number == "release all":
                if self.yes_no_question(f"Are you sure you want to release all double Pokémon? {TextStyles.grey}Except shiny and Pokémon with nicknames.{TextStyles.reset}"):
                    self.release_duplicate_pokemon()
                else:
                    return self.show_pokemon_list()
            else:
                # check if the input is the nickname or name of the pokemon
                for index, pokemon in enumerate(self.player_info["pokemon"]):
                    if number.lower() == pokemon.get('nickname', pokemon['name']).lower():
                        self.view_pokemon(index)
                        break
        except ValueError:
            return self.show_pokemon_list()

    def release_pokemon(self, index):
        """Release a Pokémon from the player's list."""
        print(f"You released {self.pokemon_nickname(self.player_info['pokemon'][index])} back into the wild!")
        self.player_info["pokemon"].pop(index)
        sleep(1)

    def release_duplicate_pokemon(self):
        """Release all duplicate Pokémon from the player's list.
        :return: Number of Pokémon released/removed from the list
        """
        # Don't release shiny Pokémon or Pokémon with nicknames
        release_count = 0
        for pokemon in self.player_info["pokemon"]:
            if self.player_info["pokemon"].count(pokemon) > 1 and not self.is_pokemon_shiny(pokemon) and not self.pokemon_has_nickname(pokemon):
                self.player_info["pokemon"].remove(pokemon)
                release_count += 1

        print(f"Released {release_count} Pokémon back into the wild!")
        return release_count

    def view_pokemon(self, index):
        """View the details of a Pokémon from the player's list."""
        pokemon = self.player_info["pokemon"][index]
        print(f"\n{TextStyles.bold}Pokémon Details{TextStyles.reset}")
        if 'nickname' in pokemon and pokemon['nickname'] != '':
            print(f"Nickname: {pokemon['nickname']}")
        print(f"Name: {pokemon['name']} {'✨' if self.is_pokemon_shiny(pokemon) else ''}")
        print(f"ID: {pokemon['id']}")
        print(f"Type: {pokemon['type'].capitalize()} {type_emoji.get(pokemon['type'], '❓')}")

        print(f"\nYou have {TextStyles.yellow}{len([p for p in self.player_info['pokemon'] if p['id'] == pokemon['id']])}{TextStyles.reset} of this Pokémon.")

        choice = input("\nPress Enter to go back or R to release this Pokémon, N to give a nickname: ").strip()
        try:
            if len(choice) > 0:
                if choice[0].lower() == 'r':
                    self.release_pokemon(index)
                elif choice[0].lower() == 'n':
                    self.pokemon_set_nickname(index, input("Enter a nickname: "))

        except ValueError:
            return self.view_pokemon(index)

        self.show_pokemon_list()

    def hatch_egg(self):
        """Hatch an egg from the player's inventory containing a random rare Pokémon."""
        if self.get_inventory_item("Eggs") < 1:
            return

        print("Oh? An egg is hatching...\n")
        time.sleep(2)

        hatched_pokemon = fetch_random_pokemon(self)

        if hatched_pokemon:
            self.set_inventory_item("Eggs", 1, "subtract")

            print(f"Congratulations! You hatched a {hatched_pokemon['name']}!")

            if self.yes_no_question("Do you want to give this Pokémon a nickname?"):
                hatched_pokemon['nickname'] = input("Enter a nickname: ").strip().capitalize()


            print(f"Added {hatched_pokemon['name'] if 'nickname' not in hatched_pokemon else hatched_pokemon['nickname']} to your bag.")
        else:
            print("Something went wrong while hatching the egg...\n")

    def show_help_menu(self):
        """Help menu with the explanation about the game."""
        print(f"\n{TextStyles.bold}Welcome to the world of Pokémon Catch!{TextStyles.reset}\n")
        print(f"You are a Pokémon Hobbyist ({self.player_info['skin']} on the map), you want to catch the Pokémon you like. Without fighting them.")
        time.sleep(2)
        print("In this game, you can move around the map, catch Pokémon and collect items and coins along the way.")
        time.sleep(2)
        print("You can move using W/A/S/D. Press B to open your bag, and Q to quit the game.")
        time.sleep(1)
        print("You can encounter wild Pokémon in the grass (🌿) and catch them using various Poké Balls in your bag.")
        time.sleep(2)
        print("\nVisit the PokéMart (🏪) to buy items such as Poké Balls you need to catch the pokemon. to help you on your journey.")
        time.sleep(2)
        print("On your way you can find coins (💰) which you can use to buy items from the PokéMart.")
        print("Or you can sell items you don't need to the PokéMart in exchange for some coins.\n")
        time.sleep(2)
        print("Visit the Pokémon Center (⛑️) to view the list of Pokémon you've caught, release them, or give them nicknames.")
        if self.get_inventory_item("Eggs") > 0:
            time.sleep(1.5)
            print("\nThe Egg (🥚) in your bag, can hatch at any random moment during your journey. It hatches into a random Pokémon out of all 151 Kanto Pokémon. Including the legendary ones.")
        if self.get_inventory_item("Berry Seeds") > 0:
            time.sleep(1.5)
            berries = ', '.join([berry for berry in GROWABLE_BERRIES])
            print(f"\nYou can plant Berry Seeds (🌱) on the grassland map. They grow into Berries {berries} over time that you can pick up.")
        if self.get_inventory_item("Razz Berries") > 0 or self.get_inventory_item("Golden Razz Berries") > 0:
            time.sleep(1.5)
            print("\nRazz Berries (🍇) increase the catch rate of the Pokémon you encounter.")
            print("Golden Razz Berries (🍋) are even stronger and increase the catch rate more.")
        if self.get_inventory_item("Pinap Berries") > 0:
            time.sleep(1.5)
            print("Pinap Berries (🍍) increase the shiny chance of the Pokémon for the next encounter.\n")

        time.sleep(3)

        # print("The emojis you see beside the Pokémon's name represent their type. 🌱(grass)🔥(fire)💧(water) etc.")
        # time.sleep(3)
        # print("Visit the Professor's house (🏠) to get information about the Pokémon you've caught.")

def initialize_new_player(player):
    """Initialize a new player on their first time playing."""
    player.set_name(player.ask_name())
    print("\nWelcome to the world of Pokémon! \n")
    player.choose_skin()
    player.show_help_menu()


def load_existing_player(player):
    """Load an existing player's progress or start a new game."""
    print(f"\nWelcome back, {player.get_name()}!\n")
    choice = player.yes_no_question("Do you want to continue your previous game?")

    if not choice:
        choice = player.multiple_choice_question("Do you want to start a new game or load from a save?",
                                                 ["New game", "Load from save"])
        if choice == "New game":
            player.reset_info()
            if player.set_name(player.ask_name()):
                player.choose_skin()
                player.show_help_menu()
        elif choice == "Load from save":
            player.load_from_saves()