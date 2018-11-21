import sys, os
sys.path.append("../..")
from SE_getter.data_getter import DataGetterFromGoogle

if __name__ == '__main__':
    print("テストを開始します。")
    section = "test_google"
    keywords = [["トヨタ", "カムリ"], ["トヨタ", "プリウス"]]
    DataGetterFromGoogle.get_all_data(keywords=keywords, section=section)
    print("テストを終了します。")
