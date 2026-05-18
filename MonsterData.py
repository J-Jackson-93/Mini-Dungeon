import random
class Monster:
    def __init__(self, name):
        self.name = name
        if (name == "Goblin"):
            self.hp = 50
            self.attack = 5
            self.xp = 5
            self.description = monster_description_generator(name)
        elif (name == "Demon"):
            self.hp = 100
            self.attack = 10
            self.xp = 10
            self.description = monster_description_generator()
        elif (name == "Demigod"):
            self.hp = 150
            self.attack = 15
            self.xp = 15
            self.description = monster_description_generator()
        elif (name == "God"):
            self.hp = 200
            self.attack = 20
            self.xp = 20
            self.description = monster_description_generator()

    def is_alive(self):
        if (self.hp > 0):
            return True
        else:
            return False

    def __str__(self):
        print(f"{self.name} | Type: {self.type} | HP: {self.hp} | Attack: {self.attack}")

def monster_description_generator(monster_name):
    match monster_name:
        case "Goblin":
            #pick a weapon
            goblin_weapons = ["a stick", "a hammer", "a bloody arm", "a rock", "a rusty sword", "a rusty spear"]
            goblin_clothes = ["a ragged loin cloth", "leather armour", "blood soaked armor", "nothing", "armor that is made for a child"]
            goblin_color = ["sickly green", "clay colored", "light brown", "tan with black stains on its skin", "gray scarred"]

            #Get the length of each list for the random calc
            weapons_choice = random.randint(0, len(goblin_weapons)-1)
            clothes_choice = random.randint(0, len(goblin_clothes)-1)
            color_choice = random.randint(0, len(goblin_color)-1)

            description = f"A {goblin_color[color_choice]} goblin wearing {goblin_clothes[clothes_choice]} and weilding {goblin_weapons[weapons_choice]} attacks."
            return description