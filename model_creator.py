from tensorflow.keras.layers import Activation, Dense, Dropout, Flatten, GaussianDropout, GaussianNoise, Input, Conv1D, concatenate, Add
from tensorflow.keras import Model

class ModelCreator:
    def __init__(self, num_trait):
        in_ = Input((18, num_trait))
        merged = Conv1D(filters=128, kernel_size=1, padding="same")(in_)

        merged = self.middle_layer(merged)
        merged = self.middle_layer(merged)
        merged = self.middle_layer(merged)
        merged = Dropout(.5)(merged)

        # 出力層
        output_layers = [self.output_layer(merged) for i in range(5)]

        # コンパイル
        model = Model(inputs=in_, outputs=output_layers)
        model.compile(
            loss="categorical_crossentropy", optimizer="SGD", metrics=["accuracy"]
        )
        self.model = model

    def output_layer(self, input_layer):
        out = Conv1D(filters=1, kernel_size=1)(input_layer)
        out = Flatten()(out)
        return Activation("softmax")(out)

    def middle_layer(self, input_layer):
        in_conv = Conv1D(filters=128, kernel_size=3, padding="same")(input_layer)
        in_conv_conv = Conv1D(
            filters=128, kernel_size=3, padding="same", activation="selu"
        )(in_conv)
        merged = Add()([in_conv_conv, in_conv])
        return Activation("selu")(merged)
        