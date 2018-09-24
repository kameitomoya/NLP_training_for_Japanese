from configparser import ConfigParser
from requests_oauthlib import OAuth1Session
from pymongo import MongoClient
import time
import json


class TwitterGetter:
    def __init__(self, section):
        config = ConfigParser()
        config.read("setting.ini")
        self.section = section
        self.consumer_key = config[section]["CONSUMER_KEY"]
        self.consumer_secret = config[section]["CONSUMER_SECRET"]
        self.access_token = config[section]["ACCESS_TOKEN"]
        self.access_token_secret = config[section]["ACCESS_TOKEN_SECRET"]

    def get_twitter(self, keyword, max_id, url="Normal", pr=True):
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

        params = {"q": keyword, "count": count, "result_type": "mixed", "Language": "ja", "max_id": max_id}

        try:
            twitter = OAuth1Session(self.consumer_key, self.consumer_secret, self.access_token,
                                    self.access_token_secret)
        except:
            raise ValueError("Failed to Authenticate OAuthSession. Please Check your ID and Passwords")

        while True:
            req = twitter.get(url, params=params)
            if req.status_code == 200:
                timeline = json.loads(req.text)
                result = []
                for i, tweet in enumerate(timeline["statuses"]):
                    result_tmp = {"user": tweet["user"]["name"], "text": tweet["text"], "time": tweet["created_at"],
                                  "id": tweet["id"], "keyword": key_word}
                    result.append(result_tmp)
                    if pr:
                        print("#{} {}::{}\n{}".format(i, tweet["user"]["name"], tweet["text"], tweet["created_at"]),
                              sep="")
                break

            elif req.status_code == 429:
                print("Reached limited requests... Wait 15 mins")
                time.sleep(15 * 60)

            else:
                raise ValueError("ERROR: {}".format(req.status_code))

        print("Getting data about @{} from tweets between {} is succeeded".format(key_word, max_id))
        return result

    def save_twitter(self, result, set=True):
        client = MongoClient()
        db = client["collect_data"]
        collection = db[self.section]
        if set:
            collection.create_index("user")

        collection.insert_many(result)
        print("Saving data in MongoDB is succeeded")

    @staticmethod
    def get_db_data(section):
        client = MongoClient()
        db = client["collect_data"]
        collection = db[section]
        return collection.find().count()

    @classmethod
    def start_collecting_data(cls, section, key_word):
        print("Collecting data about @{} is initializing... Now Total_columns is {}".format(key_word,
                                                                                            cls.get_db_data(section)))
        loop_num = 0
        max_id = -1
        total_tweets = 0
        set = True
        while True:
            if not loop_num:
                set = False

            c_inst = cls(section)
            result = c_inst.get_twitter(keyword=key_word, max_id=max_id, pr=False)
            if not result:
                print("Finished collecting data..... Now Total columns is {}".format(cls.get_db_data(section)))
                break
            c_inst.save_twitter(result, set=set)
            total_tweets += len(result)
            loop_num += 1
            max_id = result[-1]["id"]


if __name__ == '__main__':
    section = "test"
    key_word = "Ryzen 2700X"
    TwitterGetter.start_collecting_data(section=section, key_word=key_word)
    """
    max_id = -1
    result_user = []
    for i in range(5):
        if i:
            max_id -= 1
        twitter = TwitterGetter("twitter")
        result = twitter.get_twitter("プリウス", max_id=max_id)
        result_user += [item["user"] for item in result]
        max_id = result[-1]["id"]
    print("user len:{} \n set len:{}".format(len(result_user), len(set(result_user))))
    """
