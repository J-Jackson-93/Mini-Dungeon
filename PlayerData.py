#Python Class
class Player:
    def __init__(self, name):
        self.name = name
        self.current_hp = 100
        self._max_hp = 100
        self.armor = 10
        self.attack = 15
        self.magic = 5
        self.xp = 0
        self.level = 1

    def is_alive(self):
        if (self.current_hp > 0):
            return True
        else:
            return False

    def take_damage(self, dmg):
        self.current_hp -= dmg
        print(f"{self.name} takes {dmg} damage.")

    def heal(self, amount):
        self.current_hp += amount

    def __str__(self):
        return f"{self.name} | HP: {self.current_hp} / {self._max_hp} | Attack: {self.attack} | Magic: {self.magic} | Armor: {self.armor} | Exp: {self.xp}"