import numpy as np

from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import ExtraTreeRegressor

from . import model


class DecisionTreeModel(model.IModel):

    def __init__(self, **kwargs):
        self.model = DecisionTreeRegressor(**kwargs)

    def train(self, train_samples, train_labels, **kwargs):
        self.model.fit(train_samples, train_labels, **kwargs)

    def predict(self, samples, **kwargs):
        predictions = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predictions.append(prediction)
        return predictions


class ExtraTreeModel(model.IModel):

    def __init__(self, **kwargs):
        self.model = ExtraTreeRegressor(**kwargs)

    def train(self, train_samples, train_labels, **kwargs):
        self.model.fit(train_samples, train_labels, **kwargs)

    def predict(self, samples, **kwargs):
        predictions = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predictions.append(prediction)
        return predictions
