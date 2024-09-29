import random
import time
from time import sleep

import requests

from config import POKEAPI_BASE_URL, WILD_POKEMON_PRELOAD_COUNT, LEGENDARY_POKEMON, wild_grass_pokemon_file, \
    wild_water_pokemon_file, POKEBALLS

# Emoji dictionary for Pokémon types
type_emoji = {
    'fire': '🔥',
    'water': '💧',
    'grass': '🌱',
    'electric': '⚡',
    'flying': '🐦',
    'normal': '🐭',
    'fighting': '🥊',
    'poison': '☠️',
    'ground': '🏜️',
    'rock': '🪨',
    'bug': '🐞',
    'ghost': '👻',
    'steel': '🔩',
    'ice': '🧊',
    'dragon': '🐉',
    'dark': '🦇',
    'fairy': '🧚',
    'psychic': '🔮',
}

def fetch_from_api(endpoint):
    """Make a GET request to the specified API endpoint and return the JSON data.
    :return: JSON data from the API, None when an error occurs.
    """
    try:
        response = requests.get(endpoint)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except Exception:
        print("Error fetching data from the API. Is your internet connection working?")
        exit("Exiting the game.")

    return None

# Check if a Pokémon can be found in the wild in a grass area
def can_be_found_in_grass(pokemon_id):
    """Check if a given Pokémon can be found in the wild in a grass area.
    :return: True if the Pokémon can be found in the grass, False otherwise.
    """
    if pokemon_id in LEGENDARY_POKEMON: # Don't allow legendary Pokémon to be found in the wild, only be found in Eggs
        return False

    data = fetch_from_api(f'{POKEAPI_BASE_URL}pokemon/{pokemon_id}/encounters')

    if data:
        for location in data:
            for version_detail in location['version_details']:
                for encounter_detail in version_detail['encounter_details']:
                    if encounter_detail['method']['name'] in ['walk', 'old-walk', 'shake-tree', '.walk', 'sos-encounter', 'roaming-grass']:
                        return True
    return False

def can_be_found_in_water(pokemon_id):
    """Check if a given Pokémon can be found in the wild in a water area.
    :return: True if the Pokémon can be found in the water, False otherwise.
    """
    if pokemon_id in LEGENDARY_POKEMON: # Don't allow legendary Pokémon to be found in the wild, only be found in Eggs
        return False

    data = fetch_from_api(f'{POKEAPI_BASE_URL}pokemon/{pokemon_id}/encounters')

    if data:
        for location in data:
            for version_detail in location['version_details']:
                for encounter_detail in version_detail['encounter_details']:
                    if encounter_detail['method']['name'] in ['surf', 'rod', 'super-rod', 'fish-chain']:
                        return True
    return False

def extract_pokemon_data(data):
    """Extract key the important Pokémon data from the API response.
    :return: Dictionary with the Pokémon data. Keys: id, name, type, catch_rate.
    """
    return {
        'id': int(data['id']),
        'name': data['name'].capitalize(),
        'type': data['types'][0]['type']['name'],
        'catch_rate': fetch_catch_rate(data['id'])
    }

def preload_pokemon_list(count=WILD_POKEMON_PRELOAD_COUNT, type='grass'):
    """Preload a list of Pokémon in advance to speed up the game for Pokémon that can be found in the wild.
    :return: List of the count of Pokémon.
    """
    pokemon_list = []

    print(f'Loading wild {type.strip().lower().capitalize()} Pokémon', end='')

    while len(pokemon_list) < count:
        print('.', end='')
        pokemon_id = random.randint(1, 149)  # Limit to first-generation Pokémon for simplicity
        if type.strip().lower() == 'water':
            if can_be_found_in_water(pokemon_id):
                data = fetch_from_api(f'{POKEAPI_BASE_URL}pokemon/{pokemon_id}')
                if data:
                    pokemon_list.append(extract_pokemon_data(data))
        else:
            if can_be_found_in_grass(pokemon_id):
                data = fetch_from_api(f'{POKEAPI_BASE_URL}pokemon/{pokemon_id}')
                if data:
                    pokemon_list.append(extract_pokemon_data(data))

    return pokemon_list

