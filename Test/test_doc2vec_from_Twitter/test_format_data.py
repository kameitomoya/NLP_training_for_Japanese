import sys, os

sys.path.append("../..")
from doc2Vec_from_Twitter.doc2vec_from_twitter import GensimDoc2Vec


def test_format_data(data_dir):
    print("テストを開始します。")
    inst = GensimDoc2Vec(data_dir=data_dir)
    inst.format_data()
    print("テストを終了します。")


if __name__ == '__main__':
    data_dir_tmp = r"/home/tomoya/PycharmProjects/preprocess_NLP/data/doc2vec"
    test_format_data(data_dir_tmp)