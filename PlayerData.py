#Python Class
class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 100
        self.armor = 10
        self.attack = 15
        self.magic = 5
        self.xp = 0

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
        print(f"{self.name} | HP: {self.hp} | Attack: {self.attack} | Magic: {self.magic} | Armor: {self.armor} | Exp: {self.xp}")