def fetch_catch_rate(pokemon_id):
    """Get the catch rate of a Pokémon species.
    :return: The catch rate of the given Pokémon species id.
    """
    data = fetch_from_api(f'{POKEAPI_BASE_URL}pokemon-species/{pokemon_id}/')
    if data:
        catch_rate = data.get('capture_rate', 0)  # Default to 0 if capture_rate is not found

        if catch_rate > 200:  # Limit the catch rate to 200 otherwise it's too easy to catch the Pokémon
            catch_rate = 200

        return catch_rate
    return 0

def catch_pokemon(player, pokemon, pokeball):
    """Attempt to catch the given Pokémon.
    :param player: The player object.
    :param pokemon: The Pokémon as a dictionary to catch.
    :param pokeball: The type of Poké Ball to use.
    """

    # Check if the player has Poké Balls
    if player.get_inventory_item(pokeball) < 1:
        print(f"You don't have any {pokeball} in your bag!")
        return


    # Remove a Poké Ball from the player's bag
    player.set_inventory_item(pokeball, 1, 'subtract')

    catch_chance = pokemon['catch_rate'] * 255 / 255  # Catch rate formula

    # Increase the catch rate by type of pokéball used from the order of the POKEBALLS dictionary
    catch_chance += list(POKEBALLS.keys()).index(pokeball) * 15

    # shake the ball
    print("\nShaking", end='')

    # Simulate shaking the Poké Ball by printing dots
    for i in range(3):
        time.sleep(0.5)
        print('.', end='')

    pokemon_emoji = type_emoji.get(pokemon['type'], '❓')  # Default emoji if type not found

    is_shiny = False
    try:
        is_shiny = pokemon['shiny']
    except KeyError:
        is_shiny = False

    if random.randint(1, 255) < catch_chance or is_shiny or pokeball == 'Master Balls':
        # Remove the unused keys from the Pokémon dictionary for optimization
        pokemon.pop('egg_used', None)
        pokemon.pop('berry_used', None)

        # Add the Pokémon to the player's bag
        player.add_pokemon_to_bag(pokemon)
        time.sleep(1)
        print(f"\nYou caught {pokemon['name']} {pokemon_emoji}!")
        time.sleep(0.5)

        # ask if player wants to give a nickname
        if player.yes_no_question("Do you want to give this Pokémon a nickname?"):
            nickname = input("Enter a nickname: ").strip().capitalize()
            pokemon['nickname'] = nickname
        time.sleep(0.5)
        print(f"Adding {pokemon['name'] if 'nickname' not in pokemon else pokemon['nickname']} to your bag.")
        time.sleep(1)
    elif random.randint(1, 100) <= 55: # 55% chance to break free but not run away
        time.sleep(1)
        print(f"\n{pokemon['name']} {pokemon_emoji} broke free!\n")
        return encounter_menu(player, pokemon)
    else:
        time.sleep(1)
        print(f"{pokemon['name']} {pokemon_emoji} ran away!")

def use_pinap_berry(player):
    """Use a Pinap Berry to increase the shiny rate for the next encounter."""
    # check if the player has a Pinap Berry in their bag
    if player.get_inventory_item('Pinap Berries') > 0:
        # Remove one Pinap Berry from the player's bag
        player.set_inventory_item('Pinap Berries', 1, 'subtract')

        player.consumed_pinap_berry = True

        # Increase the shiny rate for the next encounter
        player.increase_shiny_rate()
        print("You used a Pinap Berry it increased the shiny rate for the next encounter.")
    else:
        print("You don't have any Pinap Berries in your bag!")

def increase_catch_rate(pokemon, amount=25):
    """Increase the catch rate for the given Pokémon."""
    # Increase the catch rate by 25 for the next encounter but clamp it to 225
    pokemon['catch_rate'] = max(0, min(pokemon['catch_rate'] + amount, 225))

