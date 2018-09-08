import chardet
import codecs
import sys
import os
import re
import MeCab
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument
from tqdm import tqdm
from Train_word2vec.train_gensim_word2vec import GensimWord2vec


class GensimDoc2vec(GensimWord2vec):
    def __init__(self, data_dir, output_dir):
        super().__init__(data_dir=data_dir, output_dir=output_dir)
        norm_data_dir = os.path.join(data_dir, "norm_data")
        wakati_data_dir = os.path.join(data_dir, "wakati_data")
        self.norm_data_dir = norm_data_dir
        self.wakati_data_dir = wakati_data_dir

        if "norm_data" not in os.listdir(self.data_dir):
            os.mkdir(norm_data_dir)
        if "wakati_data" not in os.listdir(self.data_dir):
            os.mkdir(wakati_data_dir)

    def make_data2(self):
        def norm_sentence(line):
            patterns = [" [.*?] ", "《.*?》", "--", "(.*?)", "――", "［.*?］"]
            for pattern in patterns:
                line = re.sub(pattern, "", line)
            return line

        print("データのエンコード方式の変換と整形を始めます......")
        # データの入ったファイルをリストする。
        data_list = os.listdir(self.data_dir)
        sentence_num = 0
        document_num = 0
        for i, data_temp in enumerate(data_list):
            # ファイルかどうかを判断する。
            if (os.path.isfile(os.path.join(self.data_dir, data_temp))) and ("utf8.txt" not in data_temp.split("_")):
                document_num += 1
                file_name = os.path.join(self.data_dir, data_temp)
                # データがUTF-８かどうかを判断する。
                with open(file_name, "rb") as f:
                    encoding = chardet.detect(f.read())["encoding"]
                # エンコードがUTF-8ではなかった時の処理
                if encoding != "utf-8":
                    print("エンコードされたファイル{}が{}だったため、utf-8に変更します。".format(data_temp, encoding))
                    rename_file_path = str(file_name.split(".")[0]) + "_utf8" + "." + str(file_name.split(".")[1])
                    old_file = codecs.open(file_name, "r", encoding)
                    new_encoded_file = codecs.open(rename_file_path, "w", "utf-8")
                    for row in old_file:
                        new_encoded_file.write(row)
                    old_file.close()
                    new_encoded_file.close()
                    print("エンコードを{}から{}へ変換しました。".format(encoding, "utf-8"))
                else:
                    print("エンコードされたファイル{}はutf-8でした。".format(data_temp))
                    rename_file_path = str(file_name.split(".")[0]) + "_utf8" + "." + str(file_name.split(".")[1])
                    os.rename(file_name, rename_file_path)

                new_data_file_name = os.path.join(self.norm_data_dir,
                                            str(data_temp.split(".")[0]) + "_train." + str(data_temp.split(".")[1]))
                new_data_file = open(new_data_file_name, "w")
                with open(rename_file_path, "r", encoding="utf-8") as file:
                    for line in file.readlines():
                        if not line:
                            continue
                        new_data_file.write(norm_sentence(line))
                        sentence_num += 1

        print("データのエンコード方式の変換と整形を終了します。総文章ファイル数は{},総文章数は{}でした。".format(document_num,
                                                                       sentence_num))


    def wakati(self):
        print("データの分かち書きを始めます......")
        # データの入ったファイルをリストする。
        data_list = os.listdir(self.norm_data_dir)
        total_line_num = 0
        for i, data_temp in enumerate(data_list):
            input_file_name = os.path.join(self.norm_data_dir, data_temp)
            output_file_name = os.path.join(self.wakati_data_dir,
                                            str(data_temp.split(".")[0]) + "_wakati." + str(data_temp.split(".")[1]))
            if os.path.isfile(os.path.join(self.norm_data_dir, data_temp)) and ("train.txt" in data_temp.split("_")):
                tagger = MeCab.Tagger('-F\s%f[6] -U\s%m -E\\n')
                fi = open(input_file_name, "r")
                fo = open(output_file_name, "w")
                line = fi.readline()
                while line:
                    total_line_num += 1
                    result = tagger.parse(line)
                    fo.write(result[1:])
                    line = fi.readline()
                fi.close()
                fo.close()
        print("データの分かち書きの書き込みを終了しました。総文章数は{}です。\n出力先:{}\n".format(total_line_num,
                                                                                   self.norm_data_dir))

    def model(self):
        author_list = []
        documents = [[TaggedDocument(words=sentence.split(), tags=author) for sentence in open(data, "r")] for
                     author, data in zip(author_list, os.listdir(self.wakati_data_dir))]
        model = Doc2Vec(documents=documents, dm=1, size=300, window=10, min_count=10, workers=5)
        model.save(self.output_dir)

    def similarity(self, word):
        pass


if __name__=="__main__":
    data_dir = r"/home/tomoya/Downloads/aozora/dov2vec"
    output_dir = r"/home/tomoya/Downloads/aozora/train_output"
    if "--train" in sys.argv or "--t" in sys.argv:
        pass

    elif "--eval" in sys.argv or "--e" in sys.argv:
        pass

    else:
        raise ValueError("you have to check your arguments!")

