import abc

import numpy as np
from sklearn.metrics import mean_squared_error, r2_score

from .models import model
from .parsers.common_parser import CommonParser


class Tester:

    def __init__(self, metric_name="MeanF1Score", border=0.5,
                 invert_list=["MeanF1Score"]):
        """
        Initializing object of main class with testing algorithm.

        :param metric_name: str, optional (default="MeanF1Score")
            Name of the metric to check quality.

        :param border: float, optional (default=0.5)
            The accuracy boundary at which the algorithm is considered to be
            exact.

        :param invert_list: list, optional (default=["MeanF1Score"])
            List of the metrics name which need to invert comparison with
            border.
        """
        self._metric_name = metric_name
        if type(self._metric_name) is not str:
            raise ValueError(f"metric_name parameter must be str: "
                             f"got {type(self._metric_name)}")

        class_ = globals()[self._metric_name]
        self._metric = class_(border)
        if not isinstance(self._metric, IMetric):
            raise ValueError(f"Metric is not subclass of IMetric. "
                             f"Provided type: {type(self._metric)}")

        self._invert_list = invert_list
        if type(self._invert_list) is not list:
            raise ValueError(f"invert_list parameter must be list: "
                             f"got {type(self._invert_list)}")

    def test(self, validation_labels, predictions, **kwargs):
        """
        Main testing function.

        :param predictions: array-like, sparse matrix
            Predicted data.

        :param validation_labels: array-like, sparse matrix
            Known data.

        :param kwargs: dict
            Additional arguments for metric test method.

        :return: float
            A numerical estimate of the accuracy of the algorithm.
        """
        return self._metric.test(validation_labels, predictions, **kwargs)

    def quality_control(self, validation_labels, predictions):
        """
        Function to get threshold estimation of the accuracy of the algorithm.

        :param predictions: array-like, sparse matrix
            Predicted data.

        :param validation_labels: array-like, sparse matrix
            Known data.

        :return: float
            Bool value which define quality of the algorithm.
        """
        invert_comparison = self._metric_name in self._invert_list
        return self._metric.quality_control(validation_labels, predictions,
                                            invert_comparison)


class IMetric(abc.ABC):

    def __init__(self, border):
        """
        Initializing object of testing algorithm's class.

        :param border: float
            The accuracy boundary at which the algorithm is considered to be
            exact.
        """
        self._border = border
        if type(self._border) is not float:
            raise ValueError(f"border parameter must be float: "
                             f"got {type(self._border)}.")
        if not (0.0 <= self._border <= 1.0):
            raise ValueError(f"border parameter must be in [0.0, 1.0]: "
                             f"got {self._border}.")

        self._cache = None

    @abc.abstractmethod
    def test(self, validation_labels, predictions, **kwargs):
        """
        Main testing function.

        :param predictions: array-like, sparse matrix
            Predicted data.

        :param validation_labels: array-like, sparse matrix
            Known data.

        :param kwargs: dict
            Additional arguments for test method.

        :return: float
            A numerical estimate of the accuracy of the algorithm.
        """
        raise NotImplementedError("Called abstract class method!")

    def quality_control(self, validation_labels, predictions,
                        invert_comparison=False):
        """
        Function to get threshold estimation of the accuracy of the algorithm.

        :param predictions: array-like, sparse matrix
            Predicted data.

        :param validation_labels: array-like, sparse matrix
            Known data.

        :param invert_comparison: bool
            Bool value that changes the direction of comparison

        :return: bool, optional (default=False)
            Bool value which define quality of the algorithm.
        """
        if self._cache is None:
            self._cache = self.test(validation_labels, predictions)

        if invert_comparison:
            return self._cache > self._border
        return self._cache < self._border


class MeanSquaredError(IMetric):

    def test(self, validation_labels, predictions, r2=False):
        """
        Main testing function.

        :param validation_labels: list
            List of lists with known data.

        :param predictions: list
            List of lists with predicted data.

        :param r2: bool, optional (default=False)
            Flag for additional metric.

        :return: float or tuple (float, float)
            A numerical estimate of the accuracy of the algorithm. 0.0 is
            perfect prediction. For r2 score 1.0 is perfect prediction.
        """
        self._cache = mean_squared_error(validation_labels, predictions)

        if r2:
            return self._cache, r2_score(validation_labels, predictions)
        return self._cache


