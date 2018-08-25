import mojimoji
from tqdm import tqdm
import re
import numpy as np
import pandas as pd
import MeCab as mc
import config

## TODO すべてデータベースに格納するように工夫する。

def preprocess_nlp(df, df_num):
    
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
    print("現在形態素解析と単語の正規化を実行中です。")

    for i in tqdm(range(len(df))):
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
                if i == 0:
                    print("#{}: {}".format(i, cleaned_node))
            node = node.next
        # 結果を保持するリストに対して文章を追加する。
        result_list.append(purified_sentence)
    print("総単語数は{}です。".format(total_word_num))
    # 結果を保持するリストをデータフレームへ
    analyzed_df = pd.DataFrame(result_list)
    # analyzed_df.to_csv("前処理後_{}.csv".format(df_num), encoding="utf-8")
    analyzed_df.sample(20).to_csv("前処理後_{}_sample.csv".format(df_num), encoding="utf-8")
    return analyzed_df


def count_word(df):
    unique_words = {}
    for i in tqdm(range(len(df))):
        for j, word in enumerate(df.iloc[i, :]):
            if isinstance(word, float):
                pass
            elif word not in unique_words.keys():
                unique_words[word] = 1
            else:
                unique_words[word] += 1
    df_unique_words = pd.DataFrame([[i, unique_words[i]] for i in unique_words.keys()],
                                   columns=["vocab", "vocab_count"])
    df_unique_words.to_csv("語彙.csv", encoding="utf-8")
    df_unique_words.sample(20).to_csv("語彙_sample.csv", encoding="utf-8")
    return df_unique_words


def make_wti_itw(unique_vocab, max_vocab_num=10, min_vocab_num=1):
    word_to_id = {"rare_or_frequent": 0}
    rare_vocab = set(unique_vocab[unique_vocab.vocab_count <= min_vocab_num]["vocab"])
    frequent_vocab = set(unique_vocab[unique_vocab.vocab_count >= max_vocab_num]["vocab"])
    # word_to_id, id_to_wordをつくる。
    for word in tqdm(unique_vocab["vocab"]):
        if (word not in rare_vocab)and(word not in frequent_vocab):
            word_to_id[word] = len(word_to_id)
    print("総語彙数は{}です。".format(len(word_to_id.keys())))
    df_word_to_id = pd.DataFrame([[i, word_to_id[i]] for i in word_to_id.keys()], columns=["vocab", "vocab_id"])
    df_word_to_id.to_csv("Word_to_id.csv", encoding="utf-8")
    df_word_to_id.sample(20).to_csv("Word_to_id_sample.csv", encoding="utf-8")
    return df_word_to_id

def make_one_hot(analyzed_df, unique_vocab, df_num):
    result_list = []
    for i in tqdm(range(len(analyzed_df))):
        sentence_list = []
        for j, word in enumerate(analyzed_df.iloc[i, :]):
            if isinstance(word, float):
                sentence_list.append(np.nan)
            elif word not in set(unique_vocab["vocab"]):
                sentence_list.append(0)
            else:
                sentence_list.append(int(unique_vocab[unique_vocab.vocab == word]["vocab_id"]))
        result_list.append(sentence_list)
    df_one_hot = pd.DataFrame(result_list)
    df_one_hot.to_csv("one_hot変換後_{}.csv".format(df_num), encoding="utf-8")
    df_one_hot.sample(20).to_csv("one_hot変換後_{}_sample.csv".format(df_num), encoding="utf-8")
    return df_one_hot








