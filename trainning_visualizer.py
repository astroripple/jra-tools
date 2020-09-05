import matplotlib.pyplot as plt

def draw_train_results(history):
    """
    トレーニング結果を描画する
    parameters
    ----------
    history : dict
        model.fit()で出力されるhistoryオブジェクトのhistoryフィールド
    """
    for key in history:
        if 'val' in key:
            plt.plot(history.get(key[4:]))
            plt.plot(history.get(key))
            plt.title(key[4:])
            plt.ylabel(key[4:])
            plt.xlabel('Epoch')
            plt.legend(['Train', 'Test'], loc='upper left')
            plt.show()