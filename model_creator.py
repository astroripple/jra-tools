from tensorflow.keras.layers import (
    Activation,
    Dense,
    Dropout,
    Flatten,
    GaussianDropout,
    GaussianNoise,
    Input,
    Conv1D,
    concatenate,
    Add,
)
from tensorflow.keras import Model


class ModelCreator:
    def __init__(self, num_trait):
        in_ = Input((18, num_trait))
        out = GaussianNoise(0.5)(in_)
        out = Conv1D(filters=128, kernel_size=1, padding="same")(out)

        out = self.middle_layer(out)
        out = self.middle_layer(out)
        out = self.middle_layer(out)
        out = self.middle_layer(out)
        out = Dropout(0.5)(out)

        # 出力層
        output_layers = [self.output_layer(out) for i in range(5)]

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
        in_conv = Conv1D(filters=128, kernel_size=3, padding="same", activation="selu")(
            input_layer
        )
        in_conv_conv = Conv1D(filters=128, kernel_size=3, padding="same")(in_conv)
        merged = Add()([in_conv_conv, input_layer])
        return Activation("selu")(merged)
