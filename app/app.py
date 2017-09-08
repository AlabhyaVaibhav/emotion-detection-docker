from FP import Maybe, List
from os_helpers import get_directories, get_files_from_root
from feature_helpers import extract_image_features, process_image, split_data, normalize_data, normalize_data_prediction, feature_reduction
from ml_helpers import save_data, load_data, experiment, train_model, save_model, load_model, predict_with_model
import numpy as np
import argparse

# OPTIMIZATIONS TO BE DONE (hopefully)
# - Do more FP
# - Use keyword arguments
# - Error trapping when invalid image

IMAGE_DIR = './images'
OLD_MODEL_PATH = './old_emotion_detector.pkl'
NEW_MODEL_PATH = './emotion_detector.pkl'
DATA_PATH = './data.pkl'
EMOTIONS = get_directories(IMAGE_DIR)

def generate_data(image_dir=IMAGE_DIR):
    return List(get_directories(image_dir)) \
        .chain(get_files_from_root(image_dir)) \
        .reduce(lambda v, acc: acc + v) \
        .map(extract_image_features) \
        .reduce(split_data, ([], [])) \
        .map(normalize_data) \
        .map(feature_reduction(OLD_MODEL_PATH, True)) \
        .map(lambda v: (np.array(v[0]), np.array(v[1]))) \
        .map(save_data) \
        .value

def train(data_dir=DATA_PATH):
    print("Training start...")

    Maybe.of(load_data()) \
        .map(experiment) \
        .map(train_model) \
        .map(save_model)

    print("Training complete.")

def predict(image_paths):
    print("Predicting...")

    return List(image_paths) \
        .map(process_image) \
        .reduce(lambda v, acc: acc + (v,), ()) \
        .map(normalize_data_prediction) \
        .map(feature_reduction(OLD_MODEL_PATH)) \
        .map(predict_with_model(load_model())) \
        .map(lambda v: [EMOTIONS[x] for x in v]) \
        .value

parser = argparse.ArgumentParser(description='Emotion Detection Application')
parser.add_argument('--train', action='store_true', help='start training the program to predict emotions')
parser.add_argument('--data', nargs=1, help='process images from specified folder into usable data', metavar='path_to_training_folder')
parser.add_argument('--predict', nargs='+', help='predict the emotion of face in image', metavar='path_to_input_image')
args = parser.parse_args()
unpacked_args = vars(args)
data_arg = unpacked_args['data']
train_arg = unpacked_args['train']
predict_arg = unpacked_args['predict']

if (data_arg is not None):
    generate_data(data_arg[0])

if (train_arg is not None):
    train()

if (predict_arg is not None):
    print(predict(predict_arg))

# Remove DS Store from images: rm ./app/images/*/.DS_Store