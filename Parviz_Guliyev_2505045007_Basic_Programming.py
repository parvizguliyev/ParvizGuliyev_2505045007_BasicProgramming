import time
import json
import random

# --- Game State ---
location = "airlock"
inventory = []
hp = 100
in_combat = False
current_enemy = None
enemy_hp = 0
engine_room_unlocked = False
control_room_lit = False

# --- Player Setup ---
player_name = input("Enter your character name: ")
while True:
    try:
        hp = int(input("Enter your starting HP (50–150): "))
        if 50 <= hp <= 150:
            break
        else:
            print("HP must be between 50 and 150.")
    except ValueError:
        print("Please enter a valid number.")

# --- Rooms and Items ---
rooms = {
    "airlock": {"north": "corridor", "item": []},
    "corridor": {"south": "airlock", "east": "lab", "west": "storage", "item": []},
    "lab": {
        "west": "corridor", "north": "control zone",
        "item": ["gas mask", "access ID", "cable"],
        "descriptions": {
            "oxygen tank": "A tank filled with oxygen. You can breathe again.",
            "access card": "A card that grants access to secure areas.",
            "cable": "A power cable. Might help turn on the lights."
        }
    },
    "storage": {
        "east": "corridor", "north": "engine room",
        "item": ["wrench", "engine key"],
        "descriptions": {
            "wrench": "A heavy wrench. Maybe it can fix something.",
            "engine key": "A key labeled 'Engine Room'. Must unlock something."
        }
    },
    "engine room": {
        "south": "storage", "east": "control room",
        "item": [],
        "descriptions": {
            "fuel cell": "A glowing power unit. Very valuable.",
            "alien": "A dangerous alien creature. Stay away!",
            "robot": "one of the most dangerous robot in the world."
        }
    },
    "control room": {
        "west": "engine room", "south": "lab",
        "item": ["laser gun"],
        "descriptions": {
            "laser gun": "A weapon that can kill alien threats."
        }
    }
}

enemies = {
    "alien": {"hp": 60, "attack": 20},
    "robot": {"hp": 80, "attack": 25}
}

# --- Utility ---
def slow_print(text, delay=0.04):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(delay)
    print()

def show_map():
    print("""
          [Control Room]
               ↑
       [Lab] ← [Corridor] → [Storage]
               ↓               ↑
           [Airlock]     [Engine Room]
    """)

# --- Commands ---
def look():
    if location == "control room" and not control_room_lit:
        print("It's too dark to see anything.")
        return
    items = rooms[location].get("item", [])
    if items:
        print("You see:")
        for i in items:
            print("-", i)
    else:
        print("The room is empty.")

def examine(item):
    if item in inventory:
        print("you see it in your inventory. Looks useful.")
    elif item in rooms[location].get("item", []):
        desc = rooms[location].get("descriptions", {}).get(item)
        if desc:
            print(desc)
        else:
            print("Nothing special about it.")
    else:
        print("You don't see that here.")

def show_inventory():
    if inventory:
        print("You are carrying:")
        for item in inventory:
            print("-", item)
    else:
        print("Your inventory is empty.")

def take(item):
    if item in rooms[location].get("item", []):
        inventory.append(item)
        rooms[location]["item"].remove(item)
        print(f"Picked up {item}.")
    else:
        print(f"There is no {item} here.")

def go(direction):
    global location
    if location == "storage" and direction == "north" and not engine_room_unlocked:
        print("The door is locked. You need a key to open it.")
        return
    if direction in rooms[location]:
        location = rooms[location][direction]
        print(f"You moved to {location}.")
    else:
        print("You can't go there.")

def use(item):
    global hp, engine_room_unlocked, control_room_lit
    if item not in inventory:
        print("You don't have that item.")
        return
    if item == "oxygen tank":
        hp = min(100, hp + 30)
        inventory.remove(item)
        print(f"You used the oxygen tank. Health is now {hp}.")
    elif item == "wrench":
        if location == "engine room":
            print("You fixed something with the wrench!")
        else:
            print("You can't use it here.")
    elif item == "engine key":
        if location == "storage":
            engine_room_unlocked = True
            inventory.remove("engine key")
            print("You unlocked the engine room door!")
        else:
            print("You can't use that here.")
    elif item == "cable":
        if location == "control room":
            control_room_lit = True
            inventory.remove("cable")
            print("You connected the cable. The room lights up!")
        else:
            print("You can't use that here.")
    else:
        print("You can't use that here.")

