import abc


class IModel(abc.ABC):

    @abc.abstractmethod
    def train(self, train_samples, train_labels):
        """
        Train current model.

        :param train_samples: array-like, sparse matrix
            Training data.

        :param train_labels: array-like, sparse matrix
            Target values. Will be cast to train_samples’s dtype if necessary.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def predict(self, sample):
        """
        Makes predictions based on the transmitted data.
        User must override this method.

        :param sample: array-like, sparse matrix
            Data for prediction.

        :return: array
            Returns predicted values.
        """
        raise NotImplementedError("Called abstract class method!")
