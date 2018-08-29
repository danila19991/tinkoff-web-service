from sklearn.multioutput import MultiOutputRegressor

from catboost import CatBoostRegressor

from . import model


class CatBoostModel(model.SimpleModel):

    def __init__(self, **kwargs):
        super().__init__(MultiOutputRegressor(CatBoostRegressor(**kwargs)))

    @staticmethod
    def get_weights_by_date(instances):
        weights = []
        for instance in instances:
            weights.append(12 * instance[1] + 365 * instance[2])
        return weights
