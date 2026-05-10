from collections import defaultdict

class Dungeon_Master():
    def __init__(self, filepath):
        self.lines = open(filepath).readlines()
        self.bigram = {}
        self.train()

    def train(self):
        lines = [line.strip() for line in open ("rooms.txt").readlines()]
        bigram = defaultdict(defaultdict)
        for line in lines[1:]:
            words = ["<S>"] + line.split() + ["</E>"]
            for w1, w2 in zip(words + words[1:]):
                bigram[w1][w2] += 1