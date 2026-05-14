import random
from PlayerData import Player
from MonsterData import Monster
import Leveling


def battle(player, monster, difficulty):
    while (player.is_alive() and monster.is_alive()):
        if player.is_alive():
            print(f"{player.name} is attacking {monster.name}.")
            dmg_multiplier = (100 + random.randint(0, 20)) / 100
            dmg = int(player.attack * dmg_multiplier)
            monster.hp -= dmg
            print(f"{monster.name} takes {dmg} damage. HP: {monster.hp}")
            if not monster.is_alive():
                print(f"{player.name} has slain {monster.name}.")
                player.attack += difficulty
                player.xp += monster.xp
                level_up(player)
                break
        if monster.is_alive():
            print(f"{monster.name} is attacking {player.name}.")
            dmg_multiplier = (100 + random.randint(0, 15)) / 100
            dmg = int(monster.attack * dmg_multiplier)
            player.hp -= dmg
            print(f"{player.name} takes {dmg} damage. HP: {player.hp}")
            if not player.is_alive():
                print(f"{monster.name} has slain {player.name}.")
                player.xp -= monster.xp
                if player.xp < 0:
                    player.xp = 0
                break
        input()
    if not player.is_alive() and not monster.is_alive():
        print(f"By some miracle both {player.name} and the {monster.name} died.")


def main():
    p1 = Player(input("What is the player's name?"))
    difficulty = int(input("How hard would you like the game to be? 1 (easiest) -> 10 (hardest)"))
    while (isinstance(difficulty, int) and (difficulty > 10 or difficulty < 1)):
        difficulty = int(input("Error: difficulty must be between 1 and 10."))
    room_total = int(input("How many rooms would you like?"))
    for i in range(room_total):
        if p1.is_alive():
            print(f"\nRoom {i + 1} of {room_total}")
            generate_room(p1, difficulty)
        else:
            print("Game over.")
            break

def generate_room(p1, difficulty):
    #Generate the rooms randomly using base enemies and weights for healing
    heal_chance = 25 - ((difficulty - 1) * 4 )
    room_code = random.randint(1, 100)
    if room_code <= heal_chance and not room_code == 100:
        if p1.hp == 100:
            print(f"{p1.name} health is full.")
        elif p1.hp + 25 <= 100:
            p1.heal(25)
        elif p1.hp + 25 > 100:
            p1.heal(100 - p1.hp)
        print(f"{p1.name} heals 25 health. HP: {p1.hp}")
    elif room_code == 100:
        print(f"{p1.name} restored to full health and gained 25 experience points.\n{p1.name} experience: {p1.xp}")
        p1.hp = 100
        p1.xp += 25
        level_up(p1)
    else:
        if difficulty <= 3:
            m1 = Monster("Goblin")
        elif difficulty <= 5:
            temp = random.randint(1, 2)
            if temp == 1:
                m1 = Monster("Goblin")
            elif temp == 2:
                m1 = Monster("Demon")
        elif difficulty <= 10:
            temp = random.randint(1, 3)
            if temp == 1:
                m1 = Monster("Goblin")
            elif temp == 2:
                m1 = Monster("Demon")
            elif temp == 3:
                m1 = Monster("Demigod")
        elif difficulty == 10:
            temp = random.randint(1, 4)
            if temp == 1:
                m1 = Monster("Goblin")
            elif temp == 2:
                m1 = Monster("Demon")
            elif temp == 3:
                m1 = Monster("Demigod")
            elif temp == 4:
                m1 = Monster("God")
        battle(p1, m1, difficulty)

def level_up(player):
    if player.xp >= Leveling.xp_by_level[player.level]:
        player.level += 1
        player.attack += Leveling.stat_increase[player.level]
        print(f"{player.name} leveled up! You are now level {player.level} and your attack went up by {Leveling.stat_increase[player.level]}")


main()