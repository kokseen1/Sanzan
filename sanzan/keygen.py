import numpy as np


class Keygen:
    def __init__(self, seed=None) -> None:
        self.rng = None
        self.seed = seed
        if seed is not None:
            self.seed = bytearray(self.seed, "utf8")

        self.reseed()

    def reseed(self):
        self.rng = np.random.RandomState(self.seed)

    def generate_key(self, length, reseed):
        shuf_order = np.arange(length)
        if reseed:
            self.reseed()
        self.rng.shuffle(shuf_order)
        if reseed:
            self.reseed()

        return shuf_order

    def _generate_rev_key(self, shuf_order):
        unshuf_order_x = np.zeros_like(shuf_order)
        unshuf_order_x[shuf_order] = np.arange(len(shuf_order))

        return unshuf_order_x

    def generate_rev_key(self, length, reseed):
        shuf_order = self.generate_key(length, reseed)

        return self._generate_rev_key(shuf_order)
