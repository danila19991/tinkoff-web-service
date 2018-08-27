import numpy as np

from sklearn.multioutput import MultiOutputRegressor

from catboost import CatBoostRegressor

from . import model


class CatBoostModel(model.IModel):

    def __init__(self, **kwargs):
        self.model = MultiOutputRegressor(CatBoostRegressor(**kwargs))

    @staticmethod
    def get_weights_by_date(instances):
        weights = []
        for instance in instances:
            weights.append(12 * instance[1] + 365 * instance[2])
        return weights

    def train(self, train_samples, train_labels, **kwargs):
        self.model.fit(train_samples, train_labels)

    def predict(self, samples, **kwargs):
        predictions = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predictions.append(prediction)
        return predictions
