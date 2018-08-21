import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RidgeCV

from . import model


class LinearModel(model.IModel):

    def __init__(self, **kwargs):
        self.model = LinearRegression(**kwargs)

    def train(self, train_samples, train_labels):
        self.model.fit(train_samples, train_labels)

    def predict(self, samples):
        predicts = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predicts.append(prediction)
        return predicts


class RidgeCVModel(LinearModel):

    def __init__(self, **kwargs):
        super().__init__()
        self.model = RidgeCV(**kwargs)
