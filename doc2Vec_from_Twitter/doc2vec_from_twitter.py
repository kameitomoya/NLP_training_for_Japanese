from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import numpy as np
import smart_open
import pymongo
import os
from pprint import pprint
import mojimoji
import emoji
import re
from tqdm import tqdm
import requests
import MeCab


class GensimDoc2Vec:
    def __init__(self, data_dir):
        slothlib_path = \
            r"http://svn.sourceforge.jp/svnroot/slothlib/CSharp/Version1/SlothLib/NLP/Filter/StopWord/word/Japanese.txt"
        slothlib_file = requests.get(slothlib_path).text
        slothlib_stopwords = slothlib_file.split("\r\n")
        self.data_dir = data_dir
        self.stopwords = slothlib_stopwords

    def make_file_by_mongodb(self, section, keywords):
        print("mongodb_{}から以下のキーワードでファイルの出力を開始します。".format(section))
        pprint(keywords)

        os.chdir(self.data_dir)
        client = pymongo.MongoClient()
        db = client["collect_data"]
        collection = db[section]
        for keyword in keywords:
            file_name = "{}.txt".format(keyword.replace(" ", "_"))
            print(file_name)
            with open(file_name, "w", encoding="UTF-8") as text:
                for value in collection.find({"keyword": keyword}).sort('id', pymongo.DESCENDING):
                    text.write(value["text"] + "\n")
            print("キーワード{}の出力を{}に完了しました".format(keyword, file_name))
        print("出力を完了しました。")
        pprint(os.listdir(self.data_dir))

    def format_data(self):
        def format_line(base_string):
            """英字をすべて小文字へ, 半角を全角へ、#〜や@~を削除, URLを削除, 日付の削除"""
            small_string = base_string.lower()
            zen_string = mojimoji.zen_to_han(small_string, digit=False, kana=False)
            han_string = mojimoji.han_to_zen(zen_string, digit=False, ascii=False)
            formatted_string = "".join(c for c in han_string if c not in emoji.UNICODE_EMOJI)
            patterns = [r"@\w*", r"#(\w+)", r"(http(s)?(:)?//[\w | /]*)"]
            for replace in ["'", '"', ';', '.', ',', '-', '!', '?', '=', "(", ")", "「", "」", "|", "『", "』"]:
                formatted_string = formatted_string.replace(replace, "")

            for pattern in [re.compile(i) for i in patterns]:
                formatted_string = re.sub(pattern, "", formatted_string)
            return formatted_string

        print("文書の正規化を始めます。")
        os.chdir(self.data_dir)
        data_list = [i for i in os.listdir(self.data_dir) if ("txt" in i.split(".") and
                                                              "formatted" not in i.split("_"))]
        for file_name in tqdm(data_list):
            new_file_name = str(file_name.split(".")[0]) + '_formatted.txt'
            w_file = open(new_file_name, "a")
            with open(file_name, "r", encoding="UTF-8") as r_file:
                base_line = r_file.readlines()
                for base_string in base_line:
                    f_string = format_line(base_string)
                    w_file.write(f_string)
                w_file.close()

        print("文書の正規化を終了します。")
        pprint(os.listdir(self.data_dir))

    def wakati(self):
        print("データの分かち書きを始めます。")
        os.chdir(self.data_dir)
        data_list = [i for i in os.listdir(self.data_dir) if ("txt" in i.split(".") and
                                                              "formatted.txt" in i.split("_"))]
        for file_name in tqdm(data_list):
            new_file_name = str(file_name.split(".")[0]) + '_wakati.txt'
            w_file = open(new_file_name, "w")
            with open(file_name, "r") as r_file:
                tagger = MeCab.Tagger('-F\s%f[6] -U\s%m -E\\n')
                r_line = r_file.readline()
                while r_line:
                    result = tagger.parse(r_line)
                    rm_result = [i for i in result[1:].split(" ") if not i in self.stopwords]
                    w_file.write(" ".join(rm_result))
                    r_line = r_file.readline()
            w_file.close()

    def train_model(self, dm, vector_size, min_count, workers, negative, sample, window):
        train_corpus = list(self.read_corpus())
        print("corpusの作成を終了します。")
        print("モデルの学習を始めます。")
        data_list = [i for i in os.listdir(self.data_dir) if "wakati.txt" in i.split("_")]
        tag_name = []
        for file_name in data_list:
            tag_name.append("_".join([str(i) for i in file_name.split("_")
                                 if (i not in ["normed", "wakati.txt", "wakati", "formatted"])]))
        model = Doc2Vec(dm=dm, vector_size=vector_size, min_count=min_count, epochs=100,
                        workers=workers, negative=negative, sample=sample, window=window)
        model.build_vocab(train_corpus)
        model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)
        model.save(os.path.join(self.data_dir, "model.pk"))

    def calc_similarity(self):
        pass

    def calc_ubow(self):
        pass

    def calc_hbc(self):
        pass

    def read_corpus(self):
        print("corpusを作成しています。")
        os.chdir(self.data_dir)
        data_list = [i for i in os.listdir(self.data_dir) if "wakati.txt" in i.split("_")]
        for file_name in data_list:
            tag_name = "_".join([str(i) for i in file_name.split("_")
                                 if (i not in ["normed", "wakati.txt", "wakati", "formatted"])])
            print(tag_name)
            with smart_open.smart_open(file_name, encoding="UTF-8") as f:
                for i, line in enumerate(f):
                    yield TaggedDocument(line, tag_name)


if __name__ == '__main__':
    pass