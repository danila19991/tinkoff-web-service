import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge

from . import model


class LinearModel(model.IModel):

    def __init__(self, **kwargs):
        self.model = LinearRegression(**kwargs)

    def train(self, train_samples, train_labels, **kwargs):
        self.model.fit(train_samples, train_labels, **kwargs)

    def predict(self, samples, **kwargs):
        predictions = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predictions.append(prediction)
        return predictions


class RidgeModel(LinearModel):

    def __init__(self, **kwargs):
        super().__init__()
        self.model = Ridge(**kwargs)
