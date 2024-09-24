import random
from config import GROWABLE_BERRIES, COLLISION_OBJECTS, INTERACTION_OBJECTS, WATER_OBJECTS


def is_edge_position(r, c, rows, cols):
    """Check if a position is on the edge of the map."""
    return r == 0 or c == 0 or r == rows - 1 or c == cols - 1

def generate_map(rows, cols, map_type='grassland', density=0.4, player=None):
    """Generates a map with given rows and columns for different map types."""
    new_map = []
    grass_positions = []

    for r in range(rows):
        row = []
        for c in range(cols):
            if is_edge_position(r, c, rows, cols):
                row.append('🌊' if map_type == 'beach' else '🌳')
            else:
                # density is grass density for grasslands.
                if random.random() < density:
                    if map_type == 'grassland':
                        row.append('🌿')
                    elif map_type == 'beach':
                        row.append(random.choice(WATER_OBJECTS))
                    grass_positions.append((r, c))
                else:
                    row.append('  ')  # Open path
        # Append the generated row to the map
        new_map.append(row)

    if map_type == 'grassland' and len(grass_positions) >= 3:
        place_structures(new_map, grass_positions)

    if map_type == 'grassland':
        spawn_beach(new_map)
    elif map_type == 'beach':
        spawn_forest(new_map, player)

    return new_map

def place_structures(map, grass_positions):
    """Place key structures like PokéMart, Pokémon Center, and Professor's house."""
    pokemart_pos = random.choice(grass_positions)
    grass_positions.remove(pokemart_pos)
    pokecenter_pos = random.choice(grass_positions)
    grass_positions.remove(pokecenter_pos)
    professor_pos = random.choice(grass_positions)

    map[pokemart_pos[0]][pokemart_pos[1]] = '🏪'
    map[pokecenter_pos[0]][pokecenter_pos[1]] = '⛑️'
    map[professor_pos[0]][professor_pos[1]] = '🏠'

def find_empty_positions(map):
    """Find all empty positions on the map."""
    return [(r, c) for r in range(len(map)) for c in range(len(map[r])) if map[r][c] == '  ']

def spawn_random_item(map, item_list):
    """Spawn a random item on the map in an empty position."""
    empty_positions = find_empty_positions(map)
    if empty_positions:
        item_pos = random.choice(empty_positions)
        item = random.choice(item_list)
        map[item_pos[0]][item_pos[1]] = item

def random_spawn_items(map, player):
    """Spawn items like egg, coin on a random empty location on the map."""
    if random.randint(1, 150) <= 15:
        if random.randint(1, 100) <= 25 and player.get_inventory_item("Eggs") > 0:
            player.hatch_egg()
        elif '🥚' not in [item for row in map for item in row] and '💰' not in [item for row in map for item in row]:
            spawn_random_item(map, ['🥚', '💰', '💰'])

    if random.randint(1, 100) <= 10:
        grow_plant(player)

    return map

def random_spawn_tile(map, object, positions=None, check_below=True):
    """Spawn a tile on a random position from the given list of positions."""
    forbidden_objects = COLLISION_OBJECTS + INTERACTION_OBJECTS
    if not positions:
        positions = find_empty_positions(map)

    spawn_pos = random.choice(positions)

    try:
        row, col = spawn_pos
        if is_edge_position(row, col, len(map), len(map[0])):
            map[row][col] = object
        elif check_below and map[row + 1][col] in forbidden_objects:
            random_spawn_tile(map, object, positions, check_below)
        else:
            random_spawn_tile(map, object, positions, check_below)
    except IndexError:
        random_spawn_tile(map, object, positions, check_below)

def spawn_forest(map, player):
    """Spawn a forest object at the location of the player."""
    row, col = player.get_position()
    map[row][col] = '🌲'

def spawn_beach(map):
    """Spawn one beach object on a random edge position of the map."""

    # Get top and bottom edge positions without corners
    edge_positions = [(0, c) for c in range(1, len(map[0]) - 1)] + [(len(map) - 1, c) for c in range(1, len(map[0]) - 1)]

    if edge_positions:
        random_spawn_tile(map, '🏝️', edge_positions, True)

def plant_seed(player, position=None):
    """Plant a berry seed on the current player position if possible."""
    if not position:
        position = player.get_position()

    row, col = position
    current_map = player.get_current_map()

    if current_map[row][col] == '  ':
        player.set_inventory_item("Berry Seeds", -1)
        current_map[row][col] = '🌱'
        print("You planted a seed.")
    else:
        print("You can't plant a seed here.")

def grow_plant(player):
    """Grows one planted seed into one random berry"""
    current_map = player.get_current_map()
    planted_seeds = [(r, c) for r in range(len(current_map)) for c in range(len(current_map[r])) if current_map[r][c] == '🌱']
    if planted_seeds:
        seed_pos = random.choice(planted_seeds)
        current_map[seed_pos[0]][seed_pos[1]] = random.choice(GROWABLE_BERRIES)

def display_map(player):
    """Display the current map and place player."""
    current_map = player.get_current_map()
    if player.get_current_map_name() == 'grassland':
        random_spawn_items(current_map, player)
    for r in range(len(current_map)):
        for c in range(len(current_map[r])):
            if [r, c] == player.get_position():
                print(player.player_info["skin"], end='')  # Player emoji
            else:
                print(current_map[r][c], end=' ')
        print()

def create_maps(player):
    rows, cols = 7, 20
    maps = {
        'grassland': {'map_type': 'grassland', 'density': 0.4},
    }
    for map_name, params in maps.items():
        player.set_map(map_name, generate_map(rows, cols, params['map_type'], params['density'], player))