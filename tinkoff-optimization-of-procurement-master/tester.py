import abc
import json

from sklearn.metrics import mean_squared_error, r2_score

from parsers.linear_model_parser import LinearModelParser as lmp


class Tester:

    def __init__(self, config_filename="ml_config.json", border=0.5):
        """
        Initializing object of main class with testing algorithm.

        :param config_filename: str
            Name of the json file with configuration.

        :param border: float
            The accuracy boundary at which the algorithm is considered to be
            exact.
        """
        with open(config_filename, "r") as f:
            self.__parsed_json = json.loads(f.read())

        self.__bad_metric_alarm = bool(self.__parsed_json["bad_metric_alarm"])

        self.__invert_list = ["MeanF1Score"]

        self.__metric_name = self.__parsed_json["metric_name"]
        if self.__metric_name == "MeanSquaredError":
            self.__tester = MeanSquaredError(border)
        elif self.__metric_name == "MeanF1Score":
            self.__tester = MeanF1Score(border)
        else:
            raise ValueError("No metric with given name!")

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
        return self.__tester.test(validation_labels, predictions)

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
        invert_comparison = self.__metric_name in self.__invert_list
        return self.__tester.quality_control(validation_labels, predictions,
                                             invert_comparison)


class Metric(abc.ABC):

    def __init__(self, border=0.5):
        """
        Initializing object of testing algorithm's class.

        :param border: float
            The accuracy boundary at which the algorithm is considered to be
            exact.
        """
        self.__border = border
        self.__cache = None

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

        :return: bool
            Bool value which define quality of the algorithm.
        """
        if self.__cache is None:
            self.__cache = self.test(validation_labels, predictions)

        if invert_comparison:
            return self.__cache > self.__border
        return self.__cache < self.__border


class MeanSquaredError(Metric):

    def test(self, validation_labels, predictions, r2=False):
        """
        Main testing function.

        :param validation_labels: list
            List of lists with known data.

        :param predictions: list
            List of lists with predicted data.

        :param r2: bool
            Flag for additional metric.

        :return: float
            A numerical estimate of the accuracy of the algorithm.
        """
        self.__cache = mean_squared_error(validation_labels, predictions)

        # Explained variance score (r2_score): 1 is perfect prediction.
        if r2:
            return self.__cache, r2_score(validation_labels, predictions)
        return self.__cache


class MeanF1Score(Metric):

    @staticmethod
    def zero_check(conj, arr_len):
        if arr_len == 0:
            return 0
        else:
            return conj / arr_len

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
        y_z = [x for x, p in zip(validation_label, int_prediction)
               if x == p and x != 0]
        conj = len(y_z)
        int_prediction = lmp.to_final_label2(int_prediction)
        validation_label = lmp.to_final_label2(validation_label)
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

        :param r2: bool
            Flag for additional metric.

        :return: float
            A numerical estimate of the accuracy of the algorithm.
        """
        num_checks = len(validation_labels)
        result = [self.test_check(validation_labels[i],
                                  predictions[i]) for i in range(num_checks)]
        self.__cache = sum(result) / num_checks
        return self.__cache


def tester_testing():
    tester = Tester("ml_config.json", 0.5)

    sv = [[0, 1, 2, 0, 1, 0, 0]]
    predict = [[0, 2, 1, 1, 1, 0, 0]]

    print(tester.test(sv, predict))


if __name__ == "__main__":
    tester_testing()
