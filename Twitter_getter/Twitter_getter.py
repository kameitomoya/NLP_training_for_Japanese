from configparser import ConfigParser
from requests_oauthlib import OAuth1Session
from requests import exceptions
from pymongo import MongoClient
import pymongo
import time
import json
import sys
from pprint import pprint


class TwitterGetter:
    def __init__(self, section):
        config = ConfigParser()
        config.read("setting.ini")
        self.section = section
        self.consumer_key = config[section]["CONSUMER_KEY"]
        self.consumer_secret = config[section]["CONSUMER_SECRET"]
        self.access_token = config[section]["ACCESS_TOKEN"]
        self.access_token_secret = config[section]["ACCESS_TOKEN_SECRET"]

    def get_twitter(self, keyword, max_id, since_id, url="Normal", pr=True):
        error_time = 0

        if url == "Normal":
            url = "https://api.twitter.com/1.1/search/tweets.json"
            count = 100
        elif url == "30_days":
            url = "https://api.twitter.com/1.1/tweets/search/30day/my_env_name.json"
            count = 100
        elif url == "full":
            url = "https://api.twitter.com/1.1/tweets/search/fullarchive/my_env_name.json"
            count = 500
        else:
            raise ValueError("URL argument is not correct")

        params = {"q": " ".join([str(keyword), "#".format(str(keyword)), "exclude:retweets", "exclude:nativeretweets"]),
                  "count": count, "result_type": "mixed", "Language": "ja", "max_id": max_id, "since_id": since_id}

        twitter = OAuth1Session(self.consumer_key, self.consumer_secret, self.access_token,
                                self.access_token_secret)

        while True:
            error_time += 1
            try:
                req = twitter.get(url, params=params)
                if req.status_code == 200:
                    timeline = json.loads(req.text)
                    result = []
                    for i, tweet in enumerate(timeline["statuses"]):
                        result_tmp = {"user": tweet["user"]["name"], "text": tweet["text"], "time": tweet["created_at"],
                                      "id": tweet["id"], "keyword": key_word}
                        result.append(result_tmp)
                        if pr & (i % 50 == 0):
                            print("#{}".format(tweet["text"]),
                                  sep="")
                    break

                elif req.status_code == 429:
                    print("Reached limited requests... Wait 15 mins")
                    time.sleep(15 * 60)

                else:
                    raise ValueError("ERROR: {}".format(req.status_code))

            except exceptions.ConnectionError:
                print("Connection Error.... Check your Network Environment: ErrorTime{}".format(error_time))
                time.sleep(5 * 60)
                if not error_time % 20:
                    print("10 hours have passed... Finished this process.")
                    break
                continue

        print("Getting data about @{} from tweets between {} is succeeded".format(key_word, max_id))
        return result

    def save_twitter(self, result, set=True):
        client = MongoClient()
        db = client["collect_data"]
        collection = db[self.section]
        if set:
            collection.create_index("text")

        collection.insert_many(result)
        print("Saving data in MongoDB is succeeded")

    @staticmethod
    def _get_db_data(section):
        client = MongoClient()
        db = client["collect_data"]
        collection = db[section]
        return collection.find().count()

    @staticmethod
    def _find_data(section, keyword):
        client = MongoClient()
        db = client["collect_data"]
        collection = db[section]
        for value in collection.find({"keyword": keyword}).sort('id', pymongo.DESCENDING).limit(1000):
            print("#id{}\t@keyword{}\n#text{}".format(value["id"], value["keyword"], value["text"]))


    @staticmethod
    def _get_recent_id(section, key_word):
        client = MongoClient()
        db = client["collect_data"]
        collection = db[section]
        recent_id = [i for i in collection.find({"keyword": key_word}).sort('id', pymongo.DESCENDING).limit(1)]
        if not recent_id:
            return 0
        else:
            return recent_id[0]["id"]

    @classmethod
    def start_collecting_data(cls, section, key_word, pr):
        print("Collecting data about @{} is initializing... Now Total_columns is {}".format(key_word,
                                                                                            cls._get_db_data(section)))
        before_columns_num = cls._get_db_data(section)
        loop_num = 0
        max_id = -1
        before_max_id = 10
        total_tweets = 0
        set_unique = True
        since_id = cls._get_recent_id(section=section, key_word=key_word)
        while True:
            if not loop_num:
                set_unique = False

            c_inst = cls(section)
            result = c_inst.get_twitter(keyword=key_word, max_id=max_id, since_id=since_id, pr=pr)

            if (not result) or (before_max_id == max_id):
                print("Finished collecting data.....  Get {} columns".format(cls._get_db_data(section) -
                                                                             before_columns_num))
                break
            else:
                c_inst.save_twitter(result, set=set_unique)
                total_tweets += len(result)
                loop_num += 1
                before_max_id = max_id
                max_id = result[-1]["id"]
        return cls._get_db_data(section) - before_columns_num


