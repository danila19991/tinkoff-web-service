import numpy as np

from sklearn.neighbors import KNeighborsRegressor

from . import model


class KNearestNeighborsModel(model.IModel):

    def __init__(self, **kwargs):
        self.model = KNeighborsRegressor(**kwargs)

    def train(self, train_samples, train_labels, **kwargs):
        self.model.fit(train_samples, train_labels)

    def predict(self, samples, **kwargs):
        predicts = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predicts.append(prediction)
        return predicts
