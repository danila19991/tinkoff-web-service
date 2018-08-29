from sklearn.neighbors import KNeighborsRegressor

from . import model


class KNearestNeighborsModel(model.SimpleModel):

    def __init__(self, **kwargs):
        super().__init__(KNeighborsRegressor(**kwargs))
