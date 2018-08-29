from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge

from . import model


class LinearModel(model.SimpleModel):

    def __init__(self, **kwargs):
        super().__init__(LinearRegression(**kwargs))


class RidgeModel(model.SimpleModel):

    def __init__(self, **kwargs):
        super().__init__(Ridge(**kwargs))
