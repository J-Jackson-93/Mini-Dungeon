#This file is for the healing room descriptions. This will be a procedural file to make a quick random lookup for the description.
import random

def healing_room_description():
    hr = ["A hot pool sits in the center with runes etched into the sides to promote healing and safety.",
          "An alter of gold sits at the front of the room with a golden light shining on it from above.",
          "A hooded figure waits and as you approach the figure lifts its head to you and a calmness falls over you."
          "Along the walls are multiple bunk beds and the doors have worn braces to keep them shut."]
    choice = random.randint(1,4)
    return hr[choice]

def special_room_description():
    sr = ["As the door shuts the walls turn to golden bricks and the floor becomes grass almost as if an illusion is melting away.",
          "A hooded figure waits in the room and as you approach he slowly lifts his hand to reach out to you and upon touching you, it imbues you with power."]
    choice = random.randint(1,2)
    return sr[choice]