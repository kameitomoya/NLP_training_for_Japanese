import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import Train_word2vec.train_tensorflow_word2vec as train_tensorflow_word2vec

if __name__ == "__main__":
    output_dir = "/home/tomoya/Downloads/aozora/train_output"
    data_path = "/home/tomoya/Downloads/aozora/4803_14204.html"
    model = train_tensorflow_word2vec.TensorCBOW(output_dir=output_dir, data_path=data_path)
    model.load_data_html()
    model.normalize_text()
    model.build_dictionary()
    model.text_to_numbers()