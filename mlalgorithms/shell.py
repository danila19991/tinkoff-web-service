import pickle
import os.path

import numpy as np
import pandas as pd

from .logger import decor_class_logging_error_and_time, setup_logging

from .tester import Tester

from .parsers.parser import IParser
from .parsers.linear_model_parser import LinearModelParser
from .parsers.config_parsers import ConfigParser

from .models.model import IModel


my_path = os.path.abspath(os.path.dirname(__file__))
ml_config_path = os.path.join(my_path, "ml_config.json")
log_config_path = os.path.join(my_path, "log_config.json")

setup_logging(log_config_path)


@decor_class_logging_error_and_time()
class Shell:

    def __init__(self, model_exists=False):
        """
        Constructor which initialize class fields.

        :param model_exists: bool, optional (default=False)
            Name of the json file with configuration.
        """
        self._validation_labels = None
        self._predictions = None
        self._config_parser = ConfigParser(ml_config_path)
        self._tester = Tester(
            self._config_parser["metric_name"]
        )

        self._model_parameters = self._config_parser["model_parameters"]
        self._parser_parameters = self._config_parser["parser_parameters"]

        if not model_exists:
            self._model = self._config_parser.get_instance(
                self._config_parser["model_name"],
                self._config_parser["model_module_name"],
                **self._model_parameters
            )

        self._parser = self._config_parser.get_instance(
            self._config_parser["parser_name"],
            self._config_parser["parser_module_name"],
            **self._parser_parameters,
            debug=self.is_debug()
        )

        assert self._check_interfaces()

    def _input(self, filepath_or_buffer, **kwargs):
        """
        An additional method that loads data and divides it into test and
        validation samples.

        :param filepath_or_buffer: same as Parser.parse or self.predict

        :param kwargs: dict
            Passes additional arguments to the parser.parse method.
        """
        self._parser.parse(filepath_or_buffer, to_list=True, **kwargs)

    def _check_interface(self, instance, parent_class):
        """
        Checks the classes on the according interfaces.

        :param instance: object
            Object to check.

        :param parent_class: class
            Class to verify.

        :return: bool
            Results of verifying.
        """
        return isinstance(instance, parent_class)

    def _check_interfaces(self):
        """
        Checks parser and model classes on the according interfaces.

        :return: bool
            Status of verifying.
        """
        check1 = self._check_interface(self._parser, IParser)
        check2 = self._check_interface(self._model, IModel)
        return check1 and check2

    def is_debug(self, flag_name="debug"):
        """
        Return debug status of the program.

        :param flag_name: str, optional (default="debug")
            Name of the debug flag in config.

        :return: bool
            Value of debug flag.
        """
        return self._config_parser[flag_name]

    @property
    def predictions(self):
        """
        Get current results of prediction.

        :return: list
            Current predictions.
        """
        return self._predictions

    def get_formatted_predictions(self):
        """
        Format raw results of prediction.

        :return: list
            Formatted predictions.
        """
        predictions = [x.tolist() for x in self._predictions]
        int_prediction = [[int(round(x)) for x in lst] for lst in predictions]
        predictions = [LinearModelParser.to_final_label(x)
                       for x in int_prediction]
        return predictions

    def output(self, output_filename="result"):
        """
        Output current prediction to filename.

        :param output_filename: str, optional (default="result")
            Filename to output.
        """
        predictions = self.get_formatted_predictions()

        out = pd.DataFrame(predictions, dtype=np.int64)
        out.to_csv(f"{output_filename}.csv", index=False, header=False)

    def predict(self, filepath_or_buffer, **kwargs):
        """
        Train model on input dataset.

        :param filepath_or_buffer: str, pathlib.Path, py._path.local.LocalPath
            or any object with a read() method (such as a file handle or
            StringIO)
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.

        :param kwargs: dict
            Passes additional arguments to the parser.parse method.
        """
        self._input(filepath_or_buffer, **kwargs)
        self._model.train(*self._parser.get_train_data())

        validation_samples, self._validation_labels = \
            self._parser.get_validation_data()

        self._predictions = self._model.predict(validation_samples,
                                                self._validation_labels)

    def train(self):
        pass

    def test(self):
        """
        Test prediction quality of algorithm.
        """
        test_result = self._tester.test(self._validation_labels,
                                        self._predictions)

        quality = self._tester.quality_control(self._validation_labels,
                                               self._predictions)

        print(f"Metrics: {test_result}")
        print(f"Quality satisfaction: {quality}")

    def load_model(self, filename="model"):
        """
        Load trained model with all parameters from file.

        :param filename: str, optional (default="model")
            Filename of model.
        """
        with open(f"models/{filename}.mdl", "rb") as input_stream:
            self._model = pickle.loads(input_stream.read())

    def save_model(self, filename="model"):
        """
        Save trained model with all parameters to file.

        :param filename: str, optional (default="model")
            Filename of model.
        """
        with open(f"models/{filename}.mdl", "wb") as output_stream:
            output_stream.write(pickle.dumps(self._model.model))
