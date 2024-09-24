POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2/'

# Number of wild Pokémon to load in advance to avoid delays during gameplay
WILD_POKEMON_PRELOAD_COUNT = 10

GRASS_OBJECTS = ['🌿', '🌾']
WATER_OBJECTS = ['🫧', '💦']
COLLISION_OBJECTS = ['🌳', '🌊']
INTERACTION_OBJECTS = ['🏪', '⛑️', '🏠', '🏝️', '🌲']
SPAWNABLE_OBJECTS = ['🥚', '💰']
GROWABLE_BERRIES = ('🍓', '🍓', '🍓', '🍋', '🍍') # 3/5 chance of getting a normal razz berry

# add growable berries to the spawnable objects because they are also spawnable
SPAWNABLE_OBJECTS += list(set(GROWABLE_BERRIES))

# add spawnable objects to the interaction objects because they are also interactable
INTERACTION_OBJECTS += SPAWNABLE_OBJECTS

LEGENDARY_POKEMON = [144, 145, 146, 150, 151] # 144 is Articuno, 145 is Zapdos, 146 is Moltres, 150 is Mewtwo, 151 is Mew

POKEBALLS = {'Poké Balls': '⛔️', 'Great Balls': '🔵', 'Ultra Balls': '🎱', 'Master Balls': '🔮'}

ITEM_EMOJIS = {
    "Razz Berries": "🍓", # Increases the catch rate
    "Golden Razz Berries": "🍋", # Increases the catch rate significantly
    "Pinap Berries": "🍍", # Increases the shiny chance for the next encounter
    "Berry Seeds": "🌱", # Plant a berry seed to grow one of the berries
    "Eggs": "🥚", # Eggs to hatch a Pokémon
    "Coins": "💰" # Currency to buy items from the shop
}

ITEM_EMOJIS.update(POKEBALLS) # Add the Poké Balls to the item emojis because they are also items

wild_pokemon_file = 'wild_pokemon_list.json'
wild_grass_pokemon_file = 'wild_grass_pokemon_list.txt'
wild_water_pokemon_file = 'wild_water_pokemon_list.txt'

class TextStyles:
    """Text styles for the console."""
    red = "\u001b[0;31m"
    green = "\u001b[0;32m"
    yellow = "\u001b[0;33m"
    blue = "\u001b[0;34m"
    magenta = "\u001b[0;35m"
    cyan = "\u001b[0;36m"
    white = "\u001b[0;37m"
    grey = "\u001b[0;90m"
    underline = "\u001b[4m"
    bold = "\u001b[1m"
    inverse = "\u001b[7m"
    reset = "\u001b[0m"