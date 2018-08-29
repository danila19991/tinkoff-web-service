from sklearn.tree import DecisionTreeRegressor
from sklearn.tree import ExtraTreeRegressor

from . import model


class DecisionTreeModel(model.SimpleModel):

    def __init__(self, **kwargs):
        super().__init__(DecisionTreeRegressor(**kwargs))


class ExtraTreeModel(model.SimpleModel):

    def __init__(self, **kwargs):
        super().__init__(ExtraTreeRegressor(**kwargs))
