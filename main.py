import random

#Python Class
class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.attack = 15

    def set_name(self, name):
        self.name = input("What is the player's name?")

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
        rnd = random.randint(1, 3)
        if (rnd == 1):
            self.name = "Goblin"
            self.hp = 50
            self.attack = 5
        elif (rnd == 2):
            self.type = "Demon"
            self.hp = 100
            self.attack = 10
        elif (rnd == 3):
            self.type = "God"
            self.hp = 250
            self.attack = 15

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