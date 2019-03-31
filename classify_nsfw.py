import os, sys

import tensorflow as tf
from model import OpenNsfwModel, InputType
from image_utils import create_tensorflow_image_loader
from image_utils import create_yahoo_image_loader

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

IMAGE_LOADER_TENSORFLOW = "tensorflow"
IMAGE_LOADER_YAHOO = "yahoo"


def predict_nsfw_faster(image_path):

    print("predicting nsfw for the image: ", image_path)

    model = OpenNsfwModel()

    with tf.Session() as sess:

        itype = InputType.TENSOR.name.lower()
        image_loader = IMAGE_LOADER_YAHOO

        input_type = InputType[itype.upper()]
        model.build(weights_path="open_nsfw-weights.npy", input_type=input_type)

        fn_load_image = None

        if input_type == InputType.TENSOR:
            if image_loader == IMAGE_LOADER_TENSORFLOW:
                fn_load_image = create_tensorflow_image_loader(tf.Session(graph=tf.Graph()))
            else:
                fn_load_image = create_yahoo_image_loader()
        elif input_type == InputType.BASE64_JPEG:
            import base64
            fn_load_image = lambda filename: np.array([base64.urlsafe_b64encode(open(filename, "rb").read())])

        sess.run(tf.global_variables_initializer())

        image = fn_load_image(image_path)

        predictions = \
            sess.run(model.predictions,
                     feed_dict={model.input: image})

        sfw_score = predictions[0][0]

        print("\tSFW score:\t{}".format(predictions[0][0]))
        print("\tNSFW score:\t{}".format(predictions[0][1]))

        if sfw_score > 0.94:
            return "sfw"
        else:
            return "nsfw"


def predict_nsfw(image_path):
    # change this as you see fit
    # image_path = sys.argv[1]

    # Read in the image_data
    image_data = tf.gfile.FastGFile(image_path, 'rb').read()

    # Loads label file, strips off carriage return
    label_lines = [line.rstrip() for line
                   in tf.gfile.GFile("retrained_labels.txt")]

    # Unpersists graph from file
    with tf.gfile.FastGFile("retrained_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

    with tf.Session() as sess:
        # Feed the image_data as input to the graph and get first prediction
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

        predictions = sess.run(softmax_tensor, \
                               {'DecodeJpeg/contents:0': image_data})

        # Sort to show labels of first prediction in order of confidence
        top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

        for node_id in top_k:
            human_string = label_lines[node_id]
            score = predictions[0][node_id]
            print('%s (score = %.5f)' % (human_string, score))

            if score > 0.60:
                return human_string


if __name__ == "__main__":
    print(predict_nsfw(sys.argv[1]))
