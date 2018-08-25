import mojimoji
import re
import io
import sys
import pandas as pd
import MeCab as mc
import config


def preprocess_nlp(df):
    # print()に関するデコードエラーを解決するためのもの
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    
    def norm_word(word):
        # アルファベットを小文字へ
        word = word.lower()
        # 文字種の統一
        word = mojimoji.han_to_zen(word)
        # 数字の置き換え
        for pattern in config.config_dic["num_patterns"]:
            if re.match(pattern, word):
                word = re.sub(r"\d+", "0", word)
        # 固有名詞の統一
        cleaned_node = config.config_dic["norm_expressions"].get(word) \
            if config.config_dic["norm_expressions"].get(word) else word
        return cleaned_node

    # どの品詞を含めるかについて
    category_list = config.config_dic["category_list"]
    # 結果を保持するリスト
    result_list = []
    # 解析器のセット
    tagger = mc.Tagger("")
    # デコードエラー対策
    tagger.parse(" ")
    # 総単語数のセット
    total_word_num = 0

    for i in range(len(df)):
        # 文章を保存するためのリスト
        purified_sentence = []
        # 解析対象となる文章の取得
        sentence_temp = df["sentence"][i]
        # 形態素解析を行う。
        node = tagger.parseToNode(sentence_temp)
        while node:
            # 品詞の取得
            category, sub_category = node.feature.split(",")[:2]
            # 品詞が取得する対象に含まれるかの判定
            if category in category_list:
                # 総単語数の計算
                total_word_num += 1
                # 対象に含まれる品詞を整形する。
                cleaned_node = norm_word(node.surface)
                # 整形した品詞を文章として追加する。
                purified_sentence.append(cleaned_node)
                if not i % 10000:
                    print("#{}: {}".format(i, cleaned_node))
            node = node.next
        # 結果を保持するリストに対して文章を追加する。
        result_list.append(purified_sentence)
    # 結果を保持するリストをデータフレームへ
    analyzed_df = pd.DataFrame(result_list)
    analyzed_df.to_csv("前処理後.csv", encoding="utf-16", sep=" ")
    analyzed_df.sample(100).to_csv("前処理後_sample.csv", encoding="utf-16", sep=" ")
    return analyzed_df


# todo ストップワードと希少なワードを取り除くため、ONE-HOT表現の作成辞書の作成を分離する。
def make_wti_itw_corpus(df):
    word_to_id = {}
    id_to_word = {}
    df["one_hot_sentence"] = 0
    for i, sentence in enumerate(df["transformed_sentence"]):
        sentence_temp = []
        for j, word in sentence:
            if word in word_to_id:
                word_to_id[word] = len(word_to_id)
                id_to_word[len(id_to_word)] = word
            sentence_temp.append(word_to_id[word])
    df.to_csv("one_hot変換.csv", encoding="utf-8", sep=" ")
    df.sample(100).to_csv("one_hot変換後_sample.csv", encoding="utf-8", sep=" ")
    return df, word_to_id, id_to_word

def make_one_hot(df, unique_vocab):
    pass