class MeanF1Score(IMetric):

    @staticmethod
    def _format_data(validation_label, prediction):
        """
        Formatted input data.

        :param validation_label: list
            Known data.

        :param prediction: list
            Predicted data.

        :return: tuple (list, list)
            Return tuple with formatted lists.
        """
        int_prediction = [int(round(x)) for x in prediction]

        int_prediction = CommonParser.to_final_label(int_prediction)
        validation_label = CommonParser.to_final_label(validation_label)
        return int_prediction, validation_label

    @staticmethod
    def zero_check(conj, arr_len):
        """
        Check if goods list is empty.

        :param conj: int
            Cardinality of conjunction of two sets of goods.

        :param arr_len: int
            Cardinality of goods list.

        :return: int, float
            Return 0 if goods list is empty, otherwise division conj and
            arr_len.
        """
        if arr_len == 0:
            return 0
        else:
            return conj / arr_len

    @staticmethod
    def conjunction(lst1, lst2):
        """
        Calculate conjunction of two arrays. Arrays must be sorted!

        :param lst1: list
            First sorted array.

        :param lst2: list
            Second sorted arry.

        :return: int
            Cardinality of conjunction.
        """
        it1 = iter(lst1)
        it2 = iter(lst2)
        try:
            value1 = next(it1)
            value2 = next(it2)
        except StopIteration:
            return 0

        result = 0
        while True:
            try:
                if value1 == value2:
                    result += 1
                    value1 = next(it1)
                    value2 = next(it2)
                elif value1 > value2:
                    value2 = next(it2)
                else:
                    value1 = next(it1)
            except StopIteration:
                break

        return result

    def test_check(self, validation_label, prediction, need_format=False):
        """
        Main testing function for one list of data.

        :param validation_label: list
            Known data.

        :param prediction: list
            Predicted data.

        :param need_format: bool, optional (default=False)
            Used to define that data is not formatted.

        :return: float
            A numerical estimate of the accuracy of the algorithm. 1.0 is
            perfect prediction.
        """
        if need_format:
            validation_label, prediction = self._format_data(validation_label,
                                                             prediction)

        conj = self.conjunction(prediction, validation_label)

        p = self.zero_check(conj, len(prediction))
        r = self.zero_check(conj, len(validation_label))
        if p == 0 and r == 0:
            return 0
        return 2 * p * r / (p + r)

    def test(self, validation_labels, predictions, need_format=False):
        """
        Main testing function.

        :param validation_labels: list
            List of lists with known data.

        :param predictions: list
            List of lists with predicted data.

        :param need_format: bool, optional (default=False)
            Used to define that data is not formatted.

        :return: float
            A numerical estimate of the accuracy of the algorithm. 1.0 is
            perfect prediction.
        """
        assert self.conjunction([1, 1, 2, 3, 5], [1, 2, 4, 5]) == 3, \
            "There are error in conjunction method!"

        num_checks = len(validation_labels)
        result = [self.test_check(validation_labels[i],
                                  predictions[i],
                                  need_format) for i in range(num_checks)]
        self._cache = sum(result) / num_checks
        return self._cache


class TestModel(model.IModel):

    def train(self, train_samples, train_labels, **kwargs):
        if len(train_samples) != len(train_labels):
            raise ValueError(f"Samples and labels have different sizes: "
                             f"{len(train_samples)} != {len(train_labels)}")

    def predict(self, samples, **kwargs):
        if len(samples) != len(kwargs["labels"]):
            raise ValueError(f"Samples and labels have different sizes: "
                             f"{len(samples)} != {len(kwargs['labels'])}")

        predictions = []
        for _, label in zip(samples, kwargs["labels"]):
            prediction = np.array(label)
            predictions.append(prediction)
        return predictions
