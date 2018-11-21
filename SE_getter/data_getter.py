import requests
import lxml.html
import lxml
from readability.readability import Document
import pymongo
import time
from urlextract import URLExtract
from termcolor import cprint


class DataGetterFromGoogle:
    def __init__(self, keyword, section):
        self.base_url = "https://www.google.com/search?"
        self.section = section
        self.keyword = keyword

    def get_page(self):
        for search_num in range(0, 1000, 10):
            error_num = 0
            while True:
                if error_num >= 20:
                    print("Finished Because error_num reached 20 times")
                    return None
                try:
                    time.sleep(10)
                    req = requests.get(self.base_url, params={"q": self.keyword, "start": search_num})
                    cprint("Now Get Google pages {}: {}".format(int(search_num / 10), req.url), "yellow")
                    if int(req.status_code) == 503:
                        cprint("Google detected the abnormal network traffic", "red")
                        time.sleep(60 * 60)
                    elif int(req.status_code) != 200:
                        cprint("Now Get {} Error".format(req.status_code), "red")
                        error_num += 1
                        time.sleep(5)
                    else:
                        html = lxml.html.fromstring(req.text)
                        nextlist = [i.get("href") for i in html.cssselect("h3.r > a")]
                        error_num = 0
                        break
                except ConnectionError:
                    cprint("Now Get ConnectionError: Error_num{}".format(error_num), "red")
                    error_num += 1
                    time.sleep(10 * 60)
            if not nextlist:
                cprint("Results of the search has run out", "red")
                return None
            for url_base in nextlist:
                try:
                    url = URLExtract().find_urls(url_base)[0].split("&sa=")[0]
                except IndexError:
                    cprint("Can't recognize url: {}".format(url_base), color="red")
                    continue
                cprint("Now specific page :{}".format(url), color="green")
                title, content = self.get_data(url)
                if (title != 0) and (content != 0):
                    self.save_mongodb(section=self.section, title=title, content=content)
            time.sleep(10)

    @staticmethod
    def get_data(url):
        error_num = 0
        while True:
            if error_num >= 10:
                cprint("Finished Because error_num reached 10 times", "red")
                return 0, 0
            try:
                req = requests.get(url)
                if int(req.status_code) == 503:
                    cprint("Google detected the abnormal network traffic", "red")
                    time.sleep(60 * 60)
                elif int(req.status_code) != 200:
                    cprint("Now Get StatusCode{}: Error_num{}".format(req.status_code, error_num), "red")
                    return 0, 0
                else:
                    html = req.text
                    break
            except ConnectionError:
                cprint("Now Get ConnectionError: Error_num{}".format(error_num), "red")
                error_num += 1
                time.sleep(5)
        try:
            document = Document(html)
            content_html = document.summary()
            content_text = lxml.html.fromstring(content_html).text_content().strip()
            short_title = document.short_title()
            return short_title, content_text
        except:
            return 0, 0

    def save_mongodb(self, section, title, content):
        client = pymongo.MongoClient()
        db = client["collect_data"]
        collection = db[section]
        collection.insert({"keyword": self.keyword, "title": title, "content": content})
        cprint("Mongodb saved successfully, now we have {} columns".format(self._get_db_count(section=section)),
               "green")

    @staticmethod
    def format_text(content):
        pass

    @staticmethod
    def _get_db_count(section):
        client = pymongo.MongoClient()
        db = client["collect_data"]
        collection = db[section]
        return collection.find().count()

    @classmethod
    def get_all_data(cls, keywords, section):
        for keyword in keywords:
            cprint("Now Searching #{} {} レビュー".format(keyword[0], keyword[1]), "blue")
            inst = cls(keyword=keyword, section=section)
            inst.get_page()
            cprint("Finished Search #{} {} レビュー".format(keyword[0], keyword[1]), "blue")


if __name__ == '__main__':
    print("initializing searching data .........")
    section_tmp = "Google_CAR"
    key_temp = ["トヨタ アクア", "トヨタ ヴィッツ", "トヨタ カローラ スポーツ", "トヨタ スペイド", "トヨタ タンク",
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
                "アキュラ RDX", "アキュラ MDX", "アキュラ RLX", "アキュラ TLX", "アキュラ ILX", "アキュラ NSX"]
    keywords_tmp = [i.split(" ") for i in key_temp]
    DataGetterFromGoogle.get_all_data(keywords=keywords_tmp, section=section_tmp)

    section_tmp = "Google_CPU"
    key_temp = ["Intel Xeon", "Intel Core i9", "Intel Core i7", "Intel Core i5", "Intel Core i3",
                "Intel Pentium", "Intel Celeron", "Intel Core m3", "Intel Atom", "Intel Itanium",
                "Intel Quark", "AMD Ryzen Threadripper", "AMD Ryzen 7", "AMD Ryzen 5", "AMD Ryzen 3",
                "AMD Athlon", "AMD A-Series", "AMD FX"]
    keywords_tmp = [i.split(" ") for i in key_temp]
    DataGetterFromGoogle.get_all_data(keywords=keywords_tmp, section=section_tmp)
