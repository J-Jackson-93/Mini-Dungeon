import torch
import torch.nn.functional as F
import random


class Dungeon_Master:
    def __init__(self):
        self.room_type = 1
