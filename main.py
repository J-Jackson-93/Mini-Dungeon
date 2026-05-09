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
        print(f"{self.name} heals {amount} hp.")

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
            dmg = player.attack * (random.randint(-15,15) / 100 )
            print(f"{monster.name} takes {dmg} damage.")
        if (monster.is_alive()):
            dmg = monster.attack * (random.randint(-20, 20) / 100)
            print(f"{player.name} takes {dmg} damage.")
    if (player.is_alive() and not monster.is_alive()):
        return True
    if (not player.is_alive() and monster.is_alive()):
        return False
    if (not player.is_alive() and not monster.is_alive()):
        print(f"By some miracle both the player and the {monster.name} died.")

def main():
    p1 = Player(input("What is the player's name?"))
    difficulty = input("How hard would you like the game to be? 1 (easiest) -> 10 (hardest)")
    while (not isinstance(difficulty, float) or not (difficulty <= 10 and difficulty >= 1)):
        print("Error: The number must be between 1 and 10.")
        difficulty = input("How hard would you like the game to be? 1 (easiest) -> 10 (hardest)")

    #Generate the rooms randomly using base enemies and weights for healing
    heal_chance = 50 - ((difficulty - 1) * 4 )
    room_code = random.randint(1, 100)
    if (room_code <= heal_chance):
        p1.heal += 25
    else:
        if (difficulty <= 3):
            battle(p1, )


