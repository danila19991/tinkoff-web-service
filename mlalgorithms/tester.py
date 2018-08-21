import abc

from sklearn.metrics import mean_squared_error, r2_score

from .parsers.linear_model_parser import LinearModelParser


class Tester:

    def __init__(self, metric_name="MeanF1Score", border=0.5):
        """
        Initializing object of main class with testing algorithm.

        :param metric_name: str
            Name of the metric to check quality.

        :param border: float
            The accuracy boundary at which the algorithm is considered to be
            exact.
        """
        self._invert_list = ["MeanF1Score"]

        self._metric_name = metric_name
        class_ = globals()[self._metric_name]
        self._tester = class_(border)

    def test(self, validation_labels, predictions):
        """
        Main testing function.

        :param predictions: array-like, sparse matrix
            Predicted data.

        :param validation_labels: array-like, sparse matrix
            Known data.

        :return: float
            A numerical estimate of the accuracy of the algorithm.
        """
        return self._tester.test(validation_labels, predictions)

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
        return self._tester.quality_control(validation_labels, predictions,
                                            invert_comparison)


class Metric(abc.ABC):

    def __init__(self, border=0.5):
        """
        Initializing object of testing algorithm's class.

        :param border: float
            The accuracy boundary at which the algorithm is considered to be
            exact.
        """
        self._border = border
        self._cache = None

    @abc.abstractmethod
    def test(self, validation_labels, predictions):
        """
        Main testing function.

        :param predictions: array-like, sparse matrix
            Predicted data.

        :param validation_labels: array-like, sparse matrix
            Known data.

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


class MeanSquaredError(Metric):

    def test(self, validation_labels, predictions, r2=False):
        """
        Main testing function.

        :param validation_labels: list
            List of lists with known data.

        :param predictions: list
            List of lists with predicted data.

        :param r2: bool, optional (default=False)
            Flag for additional metric.

        :return: float
            A numerical estimate of the accuracy of the algorithm.
        """
        self._cache = mean_squared_error(validation_labels, predictions)

        # Explained variance score (r2_score): 1 is perfect prediction.
        if r2:
            return self._cache, r2_score(validation_labels, predictions)
        return self._cache


class MeanF1Score(Metric):

    @staticmethod
    def zero_check(conj, arr_len):
        if arr_len == 0:
            return 0
        else:
            return conj / arr_len

    @staticmethod
    def conjunction(lst1, lst2):
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

    def test_check(self, validation_label, prediction):
        """
        Main testing function for one list of data.

        :param prediction: list
            Predicted data.

        :param validation_label: list
            Known data.

        :return: float
            A numerical estimate of the accuracy of the algorithm.
        """
        assert len(validation_label) == len(prediction)

        int_prediction = [int(round(x)) for x in prediction]

        int_prediction = LinearModelParser.to_final_label(int_prediction)
        validation_label = LinearModelParser.to_final_label(validation_label)

        conj = self.conjunction(int_prediction, validation_label)

        p = self.zero_check(conj, len(int_prediction))
        r = self.zero_check(conj, len(validation_label))
        if p == 0 and r == 0:
            return 0
        return 2 * p * r / (p + r)

    def test(self, validation_labels, predictions):
        """
        Main testing function.

        :param validation_labels: list
            List of lists with known data.

        :param predictions: list
            List of lists with predicted data.

        :return: float
            A numerical estimate of the accuracy of the algorithm.
        """
        assert self.conjunction([1, 1, 2, 3, 5], [1, 2, 4, 5]) == 3

        num_checks = len(validation_labels)
        result = [self.test_check(validation_labels[i],
                                  predictions[i]) for i in range(num_checks)]
        self._cache = sum(result) / num_checks
        return self._cache