if __name__ == '__main__':
    start_time = time.time()
    if "-c" in sys.argv:
        print("Collecting data is initializing ......")
        search_key = {"CAR": ["トヨタ アクア", "トヨタ ヴィッツ", "トヨタ カローラ スポーツ", "トヨタ スペイド", "トヨタ タンク",
                              "トヨタ パッソ", "トヨタ ポルテ", "トヨタ ルーミー", "トヨタ アルファード", "トヨタ ヴェルファイア",
                              "トヨタ ヴォクシー", "トヨタ エスクァイア", "トヨタ エスティマ", "トヨタ シエンタ", "トヨタ ノア",
                              "トヨタ ハイエース", "トヨタ アリオン", "トヨタ カムリ", "トヨタ カローラ", "トヨタ クラウン",
                              "トヨタ センチュリー", "トヨタ プリウス", "トヨタ プレミオ", "トヨタ マークX", "トヨタ MIRAI",
                              "トヨタ カローラフィールダー", "トヨタ C-HR", "トヨタ ハイラックス", "トヨタ ハリアー",
                              "トヨタ ランドクルーザー", "トヨタ 86", "トヨタ ピクシス エポック", "トヨタ ピクシス ジョイ",
                              "トヨタ ピクシス トラック", "トヨタ ピクシス バン", "トヨタ ピクシス メガ", "ホンダ シャトル",
                              "ホンダ フィット", "ホンダ オデッセイ", "ホンダ ステップワゴン", "ホンダ フリード", "ホンダ ジェイド",
                              "ホンダ レジェンド", "ホンダ クラリティ", "ホンダ アコード", "ホンダ シビック", "ホンダ グレイス",
                              "ホンダ シビック ハッチバック", "ホンダ NSX", "ホンダ S660", "ホンダ CR-V", "ホンダ ヴェゼル",
                              "ホンダ N-BOX", "ホンダ N-BOX SLASH", "ホンダ N-ONE", "ホンダ N-WGN", "ホンダ N-VAN",
                              "ホンダ アクティ", "日産 リーフ", "日産 e-NV200", "日産 ノート", "日産 セレナ", "日産 ジューク",
                              "日産 キューブ", "日産 マーチ", "日産 デイズ", "日産 クリッパーリオ", "日産 エルグランド",
                              "日産 セレナ", "日産 NV350キャラバン", "日産 GT-R", "日産 フェアレディ", "日産 エクストレイル",
                              "日産 フーガ", "日産 スカイライン", "日産 シーマ", "日産 ティアナ", "日産 シルフィ",
                              "スバル IMPREZA", "スバル IMPREZA G4", "スバル XV", "スバル フォレスタ",
                              "スバル レガシー アウトバック", "スバル B4", "スバル LEVORG", "スバル S4", "スバル WRX STI",
                              "スバル BRZ", "スバル JUSTY", "マツダ デミオ", "マツダ アクセラ", "マツダ アテンザ", "マツダ CX-3",
                              "マツダ CX-5", "マツダ CX-8", "マツダ ロードスター", "マツダ フレア", "マツダ キャロル",
                              "マツダ スクラムワゴン", "ダイハツ ミラ", "ダイハツ キャスト", "ダイハツ ムーヴ", "ダイハツ タント",
                              "ダイハツ ウェイク", "ダイハツ アトレー", "ダイハツ ブーン", "ダイハツ トール", "ダイハツ メビウス",
                              "ダイハツ アルティス", "三菱 アウトランダー", "三菱 RVR", "三菱 エクリプス", "三菱 パジェロ",
                              "三菱 デリカ", "三菱 ミラージュ", "三菱 i-MiEV", "三菱 タウンボックス", "三菱 アウトランダー",
                              "スズキ アルト", "スズキ エブリイワゴン ", "スズキ ジムニー", "スズキ スペーシア", "スズキ ハスラー",
                              "スズキ ラパン", "スズキ ワゴンR", "スズキ イグニス", "スズキ S-CROSS", "スズキ エスクード",
                              "スズキ クロスビー", "スズキ ジムニーシエラ", "スズキ スイフト", "スズキ ソリオ", "スズキ バレーノ",
                              "スズキ ランディ", "レクサス ", "レクサス ", "レクサス ", "レクサス LS", "レクサス GS",
                              "レクサス IS", "レクサス LC", "レクサス RC", "レクサス CT", "レクサス LX", "レクサス RX",
                              "レクサス NX", "インフィニティ QX80", "インフィニティ Q50", "インフィニティ QX70",
                              "インフィニティ QX60", "インフィニティ M37", "インフィニティ M56", "インフィニティ QX50",
                              "アキュラ RDX", "アキュラ MDX", "アキュラ RLX", "アキュラ TLX", "アキュラ ILX", "アキュラ NSX"],
                      "CPU": ["Intel Xeon", "Intel Core i9", "Intel Core i7", "Intel Core i5", "Intel Core i3",
                              "Intel Pentium", "Intel Celeron", "Intel Core m3", "Intel Atom", "Intel Itanium",
                              "Intel Quark", "AMD Ryzen Threadripper", "AMD Ryzen 7", "AMD Ryzen 5", "AMD Ryzen 3",
                              "AMD Athlon", "AMD A-Series", "AMD FX"]}
        result = {}
        for section in search_key.keys():
            for key_word in search_key[section]:
                columns_num = TwitterGetter.start_collecting_data(section=section, key_word=key_word, pr=False)
                result[key_word] = columns_num
        elasped_time = time.time() - start_time
        pprint(result)
        print("elapsed_time:{} sec".format(elasped_time))

    elif "-t" in sys.argv:
        print("Test is initializing .......")
        search_key = {"test": ["トヨタ アクア", "トヨタ ヴィッツ", "トヨタ カローラ スポーツ", "トヨタ スペイド", "トヨタ タンク",
                               "トヨタ パッソ", "トヨタ ポルテ", "トヨタ ルーミー", "トヨタ アルファード", "トヨタ ヴェルファイア",
                               "トヨタ ヴォクシー", "トヨタ エスクァイア", "トヨタ エスティマ", "トヨタ シエンタ", "トヨタ ノア",
                               "トヨタ ハイエース", "トヨタ アリオン", "トヨタ カムリ", "トヨタ カローラ", "トヨタ クラウン",
                               "トヨタ センチュリー", "トヨタ プリウス", "トヨタ プレミオ", "トヨタ マークX", "トヨタ MIRAI",
                               "トヨタ カローラフィールダー", "トヨタ C-HR", "トヨタ ハイラックス", "トヨタ ハリアー",
                               "トヨタ ランドクルーザー", "トヨタ 86", "トヨタ ピクシス エポック", "トヨタ ピクシス ジョイ",
                               "トヨタ ピクシス トラック", "トヨタ ピクシス バン", "トヨタ ピクシス メガ"]}
        result = {}
        for section in search_key.keys():
            for key_word in search_key[section]:
                columns_num = TwitterGetter.start_collecting_data(section=section, key_word=key_word, pr=False)
                result[key_word] = columns_num
        elasped_time = time.time() -start_time
        pprint(result)
        print("elapsed_time:{} sec".format(elasped_time))

    elif "-f" in sys.argv:
        print("Finding Twitter data is initializing .......")
        section = "CAR"
        key_word = "トヨタ センチュリー"
        TwitterGetter._find_data(section, key_word)

    else:
        raise ValueError("please input CORRECT arguments")
