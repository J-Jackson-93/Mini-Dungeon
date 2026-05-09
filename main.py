import random

#Python Class
class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.attack = 15

    def is_alive(self):
        if (self.hp > 0):
            return True
        else:
            return False

    def take_damage(self, dmg):
        self.hp -= dmg
        print(f"{self.name} takes {dmg} damage.")

    def heal(self, amount):
        self.hp += amount

    def __str__(self):
        print(f"{self.name} | HP: {self.hp} | Attack: {self.attack}")

class Monster:
    def __init__(self, name):
        self.name = name
        if (name == "Goblin"):
            self.hp = 50
            self.attack = 5
        elif (name == "Demon"):
            self.hp = 100
            self.attack = 10
        elif (name == "Demigod"):
            self.hp = 150
            self.attack = 15
        elif (name == "God"):
            self.hp = 200
            self.attack = 20

    def is_alive(self):
        if (self.hp > 0):
            return True
        else:
            return False

    def __str__(self):
        print(f"{self.name} | Type: {self.type} | HP: {self.hp} | Attack: {self.attack}")

def battle(player, monster):
    while (player.is_alive() and monster.is_alive()):
        if (player.is_alive()):
            print(f"{player.name} is attacking {monster.name}.")
            dmg_multiplier = (100 + random.randint(0, 20)) / 100
            dmg = int(player.attack * dmg_multiplier)
            monster.hp -= dmg
            print(f"{monster.name} takes {dmg} damage. HP: {monster.hp}")
            if (not monster.is_alive()):
                print(f"{player.name} has slain {monster.name}.")
                break
        if (monster.is_alive()):
            print(f"{monster.name} is attacking {player.name}.")
            dmg_multiplier = (100 + random.randint(0, 15)) / 100
            dmg = int(player.attack * dmg_multiplier)
            player.hp -= dmg
            print(f"{player.name} takes {dmg} damage. HP: {player.hp}")
            if (not player.is_alive()):
                print(f"{monster.name} has slain {player.name}.")
                break
        input()
    if (not player.is_alive() and not monster.is_alive()):
        print(f"By some miracle both {player.name} and the {monster.name} died.")

def has_next(p1):
    if (p1.hp > 0):
        return True
    else:
        return False

def main():
    p1 = Player(input("What is the player's name?"))
    difficulty = int(input("How hard would you like the game to be? 1 (easiest) -> 10 (hardest)"))
    while (isinstance(difficulty, int) and (difficulty > 10 or difficulty < 1)):
        difficulty = int(input("Error: difficulty must be between 1 and 10."))
    room_total = int(input("How many rooms would you like?"))
    for i in range(room_total):
        print(f"\nRoom {i+1} of {room_total}")
        if (has_next(p1)):
            generate_room(p1, difficulty)
        elif (not has_next(p1)):
            print("Game over.")
            break

def generate_room(p1, difficulty):
    #Generate the rooms randomly using base enemies and weights for healing
    heal_chance = 25 - ((difficulty - 1) * 4 )
    room_code = random.randint(1, 100)
    if (room_code <= heal_chance and not room_code == 100):
        if ((p1.hp + 25) <= 100):
            p1.heal(25)
        elif((p1.hp + 25) > 100):
            p1.heal(100 - p1.hp)
        print(f"{p1.name} heals 25 health. HP: {p1.hp}")
    elif (room_code == 100):
        print(f"{p1.name} restored to full health and gained 5 attack points.")
        p1.hp = 100
        p1.attack += 5
    else:
        if (difficulty <= 3):
            m1 = Monster("Goblin")
            battle(p1, m1)
        if (difficulty > 3 and difficulty <= 5):
            temp = random.randint(1, 2)
            if (temp == 1):
                m1 = Monster("Goblin")
            elif (temp == 2):
                m1 = Monster("Demon")
            battle(p1, m1)
        if (difficulty > 5 and difficulty < 10):
            temp = random.randint(1, 3)
            if (temp == 1):
                m1 = Monster("Goblin")
            elif (temp == 2):
                m1 = Monster("Demon")
            elif (temp == 3):
                m1 = Monster("Demigod")
            battle(p1, m1)
        if (difficulty == 10):
            temp = random.randint(1, 4)
            if (temp == 1):
                m1 = Monster("Goblin")
            elif (temp == 2):
                m1 = Monster("Demon")
            elif (temp == 3):
                m1 = Monster("Demigod")
            elif (temp == 4):
                m1 = Monster("God")
            battle(p1, m1)
main()