import hp_format_converter
import random

class DataGenerator:
    FILE = 'raw_data/all_abc.txt'

    def __init__(self, batch_size, num_steps, separate_batches):
        self.batch_size = batch_size
        self.num_steps = num_steps
        self.separate_batches = separate_batches
        self.songs = hp_format_converter.abc_file_to_training_data(self.FILE)
        # for song in self.songs:
        #     print len(song[0])

    def get_batch(self):
        inputs = []
        outputs = []
        for _ in range(batch_size):
            i = None
            o = None
            while i is None:
                i, o = self.get_sequence(random.choice(self.songs))
            inputs.append(i)
            outputs.append(o)
        return inputs, outputs

    def get_train_batch(self):
        if not self.separate_batches:
            return self.get_batch()
        inputs = []
        outputs = []
        for _ in range(self.batch_size):
            i = None
            o = None
            while i is None:
                idx = random.randrange(0, len(self.songs), 2)
                i, o = self.get_sequence(self.songs[idx])
            inputs.append(i)
            outputs.append(o)
        return inputs, outputs

    def get_test_batch(self):
        if not self.separate_batches:
            return self.get_batch()
        inputs = []
        outputs = []
        for _ in range(self.batch_size):
            i = None
            o = None
            while i is None:
                idx = random.randrange(1, len(self.songs), 2)
                i, o = self.get_sequence(self.songs[idx])
            inputs.append(i)
            outputs.append(o)
        return inputs, outputs

    def get_sequence(self, song):
        if self.num_steps > len(song[0]):
            return None, None
        start = random.randint(0, len(song[0]) - self.num_steps)
        return song[0][start:start+self.num_steps], song[1][start:start+self.num_steps]
