import abc

import numpy as np

import mlalgorithms.checks as checks


class IModel(abc.ABC):

    @abc.abstractmethod
    def train(self, train_samples, train_labels, **kwargs):
        """
        Train current model.

        :param train_samples: array-like, sparse matrix.
            Training data.

        :param train_labels: array-like, sparse matrix.
            Target values. Will be cast to train_samples’s dtype if necessary.

        :param kwargs: dict, optional(default={}).
            Additional keyword arguments.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def predict(self, samples, **kwargs):
        """
        Makes predictions based on the transmitted data.
        User must override this method.

        :param samples: array-like, sparse matrix.
            Data for prediction.

        :param kwargs: dict, optional(default={}).
            Additional keyword arguments.

        :return: array.
            Returns predicted values.
        """
        raise NotImplementedError("Called abstract class method!")


class SimpleModel(IModel):

    def __init__(self, model=None):
        """
        Constructor of abstract model class which initialize model for working.

        :param model: object.
            Instance of model class.
        """
        if type(self) is IModel:
            raise Exception("IModel is an abstract class and cannot be "
                            "instantiated directly")
        self.model = model

    def train(self, train_samples, train_labels, **kwargs):
        """
        Train current model.

        :param train_samples: array-like, sparse matrix.
            Training data.

        :param train_labels: array-like, sparse matrix.
            Target values. Will be cast to train_samples’s dtype if necessary.

        :param kwargs: dict, optional(default={}).
            Additional keyword arguments.
        """
        checks.check_equality(len(train_samples), len(train_labels),
                              message="Samples and labels have different "
                                      "sizes")

        self.model.fit(train_samples, train_labels, **kwargs)

    def predict(self, samples, **kwargs):
        """
        Makes predictions based on the transmitted data.
        User must override this method.

        :param samples: array-like, sparse matrix.
            Data for prediction.

        :param kwargs: dict, optional(default={}).
            Additional keyword arguments.

        :return: array.
            Returns predicted values.
        """
        predictions = []
        for sample in samples:
            prediction = self.model.predict(np.array(sample).reshape(1, -1))[0]
            predictions.append(prediction)
        return predictions
