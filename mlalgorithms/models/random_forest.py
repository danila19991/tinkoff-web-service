import numpy as np

from sklearn.ensemble import ExtraTreesRegressor

from . import model


class ExtraTreesModel(model.IModel):

    def __init__(self, **kwargs):
        self.model = ExtraTreesRegressor(**kwargs)

    def train(self, train_samples, train_labels):
        self.model.fit(train_samples, train_labels)

    def predict(self, validation_samples, validation_labels):
        predicts = []
        for sample, label in zip(validation_samples, validation_labels):
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predicts.append(prediction)
        return predicts