def use_razz_berry(player, pokemon, amount=25, type='Razz'):
    """Use a Razz Berry to increase the catch rate for the current encounter."""

    # check if the player has a Razz Berry in their bag
    if player.get_inventory_item(f'{type} Berries') > 0:
        # Check if not already used a Berry on this encounter
        if 'berry_used' in pokemon:
            print("You already used a Berry on this Pokémon encounter.")
            return

        # Remove one Razz Berry from the player's bag
        player.set_inventory_item(f'{type} Berries', 1, 'subtract')

        increase_catch_rate(pokemon, amount)

        # Mark the Pokémon as used a Berry
        pokemon['berry_used'] = True

        for i in range(3): # Simulate eating the Berry by printing "Yum" three times
            print("Yum ", end='')
            time.sleep(0.5)

        print("\nYou used a Razz Berry it increased the catch rate.")
    else:
        print("You don't have any Razz Berries in your bag!")


def encounter_menu(player, pokemon):
    """Menu for the player to decide what to do when encountering a wild Pokémon."""

    action = input("Do you want to open your bag (b)ag or (r)un?: ").strip().lower()
    action = action[0] if len(action) > 0 else '' # Get the first character when string is not empty

    # Retrieve the emoji based on the Pokémon's type
    pokemon_emoji = type_emoji.get(pokemon['type'], '❓')  # Default emoji if type not found

    if action == 'b':
        selected_item = player.select_item_from_bag()

        if selected_item in POKEBALLS:
            catch_pokemon(player, pokemon, selected_item)
        elif selected_item == 'Pinap Berries':
            use_pinap_berry(player)
            return encounter_menu(player, pokemon)
        elif selected_item == 'Razz Berries':
            use_razz_berry(player, pokemon)
            return encounter_menu(player, pokemon)
        elif selected_item == 'Golden Razz Berries':
            use_razz_berry(player, pokemon, amount=50, type='Golden Razz')
            return encounter_menu(player, pokemon)
        elif selected_item == 'Eggs':
            # You can hurt a Pokémon by throwing an egg at it to slightly increase the catch rate

            # Check if not already used an egg on this pokemon encounter
            if 'egg_used' in pokemon:
                print("You already used an egg on this Pokémon encounter.")
                return encounter_menu(player, pokemon)

            print("You threw an egg at the Pokémon. The Pokémon got hurt but the catch rate is slightly increased.")
            player.set_inventory_item('Eggs', 1, 'subtract')
            increase_catch_rate(pokemon, amount=10)
            pokemon['egg_used'] = True
            return encounter_menu(player, pokemon)
        else:
            print("You can only use Poké Balls to catch a Pokémon.")
            encounter_menu(player, pokemon)
    elif action == 'r':
        print(f"You successfully ran away from {pokemon['name']} {pokemon_emoji}!")
    else:
        print(f"{pokemon['name']} {pokemon_emoji} wants to escape while you where confused.")
        return encounter_menu(player, pokemon)

def encounter_pokemon(player, list_pokemon, type='grass'):
    """Encounter a random Pokémon from the list of wild Pokémon."""

    if type.strip().lower() not in ['grass', 'water']:
        return False

    # When the list is less than 1, preload more Pokémon in advance
    if len(list_pokemon) < 1:
        if type == 'grass':
            new_pokemon = preload_pokemon_list(WILD_POKEMON_PRELOAD_COUNT, 'grass')
            list_pokemon.extend(new_pokemon)
            save_wild_pokemon_list(type.lower())
        elif type == 'water':
            new_pokemon = preload_pokemon_list(WILD_POKEMON_PRELOAD_COUNT, 'water')
            list_pokemon.extend(new_pokemon)
            save_wild_pokemon_list(type.lower())

    pokemon = random.choice(list_pokemon)
    list_pokemon.remove(pokemon)

    random.seed(time.time())

    shiny_rate = player.get_shiny_rate()
    try:
        shiny_rate = int(shiny_rate)
        shiny_chance = random.randint(0, shiny_rate)
    except ValueError:
        shiny_chance = 100

    player.decrease_shiny_rate()

    # check if player has a berry consumed
    if player.consumed_pinap_berry:
        player.consumed_pinap_berry = False

    # print(f"Shiny rate: {shiny_rate}%")
    # print(f"Shiny chance: {shiny_chance}%")

    # Retrieve the emoji based on the Pokémon's type
    pokemon_emoji = type_emoji.get(pokemon['type'], '❓')  # Default emoji if type not found

    print(f"\nA wild {pokemon['name']} {pokemon_emoji} appears! {'✨' if shiny_chance <= 5 else ''}")
    if shiny_chance <= 5:
        pokemon['shiny'] = True

    time.sleep(1)

    encounter_menu(player, pokemon)

