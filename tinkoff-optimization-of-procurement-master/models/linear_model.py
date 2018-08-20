import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import RidgeCV

from models import model


class LinearModel(model.IModel):

    def __init__(self):
        self.model = LinearRegression()

    def train(self, train_samples, train_labels):
        self.model.fit(train_samples, train_labels)

    def predict(self, validation_samples, validation_labels):
        predicts = []
        for sample, label in zip(validation_samples, validation_labels):
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predicts.append(prediction)
        return predicts


class RidgeCVModel(LinearModel):

    def __init__(self):
        super().__init__()
        self.model = RidgeCV()
