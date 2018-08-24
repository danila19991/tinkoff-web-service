import numpy as np

from catboost import CatBoostRegressor

from . import model


class CatBoostModel(model.IModel):

    def __init__(self, **kwargs):
        self.model = CatBoostRegressor(**kwargs)

    def train(self, train_samples, train_labels, **kwargs):
        self.model.fit(train_samples, train_labels, **kwargs)

    def predict(self, samples, **kwargs):
        predictions = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1),
                                            **kwargs)[0]
            predictions.append(prediction)
        return predictions
