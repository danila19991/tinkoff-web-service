import numpy as np

from sklearn.neighbors import KNeighborsRegressor

from ml_algorithm.models import model


class KNearestNeighborsModel(model.IModel):

    def __init__(self):
        self.model = KNeighborsRegressor()

    def train(self, train_samples, train_labels):
        self.model.fit(train_samples, train_labels)

    def predict(self, validation_samples, validation_labels):
        predicts = []
        for sample, label in zip(validation_samples, validation_labels):
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predicts.append(prediction)
        return predicts