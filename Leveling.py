class Leveling:

    xp_by_level = [0, 10, 25, 75, 225, 675, 2025]
    stat_increase = [0, 0, 2, 3, 3, 4, 5]

    def increase_player_stats(player, points):
        #Increase _max_hp and attack. Then fully restore hp and print new attack and hp.
        player._max_hp += 5 * points
        player.attack += points
        player.current_hp = player._max_hp
        print(player)

    def level_up(self, player):
        if player.xp >= self.xp_by_level[player.level]:
            if self.stat_increase[player.level] > 0:
                self.increase_player_stats(player, self.stat_increase[player.level])
