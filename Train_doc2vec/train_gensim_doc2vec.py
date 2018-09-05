import sys
from Train_word2vec.train_gensim_word2vec import GensimWord2vec


class GensimDoc2vec(GensimWord2vec):
    def __init__(self, data_dir, output_dir):
        super().__init__(data_dir=data_dir, output_dir=output_dir)

    def make_data(self, new_data_path):
        pass

    def wakati(self):
        pass

    def model(self):
        pass

    def similarity(self, word):
        pass


if __name__=="__main__":
    if "--train" in sys.argv or "--t" in sys.argv:
        pass

    elif "--eval" in sys.argv or "--e" in sys.argv:
        pass

    else:
        raise ValueError("you have to check your arguments!")

