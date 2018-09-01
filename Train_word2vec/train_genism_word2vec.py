from gensim.models import word2vec
import logging
from tqdm import tqdm
import MeCab
import os
import sys
import time


class GenismWord2vec:
    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.output_dir = output_dir

    def make_data(self, new_data_path):
        print("wikipediaデータの書き込みを始めます。")
        def iter_docs(file):
            for line in file:
                if line.startswith("<doc"):
                    buffer = []
                elif line.startswith("</doc>"):
                    content = "".join(buffer)
                    yield content
                else:
                    buffer.append(line)

        new_data = open(new_data_path, "w")
        total_content_num = 0
        with open(self.data_dir, encoding="utf-8") as file:
            for i, content in tqdm(enumerate(iter_docs(file))):
                total_content_num += 1
                new_data.write(content)
        print("wikipediaデータの書き込みを終了しました。総文章数は、{}です。".format(total_content_num))
        self.data_dir = new_data_path

    def wakati(self):
        print("データの分かち書きの書き込みを開始します。")
        tagger = MeCab.Tagger('-F\s%f[6] -U\s%m -E\\n')
        fi = open(self.data_dir, "r")
        fo = open(os.path.join(self.output_dir, "wiki_data.txt"), "w")
        line = fi.readline()
        total_line_num = 0
        while line:
            total_line_num += 1
            result = tagger.parse(line)
            fo.write(result[1:])
            line = fi.readline()
        fi.close()
        fo.close()
        print("データの分かち書きの書き込みを終了しました。総文章数は、{}です。".format(total_line_num))

    def model(self):
        print("word2vecモデルの実行を始めます。")
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        sentences = word2vec.LineSentence(os.path.join(self.output_dir, "wiki_data.txt"))
        model = word2vec.Word2Vec(sentences,
                                  sg=1,         # sgは0でCBOW, 1でskip-gramモデルを学習する。
                                  size=500,     # sizeは単語の次元を表す。
                                  workers=5,    # workerは用いるスレッド数の指定
                                  min_count=10, # min_countは頻出しない単語を決定する。
                                  window=10,    # windowは予測に使用する単語数
                                  hs=0,         # hsは0)で負例サンプリング, 1)で階層ソフトマックス法を用いる。
                                  negative=10)  # negativeは負例サンプルの数を示す。

        model.save(os.path.join(self.output_dir, "model_example.model"))
        print("word2vecモデルの実行を終了します。")

    def similarity(self, input_word):
        print("word2vecモデルの検証を開始します。")
        model = word2vec.Word2Vec.load(os.path.join(self.output_dir, "model_example.model"))
        results = model.most_similar(positive=input_word, topn=10)

        for result in results:
            print("{}\t{}".format(result[0], result[1]))


if __name__=="__main__":
    if sys.argv[1] == "--train":
        print("process is initializing.....")
        start = time.time()
        data_dir = r"/home/tomoya/Downloads/articles/AA/wiki_00"
        output_dir = r"/home/tomoya/Downloads/temp_data"
        model = GenismWord2vec(data_dir=data_dir, output_dir=output_dir)
        model.make_data(new_data_path=r"/home/tomoya/Downloads/temp_data/wiki_00_data.txt")
        model.wakati()
        model.model()
        model.similarity("ローマ")
        process_time = time.time() - start
        print("finished all processes, it takes {}seconds".format(process_time))

    elif (sys.argv[1] == "--eval")and(isinstance(sys.argv[2], str)):
        print("process is initializing.....")
        start = time.time()
        data_dir = r"/home/tomoya/Downloads/articles/AA/wiki_00"
        output_dir = r"/home/tomoya/Downloads/temp_data"
        model = GenismWord2vec(data_dir=data_dir, output_dir=output_dir)
        model.similarity(sys.argv[2])
        process_time = time.time() - start
        print("finished all processes, it takes {}seconds".format(process_time))

    else:
        raise ValueError("""please confirm your arguments""")
