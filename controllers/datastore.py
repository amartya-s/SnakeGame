import os
import pickle
import json

from SnakeGame.constants.game_params import GameParams


class DataStore:
    def __init__(self, inst):
        self.inst = inst
        self.player = self.bombs = []
        self.food = None
        self.foods_with_timer = []
        self.score = 0
        self.file = "{}\\game-{}.txt".format(GameParams.DATASTORE_FILE_PATH,self.inst)

    def load(self):
        obj = None
        with open(self.file, 'rb') as f:
            try:
                obj = pickle.load(f)
            except EOFError:
                obj = None

        if obj:
            self.player = obj.player
            self.bombs = obj.bombs
            self.food = obj.food
            self.score = obj.score
            self.foods_with_timer = obj.foods_with_timer

            return True

        return False

    def update(self, player, bombs, food, foods_with_timer, score):
        self.player = player
        self.bombs = bombs
        self.food = food
        self.foods_with_timer = foods_with_timer
        self.score = score
        self.save()

    def save(self):
        with open(self.file, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)


class DataStoreManager:
    game_list_file = "{}\\game-list".format(GameParams.DATASTORE_FILE_PATH)

    def __init__(self, inst):
        self.inst = inst
        self.datastore_obj = None

    @staticmethod
    def get_saved_games():
        if not os.path.exists(DataStoreManager.game_list_file):
            f=open(DataStoreManager.game_list_file, 'w+')
            json.dump([], f)
            return []
        else:
            game_list = json.load(open(DataStoreManager.game_list_file, 'r+'))
            return game_list

    def update(self, player, bombs, food, foods_with_timer, score):
        self.datastore_obj = DataStore(self.inst)
        self.datastore_obj.update(player, bombs, food, foods_with_timer, score)

        saved_games = DataStoreManager.get_saved_games()
        if self.inst not in saved_games:
            saved_games.append(self.inst)
        json.dump(saved_games, open(DataStoreManager.game_list_file, 'w'))

    def load(self):
        self.datastore_obj = DataStore(self.inst)
        return self.datastore_obj.load()

    def get_player(self):
        return self.datastore_obj.player

    def get_bombs(self):
        return self.datastore_obj.bombs

    def get_food(self):
        return self.datastore_obj.food

    def get_foods_with_timer(self):
        return self.datastore_obj.foods_with_timer

    def get_score(self):
        return self.datastore_obj.score
