import sys, os

sys.path.append("../..")
from doc2Vec_from_Twitter.doc2vec_from_twitter import GensimDoc2Vec


def test_train_model(data_dir):
    print("テストを開始します。")
    inst = GensimDoc2Vec(data_dir=data_dir)
    dm = 1
    vector_size = 200
    min_count = 20
    workers = -1
    negative = 1
    sample = 1e-3
    window = 10
    inst.train_model(dm=dm, vector_size=vector_size, min_count=min_count, workers=workers,
                     negative=negative, sample=sample, window=window)
    print("テストを終了します。")


if __name__ == '__main__':
    data_dir_tmp = r"/home/tomoya/PycharmProjects/preprocess_NLP/data/doc2vec"
    test_train_model(data_dir_tmp)