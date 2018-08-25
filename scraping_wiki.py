from glob import glob
import os
import sys
import pandas as pd


class ScrapingWiki:
    def __init__(self, input_dir=None, output_dir=None):
        if not input_dir:
            self.input_dir = input("please enter the directory contains Wikipedia dump data")
        if not output_dir:
            self.output_dir = os.getcwd()
        self.input_dir = input_dir
        self.output_dir = output_dir

    def extract_sentence(self):
        def get_sentence(content):
            content = content.replace("\n", " ").strip()
            content = content.replace("？", "。").replace("！", "。").replace("?", "。")\
                .replace("!", "。").replace("「", "").replace("」", "")
            content_maru = [i for i in content.split("。") if i]
            return content_maru

        def iter_docs(file):
            for line in file:
                if line.startswith("<doc"):
                    buffer = []
                elif line.startswith("</doc>"):
                    content = "".join(buffer)
                    yield content
                else:
                    buffer.append(line)

        df_result = pd.DataFrame([])
        sentence_num = 0
        for path in glob(os.path.join(self.input_dir, "*", "wiki_*")):
            # 現在のプロセスを表示する。
            print("Processing {}...".format(path), file=sys.stderr)
            sentence_list = []
            with open(path, encoding="utf-8") as file:
                for i, content in enumerate(iter_docs(file)):
                    for sentence in get_sentence(content):
                        sentence_list.append(sentence)
                        sentence_num += 1

                        if i % 5000 == 0:
                            print("example_sentence:{}".format(sentence))
                df_temp = pd.DataFrame({"sentence": sentence_list})
                df_result = pd.concat([df_result, df_temp], ignore_index=True)
        print("総文章数は{}です。".format(sentence_num))
        os.chdir(self.output_dir)
        df_result.to_csv("wikiデータ.csv", encoding="utf-8")
        df_result.sample(100).to_csv("wikiデータ_sample.csv", encoding="utf-8")
        return df_result