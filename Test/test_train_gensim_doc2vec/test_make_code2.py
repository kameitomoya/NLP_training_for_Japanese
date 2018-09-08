import sys, os
sys.path.append("../..")
from Train_doc2vec.train_gensim_doc2vec import GensimDoc2vec

if __name__ == "__main__":
    print("make_dataのテストを開始します。")
    data_dir = r"/home/tomoya/Downloads/aozora/doc2vec"
    output_dir = r"/home/tomoya/Downloads/aozora/train_output"
    new_data_path = r"/home/tomoya/Downloads/aozora/doc2vec/norm_data"
    model = GensimDoc2vec(data_dir=data_dir, output_dir=output_dir)
    model.make_data(new_data_path)