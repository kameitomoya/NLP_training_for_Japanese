import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess_NLP import preprocess_nlp

print("関数test_one_hotのテストを始めます.....")

# input_dir = input("入力データのディレクトリを指定して下さい。:")
# data_name = input("入力データのデータ名を指定して下さい。:")
# output_dir = input("出力データのディレクトリを指定して下さい。:")
input_dir = "/home/tomoya/Downloads/temp_data"
data_name = "前処理後.csv"
data_name2 = "Word_to_id.csv"
output_dir = "/home/tomoya/Downloads/temp_data"

try:
    os.chdir(input_dir)
    analyzed_df = pd.read_csv(data_name, engine="python", encoding="utf-8")
    vocab_data = pd.read_csv(data_name2, engine="python", encoding="utf-8")

except FileNotFoundError as e:
    print("Fileが存在しません。")
    raise e

os.chdir(output_dir)
df_1 = analyzed_df.iloc[:int(len(analyzed_df)/2), :].reset_index(drop=True)
df_2 = analyzed_df.iloc[int(len(analyzed_df)/2)+1:, :].reset_index(drop=True)
df_1 = preprocess_nlp.make_one_hot(df_1, unique_vocab=vocab_data, df_num=1)
df_2 = preprocess_nlp.make_one_hot(df_2, unique_vocab=vocab_data, df_num=2)
df = pd.concat([df_1, df_2], ignore_index=True)
df.to_csv("One-hot変換後.csv")
print("正常に処理が終了しました。")
