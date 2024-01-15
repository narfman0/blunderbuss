class Level:
    def __init__(self, level_name="1"):
        f = open(f"data/levels/{level_name}.txt")
        self.tile_data = [[int(c) for c in row] for row in f.read().split("\n")]
        f.close()