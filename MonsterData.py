class Monster:
    def __init__(self, name):
        self.name = name
        if (name == "Goblin"):
            self.hp = 50
            self.attack = 5
            self.xp = 5
        elif (name == "Demon"):
            self.hp = 100
            self.attack = 10
            self.xp = 10
        elif (name == "Demigod"):
            self.hp = 150
            self.attack = 15
            self.xp = 15
        elif (name == "God"):
            self.hp = 200
            self.attack = 20
            self.xp = 20

    def is_alive(self):
        if (self.hp > 0):
            return True
        else:
            return False

    def __str__(self):
        print(f"{self.name} | Type: {self.type} | HP: {self.hp} | Attack: {self.attack}")