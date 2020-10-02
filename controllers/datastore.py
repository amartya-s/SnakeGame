import pickle


class DataStore:
    def __init__(self, inst):
        self.inst = inst
        self.player = self.bombs = []
        self.food = None
        self.score = 0
        self.file = "datastore-{}.txt".format(self.inst)

    def load(self):
        obj = None
        with open(self.file, 'a+') as f:
            obj = pickle.load(f)

        if obj:
            self.player = obj.player
            self.bombs = obj.bombs
            self.food = obj.food
            self.score = obj.score

    def update(self, player, bombs, food, score):
        self.player = player
        self.bombs = bombs
        self.food = food
        self.score = score

        self.save()

    def save(self):
        with open(self.file, 'w') as f:
            pickle.dump(self, f)


class DataStoreManager:
    def __init__(self, inst):
        self.inst = inst
        self.datastore_obj = DataStore(self.inst)

    def update(self, player, bombs, food, score):
        self.datastore_obj.update(player, bombs, food, score)

    def get_player(self):
        return self.datastore_obj.player

    def get_bombs(self):
        return self.datastore_obj.bombs

    def get_food(self):
        return self.datastore_obj.food

    def get_score(self):
        return self.datastore_obj.score
