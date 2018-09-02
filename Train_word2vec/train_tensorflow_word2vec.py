# TODO 各ライブラリをインポートする。
import tensorflow as tf
import numpy as np
from bs4 import BeautifulSoup
import chardet
import codecs
import pickle
import os
import collections
import MeCab
from tqdm import tqdm


class TensorCBOW:
    def __init__(self, output_dir, data_path, batch_size=100, embedding_size=200, vocabulary_size=10000,
                 generations=100000, print_loss_every=1000, negative_sample=10, window_size=5,
                 model_learning_rate=0.01, save_embeddings_every=5000):
        # バッチサイズを指定する。
        self.batch_size = batch_size
        # 埋め込み行列の次元数について指定する。
        self.embedding_size = embedding_size
        # 語彙数について指定する。
        self.vocabulary_size = vocabulary_size
        # トレーニングの実行回数について指定する。
        self.generations = generations
        # 損失を表示するトレーニング回数について指定する。
        self.print_loss_every = print_loss_every
        # 負例サンプリングの負例の数について指定する。
        self.negative_sample = negative_sample
        # コンテキストのウィンドウサイズについて指定する。
        self.window_size = window_size
        # MODELの学習率を指定する。
        self.model_learning_rate = model_learning_rate
        # 埋め込みベクトルを保存する。
        self.save_embeddings_every = save_embeddings_every
        # 出力先となるディレクトリに関して指定する。
        self.output_dir = output_dir
        # 読み取りデータの出力ファイルをパスで自動的に指定する。
        self.load_data_path = os.path.join(output_dir, "train_data_for_tensor_word2vec.txt")
        # 整形データの出力ファイルをパスで自動的に指定する。
        self.transformed_data_path = os.path.join(output_dir, "transformed_train_data_for_tensor_word2vec.txt")
        # pickle化した辞書データを保存するバイナリファイルをパスで自動的に指定する。
        self.words_dict_dir = os.path.join(self.output_dir, "words_dict.pickle")
        # pickle化した語彙id化した整形データを保存するバイナリファイルをパスで自動的に指定する。
        self.word_to_number_data_dir = os.path.join(self.output_dir, "word_to_number_data.pickle")
        # 入力ファイルのデータを指定する。
        self.data_path = data_path

    def load_data_html(self):
        print("データの読み込みを開始します......")

        # outputファイルの作成
        output_file = open(self.load_data_path, "w")
        # エンコードの調査
        with open(self.data_path, "rb") as f:
            encoding = chardet.detect(f.read())["encoding"]

        # エンコードがUTF-8ではなかった時の処理
        if encoding != "utf-8":
            print("エンコードされたファイルが{}だったため、utf-8に変更します。".format(encoding))
            new_encoded_file_name = os.path.join(self.output_dir, "new_encoded_data.html")
            old_file = codecs.open(self.data_path, "r", encoding)
            new_encoded_file = codecs.open(new_encoded_file_name, "w", "utf-8")
            for row in old_file:
                new_encoded_file.write(row)
            old_file.close()
            new_encoded_file.close()
            self.data_path = os.path.join(self.output_dir, "new_encoded_data.html")
            print("エンコードを{}から{}へ変換しました。".format(encoding, "utf-8"))

        # テキストファイルの作成
        with open(self.data_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            for i, sentence in tqdm(enumerate(soup.find_all("div"))):
                output_file.write(sentence.text)

        print("データの読み込みを正常に完了しました。\n出力先:{}\n".format(self.load_data_path))

    def normalize_text(self):
        # TODO　単語間に空白があり、なおかつ固有名詞の統一、半角を全角、数字の０への統一などを行う必要がある(本番では)。
        print("データの分かち書きの書き込みを開始します......")
        tagger = MeCab.Tagger('-F\s%f[6] -U\s%m -E\\n')
        fi = open(self.load_data_path, "r")
        fo = open(self.transformed_data_path, "w")
        line = fi.readline()
        total_line_num = 0
        while line:
            total_line_num += 1
            result = tagger.parse(line)
            fo.write(result[1:])
            line = fi.readline()
        fi.close()
        fo.close()
        print("データの分かち書きの書き込みを終了しました。総文章数は{}です。\n出力先:{}\n".format(total_line_num,
                                                             self.transformed_data_path))

    def build_dictionary(self):
        print("ユニークな単語の辞書を作成します......")
        # 単語間に空白の空いたテキストを用意する。
        sentences = open(self.transformed_data_path, "r")
        # 改行ごとにデータを分割する。
        split_sentences = [s.split() for s in sentences]
        # 改行の中の単語を単語によって取得する。
        words = [x for sublist in split_sentences for x in sublist]
        # カウントのためのリストを作成する。
        count = [["RARE", -1]]
        # どの単語がどの程度存在しているのかをリストで示す。
        count.extend(collections.Counter(words).most_common(self.vocabulary_size - 1))
        # 辞書形式で語彙のIDと語彙を保存する。
        words_dict = {}
        for word, word_count in tqdm(count):
            words_dict[word] = len(words_dict)
        # pickle化して保存
        print("単語の辞書をpickle化します......")
        with open(self.words_dict_dir, "wb") as f:
            pickle.dump(words_dict, f)
        print("ユニークな単語の辞書を正常に作成しました。総単語数は{}です。\n出力先:{}\n".format(len(words_dict),
                                                                 self.words_dict_dir))

    def text_to_numbers(self):
        print("文章のone-hot化を開始します......")
        # pickle化したデータの読み込み
        with open(self.words_dict_dir, "rb") as f:
            word_dict = pickle.load(f)
        # 単語間に空白のあるデータの読み込み
        sentences = open(self.transformed_data_path, "r")
        # 語彙idへと変換する。
        data = []
        for sentence in sentences:
            sentence_data = []
            for word in sentence.split(" "):
                if word in word_dict:
                    word_ix = word_dict[word]
                else:
                    word_ix = 0
                sentence_data.append(word_ix)
            data.append(sentence_data)
        # pickle化した整形データをpickle化する。
        print("one-hot化した文章をpickle化します......")
        with open(self.word_to_number_data_dir, "wb") as f:
            pickle.dump(data, f)
        print("文章のone-hot化を正常に終了しました。\n出力先:{}\n".format(self.word_to_number_data_dir))

    def generate_batch_data(self):
        # TODO 各文に対して、ウィンドウサイズ以上の単語数が存在するかどうかを確認する。
        # 数字化したデータの取得
        with open(self.word_to_number_data_dir, "rb") as f:
            sentences = pickle.load(f)

        batch_data = []
        label_data = []
        # バッチサイズに達するまで処理を続ける。
        while len(batch_data) < self.batch_size:
            # 文章をランダムに抽出する。
            rand_sentence = np.random.choice(sentences)
            # ランダムに抽出した文章がwindow_size以上の単語を保持しているかを判別する。
            if len(rand_sentence) <= self.window_size * 2:
                continue
            # ランダムに抽出した文からウィンドウサイズ分の単語を抽出する。
            window_sequences = [rand_sentence[max((ix - self.window_size), 0): (ix + self.window_size + 1)]
                                for ix, x in enumerate(rand_sentence)]
            # ターゲットとなる単語のインデックスを得る。
            label_indices = [ix if ix < self.window_size else self.window_size for ix, x in enumerate(window_sequences)]
            # ターゲットとコンテキストをタプルとして得る。
            batch_and_labels = [(x[:y] + x[(y + 1):], x[y]) for x, y in zip(window_sequences, label_indices)]
            batch_and_labels = [(x, y) for x, y in batch_and_labels if len(x) == 2 * self.window_size]
            # ターゲットとコンテキストを個々に分割する。
            batch, labels = [list(x) for x in zip(*batch_and_labels)]
            batch_data.extend(batch[:self.batch_size])
            label_data.extend(labels[:self.batch_size])

        # バッチデータとして保存する。
        batch_data = batch_data[: self.batch_size]
        label_data = label_data[: self.batch_size]

        batch_data = np.array(batch_data)
        label_data = np.transpose(np.array([label_data]))
        return batch_data, label_data

    def make_model(self):
        print("モデルの学習を始めます......")
        # テキストデータの読み込み
        text_data = open(self.transformed_data_path, "r")
        # ディクショナリデータの読み込み
        with open(self.words_dict_dir, "rb") as f:
            word_dictionary = pickle.load(f)
        # vocabulary_sizeの更新
        self.vocabulary_size = len(word_dictionary)
        # Tensorflowセッションの開始
        with tf.Session() as sess:
            # TODO 初期値においてHeの初期値を導入する必要があるのではないか。
            # 単語埋め込みの設定
            embeddings = tf.Variable(tf.random_uniform([self.vocabulary_size, self.embedding_size], -1.0, 1.0))
            # 埋め込みの保存を実行
            saver = tf.train.Saver({"embeddings": embeddings})
            # プレースホルダを作成
            x_inputs = tf.placeholder(tf.int32, shape=[self.batch_size, 2 * self.window_size])
            y_target = tf.placeholder(tf.int32, shape=[self.batch_size, 1])
            # 単語埋め込みを検索し、ウィンドウの埋め込みを結合
            embed = tf.zeros([self.batch_size, self.embedding_size])
            for element in range(2 * self.window_size):
                embed += tf.nn.embedding_lookup(embeddings, x_inputs[:, element])
            # NCE損失関数のパラメータ
            nce_weights = tf.Variable(tf.truncated_normal([self.vocabulary_size, self.embedding_size],
                                                          stddev=1.0 / np.sqrt(self.embedding_size)))
            nce_biases = tf.Variable(tf.zeros([self.vocabulary_size]))
            # NCE損失関数を設定
            loss = tf.reduce_mean(tf.nn.nce_loss(weights=nce_weights,
                                                 biases=nce_biases,
                                                 labels=y_target,
                                                 inputs=embed,
                                                 num_sampled=self.negative_sample,
                                                 num_classes=self.vocabulary_size))
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=self.model_learning_rate).minimize(loss)
            init = tf.global_variables_initializer()
            sess.run(init)

            for i in range(self.generations):
                # 学習の開始
                batch_inputs, batch_labels = self.generate_batch_data()
                feed_dict = {x_inputs: batch_inputs, y_target: batch_labels}
                sess.run(optimizer, feed_dict=feed_dict)

                # 損失関数の評価
                if not (i+1) % self.print_loss_every:
                    loss_val = sess.run(loss, feed_dict=feed_dict)
                    print("Loss at step {} : {}".format(i+1, loss_val))

                # ディクショナリと埋め込みを保存
                if not (i + 1) % self.save_embeddings_every:
                    print("Save dictionary and embedding_vec: {}".format(self.output_dir))
                    with open(os.path.join(self.output_dir, "train_movie_vocab.pickle"), "wb") as f:
                        pickle.dump(word_dictionary, f)

                    # 埋め込みベクトルの保存
                    model_checkpoint_path = os.path.join(self.output_dir, "train_cbow_movie_embedding.ckpt")
                    saver.save(sess, model_checkpoint_path)

            # 最終的な埋め込みベクトルの保存
            model_checkpoint_path = os.path.join(self.output_dir, "final_cbow_movie_embedding.ckpt")
            save_path = saver.save(sess, model_checkpoint_path)

        print("モデルの学習を正常に終了しました。\t{}".format(save_path))

    def use_embedding_vec(self, word):
        print("埋め込みベクトルの解析を始めます。")
        
        print("埋め込みベクトルの解析を終わります。")
        pass

    def plot_by_tsne(self):
        print("t-SNEによる埋め込みベクトルのプロットを始めます。")
        print("t-SNE")
        pass
