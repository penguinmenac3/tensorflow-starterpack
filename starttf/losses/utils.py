import tensorflow as tf


def overlay_classification_on_image(classification, rgb_image, scale=1):
    """
    Overlay a classification either 1 channel or 3 channels on an input image.
    :param classification: The classification tensor of shape [bach_size, v, u, 1] or [batch_size, v, u, 3].
                           The value range of the classification tensor is supposed to be 0 to 1.
    :param rgb_image: The input image of shape [batch_size, h, w, 3].
                      The input image value range is 0-255. And channel order is RGB.
                      If you have BGR you can use image[..., ::-1] to make it RGB.
    :param scale: The scale with which to multiply the size of the image to achieve the normal size.
    :return: The merged image tensor.
    """
    if not classification.get_shape()[3] in [1, 2, 3]:
        raise RuntimeError("The classification can either be of 1, 2 or 3 dimensions as last dimension, but shape is {}".format(classification.get_shape().as_list()))

    size = rgb_image.get_shape()[1:3]
    if classification.get_shape()[3] == 1:
        classification = tf.pad(classification, [[0, 0], [0, 0], [0, 0], [0, 2]], "CONSTANT")
    elif classification.get_shape()[3] == 2:
        classification = tf.pad(classification, [[0, 0], [0, 0], [0, 0], [0, 1]], "CONSTANT")
    casted_classification = tf.cast(classification, dtype=tf.float32)
    target_size = (int(classification.get_shape()[1] * scale), int(classification.get_shape()[2] * scale))
    scaled_image = tf.image.resize_images(casted_classification, size=target_size, method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    cropped_img = tf.image.crop_to_bounding_box(scaled_image, 0, 0, size[0], size[1])
    return 0.5 * rgb_image + 0.5 * 255 * cropped_img
