import os
import pandas as pd
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import preprocess_nlp

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
df = preprocess_nlp.preprocess_nlp(df)
print("正常に処理が終了しました。")




