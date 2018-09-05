import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess_NLP import preprocess_nlp

print("関数preprocess_nlpのテストを始めます.....")

# input_dir = input("入力データのディレクトリを指定して下さい。:")
# data_name = input("入力データのデータ名を指定して下さい。:")
# output_dir = input("出力データのディレクトリを指定して下さい。:")
input_dir = "/home/tomoya/Downloads/temp_data"
data_name = "wikiデータ.csv"
output_dir = "/home/tomoya/Downloads/temp_data"

try:
    os.chdir(input_dir)
    df = pd.read_csv(data_name, engine="python", encoding="utf-8")

except FileNotFoundError as e:
    print("Fileが存在しません。")
    raise e

os.chdir(output_dir)
df_1 = df.iloc[:50000, :].reset_index(drop=True)
df_1 = preprocess_nlp.preprocess_nlp(df_1, 1)
df_1.to_csv("前処理後.csv", encoding="utf-8")
print("正常に処理が終了しました。")




