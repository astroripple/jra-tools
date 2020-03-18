import keras
from keras.layers.core import Activation, Dense, Dropout, Flatten
from keras.layers.noise import GaussianDropout, GaussianNoise
from keras.layers import Input, Conv1D, merge
from keras.models import Model


class ModelCreator:
    def __init__(self, num_trait):
        in_ = Input((18, num_trait))
        merged = Conv1D(filters=128, kernel_size=1, padding="same")(in_)

        in_conv = Conv1D(filters=128, kernel_size=3, padding="same")(merged)
        in_conv_conv = Conv1D(
            filters=128, kernel_size=3, padding="same", activation="selu"
        )(in_conv)
        merged = keras.layers.add([in_conv_conv, in_conv])
        merged = Activation("selu")(merged)

        in_conv = Conv1D(filters=128, kernel_size=3, padding="same")(merged)
        in_conv_conv = Conv1D(
            filters=128, kernel_size=3, padding="same", activation="selu"
        )(in_conv)
        merged = keras.layers.add([in_conv_conv, in_conv])
        merged = Activation("selu")(merged)

        # 出力層
        out1 = Conv1D(filters=1, kernel_size=1)(merged)
        out1 = Flatten()(out1)
        out1 = Activation("softmax")(out1)

        out2 = Conv1D(filters=1, kernel_size=1)(merged)
        out2 = Flatten()(out2)
        out2 = Activation("softmax")(out2)

        out3 = Conv1D(filters=1, kernel_size=1)(merged)
        out3 = Flatten()(out3)
        out3 = Activation("softmax")(out3)

        out4 = Conv1D(filters=1, kernel_size=1)(merged)
        out4 = Flatten()(out4)
        out4 = Activation("softmax")(out4)

        out5 = Conv1D(filters=1, kernel_size=1)(merged)
        out5 = Flatten()(out5)
        out5 = Activation("softmax")(out5)

        # コンパイル
        model = Model(inputs=in_, outputs=[out1, out2, out3, out4, out5])
        model.compile(
            loss="categorical_crossentropy", optimizer="SGD", metrics=["accuracy"]
        )
        self.model = model