def fetch_random_pokemon(player):
    """Fetch one pokemon of all the pokemon 1 / 151 including the legendary pokemon."""
    random_id = random.randint(1, 151)
    try:
        response = requests.get(f'{POKEAPI_BASE_URL}pokemon/{random_id}')
        if response.status_code == 200:
            data = response.json()
            pokemon_id = int(data['id'])
            pokemon = {
                'id': pokemon_id,
                'name': data['name'].capitalize(),
                'type': data['types'][0]['type']['name'],
                'catch_rate': fetch_catch_rate(pokemon_id), # Not used in this function but for saving consistency
                # 'caught': 'Hatched'
            }
            # add the pokemon to the player's bag
            player.add_pokemon_to_bag(pokemon)
            return pokemon
    except Exception as e:
        print(f"Error fetching wild Pokémon data. Is your internet connection working?")

    return False


wild_grass_pokemon_list = []
wild_water_pokemon_list = []

def get_wild_pokemon_list(pokemon_type):
    """Get the list of wild Pokémon based on type (grass or water)."""
    return wild_grass_pokemon_list if pokemon_type == 'grass' else wild_water_pokemon_list

def set_wild_pokemon_list(pokemon_type, new_list):
    """Set a new list of wild Pokémon based on type (grass or water)."""
    if pokemon_type == 'grass':
        wild_grass_pokemon_list.clear()
        wild_grass_pokemon_list.extend(new_list)
    else:
        wild_water_pokemon_list.clear()
        wild_water_pokemon_list.extend(new_list)

def save_wild_pokemon_list(pokemon_type):
    """Save the list of wild Pokémon to a file based on type (grass or water)."""

    if pokemon_type.strip().lower() == 'water':
        filename = wild_water_pokemon_file
    else:
        filename = wild_grass_pokemon_file

    pokemon_list = get_wild_pokemon_list(pokemon_type)

    if len(pokemon_list) < 1:
        return

    print(f"Saving wild {pokemon_type} Pokémon data", end='')
    with open(filename, 'w') as f:
        for pokemon in pokemon_list:
            print('.', end='')  # Visual feedback
            f.write(f"{pokemon['id']},{pokemon['name']},{pokemon['type']},{pokemon['catch_rate']}\n")

    print("\nSave completed.")

def load_wild_pokemon_list(pokemon_type, filename, preload_count=WILD_POKEMON_PRELOAD_COUNT):
    """Load the list of wild Pokémon from a file or preload if the file doesn't exist."""
    pokemon_list = get_wild_pokemon_list(pokemon_type)
    print(f"Loading wild {pokemon_type} Pokémon data.")
    try:
        with open(filename, 'r') as f:
            for line in f:
                data = line.strip().split(',')
                pokemon_list.append({
                    'id': int(data[0]),
                    'name': data[1],
                    'type': data[2],
                    'catch_rate': int(data[3])
                })
    except FileNotFoundError:
        print(f"No wild {pokemon_type} Pokémon data found. Preloading Pokémon data.")
        if preload_count:
            pokemon_list.extend(preload_pokemon_list(preload_count))
            save_wild_pokemon_list(pokemon_type)
    print(f"Loaded {pokemon_type} Pokémon data.")

# Load the wild grass Pokémon list when the module is imported
load_wild_pokemon_list('grass', wild_grass_pokemon_file)