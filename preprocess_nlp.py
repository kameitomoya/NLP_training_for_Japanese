from tqdm import tqdm
import mojimoji
import re
import MeCab as mc
import config


def preprocess_nlp(df):
    def norm_word(word):
        # アルファベットを小文字へ
        word = word.lower()
        # 文字種の統一
        word = mojimoji.han_to_zen(word)
        # 数字の置き換え
        for pattern in config.config_dic["num_patterns"]:
            if re.match(pattern, "0", word):
                word = re.sub(r"\d+", "0", word)
        # 固有名詞の統一
        cleaned_node = config.config_dic["norm_expressions"].get(word) \
            if config.config_dic["norm_expressions"].get(word) else word
        return cleaned_node

    category_list = config.config_dic["category_list"]
    df["transformed_sentence"] = 0
    tagger = mc.Tagger("")
    tagger.parse()

    for i in tqdm(range(len(df))):
        purified_sentence = []
        sentence_temp = df["sentence"][i]
        node = tagger.parseToNode(sentence_temp)
        while node:
            category, sub_category = node.feature.split(",")[:2]
            if category in category_list:
                cleaned_node = norm_word(node.surface)
                purified_sentence.append(cleaned_node)
            node = node.next
        df["transformed_sentence"][i] = purified_sentence
    df.to_csv("前処理後.csv", encoding="utf-16", sep=" ")
    df.sample(100).to_csv("前処理後_sample.csv", encoding="utf-16", sep=" ")
    return df


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
    df.to_csv("one_hot変換.csv", encoding="utf-16", sep=" ")
    df.sample(100).to_csv("one_hot変換後_sample.csv", encoding="utf-16", sep=" ")
    return df, word_to_id, id_to_word

def make_one_hot(df, unique_vocab):
    pass


