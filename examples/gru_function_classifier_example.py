import math

import tensorflow as tf

from datasets.classification.function_generator import function_generator
from utils.prepare_training import write_tf_records, read_tf_records
from models.gru_function_classifier import FunctionClassifier


GENERATE_DATA = False


def main():
    # Define "constants".
    hyper_params_filepath = "examples/gru_function_classifier.json"
    data_tmp_folder = "data/.records/gru_function_classifier"
    training_examples_number = 10000
    validation_examples_number = 1000

    if GENERATE_DATA:
        # Create training data.
        print("Generating data")
        train_data = function_generator([lambda x, off: math.sin(x / 50.0 + off), lambda x, off: x / 50.0 + off], 100, training_examples_number)
        validation_data  = function_generator([lambda x, off: math.sin(x / 50.0 + off), lambda x, off: x / 50.0 + off], 100, validation_examples_number)

        # Write tf records
        print("Writing data")
        write_tf_records(data_tmp_folder, 4, 2, train_data, validation_data)

    # Create model.
    print("Creating Model")
    model = FunctionClassifier(hyper_params_filepath)

    # Load data with tf records.
    print("Loading data")
    train_features, train_labels = read_tf_records(data_tmp_folder, "train", model.hyper_params.train.batch_size, (100,), (2,), tf.float32, tf.uint8, 4)
    validation_features, validation_labels = read_tf_records(data_tmp_folder, "validation", model.hyper_params.train.batch_size, (100,), (2,), tf.float32, tf.uint8, 2)

    # Limit used gpu memory.
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 0.75

    # train model.
    with tf.Session(config=config) as sess:
        print("Setup")
        model.setup(sess)

        print("Training")
        model.fit(train_features, train_labels, validation_examples_number, validation_features, validation_labels, verbose=True)
    
        print("Exporting")
        model.export()


if __name__ == "__main__":
    main()
