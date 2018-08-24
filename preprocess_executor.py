import sys
import os
import pandas as pd
import preprocess_nlp
import scraping_wiki as scraping_wiki
import scraping_twitter as scraping_twitter


print("処理を開始します。")
try:
    answer = sys.argv[1]
except IndexError as e:
    print("please confirm your argument !!")
    raise ValueError("-w or -W for wikipedia dump data\n-t or -T for Twitter data")


if (sys.argv[1] == "-W") or (sys.argv[1] == "-w"):
    print("Wikipediaデータの処理を始めます....")
    input_dir = input("wikipediaのデータのディレクトリを指定して下さい。:")
    output_dir = input("出力先のディレクトリを指定して下さい。:")
    wiki = scraping_wiki.ScrapingWiki(input_dir=input_dir, output_dir=output_dir)
    df = wiki.extract_sentence()

elif (sys.argv[1] == "-T") or (sys.argv[1] == "-t"):
    print("Twitterデータの処理を始めます....")
    input_dir = input("wikipediaのデータのディレクトリを指定して下さい。:")
    output_dir = input("出力先のディレクトリを指定して下さい。:")
    wiki = scraping_twitter.ScrapeTwitter(input_dir=input_dir, output_dir=output_dir)
    df = wiki.extract_sentence()

else:
    answer = input("解析済みのデータフレームが存在しますか？ y/n")
    if answer == "y":
        input_dir = input("解析済みデータのディレクトリを指定して下さい。:")
        data_name = input("ファイル名を指定してください。:")
        os.chdir(input_dir)
        df = pd.read_csv(data_name, engine="python", encoding="utf-8")
    else:
        raise ValueError("分析するデータの種類を指定してください。")


# 自然言語の下処理を始める。
print("自然言語処理の下処理を始めます。")
df_vocab = preprocess_nlp.preprocess_nlp(df)
unique_vocab = preprocess_nlp.make_wti_itw_corpus(df_vocab)
word_to_id, id_to_word, df_one_hot = preprocess_nlp.make_one_hot(df_vocab, unique_vocab)
