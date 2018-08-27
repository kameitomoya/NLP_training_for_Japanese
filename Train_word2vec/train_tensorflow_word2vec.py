# TODO 各ライブラリをインポートする。
import tensorflow as tf
import numpy as np
# import matplotlib.pyplot
import os
import collections
import pickle as pk
import MeCab
from tqdm import tqdm


class tensor_CBOW:
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
        # 負例サンプリングん負例の数について指定する。
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
        # 語彙データの出力ファイルをパスで自動的に指定する。
        self.dict_data_path = os.path.join(output_dir, "dict_data_for_tensor_word2vec.txt")
        # 入力ファイルのデータを指定する。
        self.data_path = data_path

    def load_data(self):
        output_file = open(self.load_data_path, "w")
        with open(self.data_path, "r", encoding="utf-8") as file:
            for i in tqdm(file):
                output_file.write(i)

    def normalize_text(self):
        pass

    def build_dictionary(self):
        # 単語間に空白が存在する事を要求する。
        sentences = open(self.transformed_data_path, "r")
        #
        split_sentences = [s.split() for s in sentences]
        #
        words = [x for sublist in split_sentences for x in sublist]
        #
        count = [["RARE", -1]]
        #
        count.extend(collections.Counter(words).most_common(self.vocabulary_size - 1))
        #
        words_dict = {}
        for word, word_count in tqdm(count):
            words_dict[word] = len(words_dict)
        # TODO pickleでディクショナリを保存する。

    def text_to_numbers(self):
        # TODO pickleでディクショナリを読み込む。
        word_dict = []
        sentences = open(self.transformed_data_path, "r")
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
        # TODO pickleでディクショナリを読み込む。

    def generate_batch_data(self, sentences):
        ## TODO 各文に対して、ウィンドウサイズ以上の単語数が存在するかどうかを確認する。
        batch_data = []
        label_data = []
        while len(batch_data) < self.batch_size:
            rand_sentence = np.random.choice(sentences)
            window_sequences = [rand_sentence[max((ix - self.window_size), 0): (ix + self.window_size + 1)]
                                for ix, x in enumerate(rand_sentence)]
            label_indices = [ix if ix < self.window_size else self.window_size for ix, x in enumerate(window_sequences)]
            batch_and_labels = [(x[y], x[:y] + x[(y + 1):]) for x, y in zip(window_sequences, label_indices)]
            tuple_data = [(x, y_) for x, y in batch_and_labels for y_ in y]
            batch, labels = [list(x) for x in zip(*tuple_data)]
            batch_data.extend(batch[:batch_data])
            label_data.extend(labels[:batch_data])
        batch_data = batch_data[: self.batch_size]
        label_data = label_data[: self.batch_size]

        batch_data = np.array(batch_data)
        label_data = np.transpose(np.array([label_data]))
        return batch_data, label_data

    def make_model(self):
        text_data = open(self.transformed_data_path, "r")
        word_dictionary = open(self.dict_data_path, "r")
        with tf.Session() as sess:
            # TODO 初期値においてHeの初期値を導入する必要があるのではないか。
            # 単語埋め込みの設定
            embeddings = tf.Variable(tf.random_uniform([self.vocabulary_size, self.embedding_size], -1.0, 1.0))
            # 埋め込みの保存を実行
            saver = tf.train.Saver({"embeddings": embeddings})
            # プレースホルダを作成
            x_inputs = tf.placeholder(tf.int32, shape=[self.batch_size, 2*self.window_size])
            y_target = tf.placeholder(tf.int32, shape=[self.batch_size, 1])
            # 単語埋め込みを検索し、ウィンドウの埋め込みを結合
            embed = tf.zeros([self.batch_size, self.embedding_size])
            for element in range(2*self.window_size):
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

            self.make_model()
            init = tf.global_variables_initializer()
            sess.init(init)

            for i in range(self.generations):
                batch_inputs, batch_labels = self.generate_batch_data(text_data)
                feed_dict = {x_inputs: batch_inputs, y_target: batch_labels}
                sess.run(optimizer, feed_dict=feed_dict)

                if (i+1) % self.save_embeddings_every == 0:
                    with open(os.path.join(self.output_dir, "movie_vocab.pkl"), "wb") as f:
                        pk.dump(word_dictionary, f)

                    #埋め込みベクトルの保存
                    model_checkpoint_path = os.path.join(self.output_dir, "cbow_movie_embedding.ckpt")
                    save_path = saver.save(sess, model_checkpoint_path)
