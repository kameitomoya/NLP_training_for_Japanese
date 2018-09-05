import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess_NLP import preprocess_nlp

print("関数make_wti_itwのテストを始めます.....")

# input_dir = input("入力データのディレクトリを指定して下さい。:")
# data_name = input("入力データのデータ名を指定して下さい。:")
# output_dir = input("出力データのディレクトリを指定して下さい。:")
input_dir = "/home/tomoya/Downloads/temp_data"
data_name = "語彙.csv"
output_dir = "/home/tomoya/Downloads/temp_data"

try:
    os.chdir(input_dir)
    df = pd.read_csv(data_name, engine="python", encoding="utf-8")

except FileNotFoundError as e:
    print("Fileが存在しません。")
    raise e

os.chdir(output_dir)
df = preprocess_nlp.make_wti_itw(df, max_vocab_num=1000, min_vocab_num=10)
print("正常に処理が終了しました。")
