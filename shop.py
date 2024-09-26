import time

from config import ITEM_EMOJIS

pokemart_items = [
    ("Poké Balls", 25),
    ("Great Balls", 50),
    ("Ultra Balls", 125),
    ("Master Balls", 10000),
    ("Razz Berries", 15),
    ("Berry Seeds", 5),
    ("Leave the store", 0)
]

pokemart_sell_items = [
    ("Eggs", 10),
    ("Golden Razz Berries", 40),
    ("Pinap Berries", 25)
]

SELL_RATE = 0.8  # Sell the item for 80% of the original price

def display_menu():
    """Displays the PokéMart item menu with prices and emojis."""
    for key, (item, price) in enumerate(pokemart_items, 1):
        item_emoji = ITEM_EMOJIS.get(item, "")
        if price > 0:
            price = format(price, ",d").replace(",", ".")
            print(f"{key}. Buy {item} {item_emoji} for {price} coins each")
        else:
            print(f"{key}. {item}")


def get_player_choice():
    """Gets the player's menu choice and validates it."""
    try:
        choice = input("What would you like to get?: ").strip().lower()
        if choice in ["l", "q"]: # (l)eave or (q)uit
            return "leave"
        elif not choice.isdigit() and len(choice) > 3: # If the input is not a number and longer than 3 characters (probably a item name)
            # Then it is possibly a string with the item name is given, check if the choice is in the item names.
            for key, (item, price) in enumerate(pokemart_items, 1):
                if choice in item.lower():
                    return key - 1

        choice = int(choice) - 1
        if choice < 0 or choice >= len(pokemart_items):
            raise ValueError("Invalid choice. Please select a valid item.")
        return choice
    except (ValueError, TypeError):
        print("Invalid input. Please try again.")
        return None


def handle_purchase_confirmation(player, item_name, item_price, quantity):
    """Handles the confirmation and execution of the item purchase."""
    total_cost = item_price * quantity

    print(f"Are you sure you want to buy {quantity} {item_name} for {total_cost} coins?")
    print(f"You have currently {player.get_coins()} coins.")
    confirm = player.yes_no_question("Confirm?")

    if confirm:
        if player.get_coins() < total_cost:
            print(f"You don't have enough coins to buy {item_name}.")
            return False
        # Update player data
        player.set_coins(total_cost, "subtract")
        player.set_inventory_item(item_name, quantity)
        print(f"Thank you for purchasing {quantity} {item_name}(s) for {total_cost} coins!")
        return True
    else:
        print("You changed your mind? Can I help you with something else.")
        return False


def handle_item_purchase(player, choice):
    """Handles the process of purchasing an item from the PokéMart."""
    item_name, item_price = pokemart_items[choice]
    quantity = input(f"How many {item_name} would you like to buy?: ").strip()

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError()

        return handle_purchase_confirmation(player, item_name, item_price, quantity)
    except ValueError:
        print("The given quantity is incorrect. Please give a valid amount.")
        return False


def pokemart_buy(player):
    """Facilitates the item buying process in the PokéMart."""
    shopping = True
    while shopping:
        display_menu()
        choice = get_player_choice()
        if choice == "leave":
            print("Thank you for visiting the PokéMart!")
            shopping = False
        elif choice is not None:
            if choice == len(pokemart_items) - 1:  # Last item is to leave
                print("Thank you for visiting the PokéMart!")
                shopping = False
            else:
                handle_item_purchase(player, choice)


def handle_item_sale(player, item, quantity, price_per_item):
    """Handles the sale of an item and updates the player's inventory and coins."""
    total_earnings = price_per_item * quantity
    player.set_coins(total_earnings, "add")
    player.set_inventory_item(item, quantity, "subtract")
    print(f"Thank you for selling {quantity} {item}(s) for {total_earnings} coins!")


def pokemart_sell(player):
    """Facilitates the item selling process in the PokéMart."""
    item = player.select_item_from_bag()
    if not item:
        print("Thank you for visiting the PokéMart!")
        return

    # Get the price of the item, first check if it's in pokemart_items, then in pokemart_sell_items
    try:
        sellable_items = pokemart_items + pokemart_sell_items
        price_per_item = next(price for name, price in sellable_items if name == item) * SELL_RATE
    except StopIteration:
        print("This item is not sellable.")
        return

    # Prompt player for quantity and display the price information
    quantity = input(f"How many {item} would you like to sell? (Price per {item}: {price_per_item} coins): ").strip()

    try:
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        total_earnings = price_per_item * quantity
        confirm = player.yes_no_question(
            f"Are you sure you want to sell {quantity} {item}(s) for {total_earnings} coins?")
        if confirm:
            handle_item_sale(player, item, quantity, price_per_item)
        else:
            print("You changed your mind? Can I help you with something else.")
    except ValueError:
        print("Invalid quantity. Please try again.")


def show_pokemart_menu(player):
    """Displays the PokéMart menu and directs the player to buy or sell."""
    print(f"Hi {player.get_name()}! Welcome to the PokéMart! I see you have {player.get_coins()} coins.")
    print("\nHow can I help you today?")
    choice = player.multiple_choice_question("Do you want to:", ["Buy", "Sell", "Leave"], False)

    if choice == "Buy":
        pokemart_buy(player)
    elif choice == "Sell":
        pokemart_sell(player)


def show_pokecenter_menu(player):
    """Displays the Pokémon Center menu."""
    print(f"\nWelcome to the Pokémon Center, {player.get_name()}!")
    choice = player.yes_no_question("Do you want to view your Pokémon?")

    if choice:
        player.show_pokemon_list()
    else:
        print("Thank you for visiting the Pokémon Center!")

def show_professor_house_menu():
    """Displays the Professor's house menu."""
    print("You entered the Professor's lab!")
    time.sleep(1)
    print('...', end='')
    time.sleep(1)
    print(' ...', end='')
    time.sleep(1)
    print(' ...')
    time.sleep(1)
    print('The professor is not here')
    time.sleep(1)
    print('Looks like you have to come back in a later version of this game.')
    time.sleep(1.5)