def attack():
    global enemy_hp, in_combat, current_enemy
    if not in_combat:
        print("You're not in combat.")
        return
    damage = random.randint(10, 30)
    enemy_hp -= damage
    print(f"You attack the {current_enemy} for {damage} damage!")
    if enemy_hp <= 0:
        print(f"You defeated the {current_enemy}!")
        rooms[location]["item"].remove(current_enemy)
        in_combat = False
        current_enemy = None
        enemy_hp = 0
    else:
        retaliate()

def defend():
    if not in_combat:
        print("You're not in combat.")
        return
    reduced = random.randint(5, 15)
    print(f"You brace yourself. damage will be reduced by {reduced}.")
    retaliate(defense=reduced)

def retaliate(defense=0):
    global hp
    if not current_enemy:
        return
    damage = max(0, enemies[current_enemy]["attack"] - defense)
    hp -= damage
    print(f"The {current_enemy} attacks you for {damage} damage! Your HP is now {hp}.")
    if hp <= 0:
        print("You died. Game over.")
        exit()

# --- Game Start ---
slow_print(f"Welcome to the abandoned space station, {player_name}!", 0.06)
slow_print("Type 'load' to load a saved game or press Enter to start a new one.", 0.04)
choice = input("> ")

if choice == "load":
    try:
        with open("savegame.txt", "r") as file:
            data = json.load(file)
            location = data["location"]
            inventory = data["inventory"]
            hp = data["hp"]
            engine_room_unlocked = data.get("engine_room_unlocked", False)
            control_room_lit = data.get("control_room_lit", False)
            rooms.clear()
            rooms.update(data["rooms"])
            slow_print("Game loaded.")
    except FileNotFoundError:
        slow_print("No saved game found. Starting new game.")
    except json.JSONDecodeError:
        slow_print("Save file is corrupt. Starting new game.")
else:
    available_rooms = list(rooms.keys())
    random_rooms = random.sample(available_rooms, len(enemies))
    for i, enemy in enumerate(enemies):
        rooms[random_rooms[i]]["item"].append(enemy)

# --- Game Loop ---
while True:
    slow_print("\nYou are in: " + location)
    slow_print(f"Health: {hp}")
    cmd = input("> ").strip().lower()

    if in_combat:
        if cmd == "attack":
            attack()
        elif cmd == "defend":
            defend()
        else:
            print("You're in combat! Use 'attack' or 'defend'.")
        continue

    if cmd == "look":
        look()
    elif cmd.startswith("examine "):
        examine(cmd[8:])
    elif cmd == "inventory":
        show_inventory()
    elif cmd == "map":
        show_map()
    elif cmd.startswith("take "):
        take(cmd[5:])
    elif cmd.startswith("go "):
        go(cmd[3:])
    elif cmd == "w":
        go("north")
    elif cmd == "s":
        go("south")
    elif cmd == "a":
        go("west")
    elif cmd == "d":
        go("east")
    elif cmd.startswith("use "):
        use(cmd[4:])
    elif cmd == "save":
        if in_combat:
            print("You can't save during combat!")
        else:
            with open("savegame.txt", "w") as file:
                json.dump({
                    "location": location,
                    "inventory": inventory,
                    "hp": hp,
                    "engine_room_unlocked": engine_room_unlocked,
                    "control_room_lit": control_room_lit,
                    "rooms": rooms
                }, file)
            print("Game saved.")
    elif cmd == "help":
        print("Commands: look, take [item], use [item], examine [item], go [direction] (or w/a/s/d), inventory, save, attack, defend, map")
    else:
        print("Unknown command. Type 'help'.")

    for enemy in enemies:
        if enemy in rooms[location].get("item", []):
            slow_print(f"A {enemy} appears with {enemies[enemy]['hp']} HP!")
            in_combat = True
            current_enemy = enemy
            enemy_hp = enemies[enemy]["hp"]
            print("You must fight! Type 'attack' or 'defend'.")
            break

    if location == "airlock" and "access card" in inventory and "oxygen tank" in inventory:
        slow_print("You have what you need to escape.")
        slow_print("You escape the station. Victory!")
        break

slow_print("GAME OVER.", 0.2)
