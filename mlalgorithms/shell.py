import pickle
import os.path

import numpy as np
import pandas as pd

from .logger import decor_class_logging_error_and_time, setup_logging

from .tester import Tester

from .parsers.parser import IParser
from .parsers.common_parser import CommonParser
from .parsers.config_parsers import ConfigParser

from .models.model import IModel


file_path = os.path.abspath(os.path.dirname(__file__))
ml_config_path = os.path.join(file_path, "ml_config.json")
log_config_path = os.path.join(file_path, "log_config.json")

setup_logging(log_config_path)


@decor_class_logging_error_and_time()
class Shell:

    def __init__(self, existing_model_name=""):
        """
        Constructor which initialize class fields.

        :param existing_model_name: str, optional (default="")
            Name of the existing model file.
        """
        self._validation_labels = None
        self._predictions = None
        self._config_parser = ConfigParser(ml_config_path)
        self._tester = Tester(
            self._config_parser.get_metric()
        )

        self._model_parameters = self._config_parser.get_params_for("model")
        self._parser_parameters = self._config_parser.get_params_for("parser")

        if not existing_model_name:
            self._model = self._config_parser.get_instance(
                self._model_parameters["class_name"],
                self._model_parameters["module_name"],
                **self._model_parameters["params"]
            )
        else:
            self.load_model(existing_model_name)

        self._parser = self._config_parser.get_instance(
            self._parser_parameters["class_name"],
            self._parser_parameters["module_name"],
            **self._parser_parameters["params"],
            debug=self.is_debug()
        )

        assert self._check_interfaces()

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

    def is_raw_data(self, flag_name="not_parse_data"):
        """
        Return status of the raw data flag in the parser parameters.

        :param flag_name: str, optional (not_parse_data="")
            Name of the flag in config.

        :return: bool
            Value of the flag.
        """
        return self._parser_parameters[2][flag_name]

    def get_formatted_predictions(self, raw_data=False):
        """
        Format raw results of prediction.

        :param raw_data: bool, optional (default=False)
            Define if shell has not parsed data.

        :return: pd.DataFrame
            Formatted predictions.
        """
        predictions = [x.tolist() for x in self._predictions]

        if not raw_data:
            predictions = [[int(round(x)) for x in lst] for lst in predictions]
            predictions = [CommonParser.to_final_label(x)
                           for x in predictions]
            formatted_output = [{
                    "chknum": chknum,
                    "pred": " ".join(str(x) for x in pred)
                } for chknum, pred in zip(self._parser.chknums, predictions)
            ]
        else:
            assert len(self._parser.chknums) == len(self._predictions)
            predictions = [int(round(CommonParser.to_final_label_math(x)))
                           for x in predictions]
            formatted_output = [{
                    "chknum": chknum,
                    "pred": pred
                } for chknum, pred in zip(self._parser.chknums, predictions)
            ]
            predictions = pd.DataFrame(formatted_output, dtype=np.int64)
            predictions = predictions.groupby("chknum",
                                              as_index=False).agg(list)
            predictions = predictions.values.tolist()
            formatted_output = [{
                    "chknum": chknum,
                    "pred": " ".join(str(x) for x in pred)
                } for chknum, pred in predictions
            ]
        return pd.DataFrame(formatted_output, dtype=np.int64)

    def output(self, output_filename="result.csv"):
        """
        Output current prediction to filename.

        :param output_filename: str, file or buffer
            optional (default="result.csv")
            Filename to output.
        """
        out = self.get_formatted_predictions(raw_data=self.is_raw_data())
        out.to_csv(output_filename, index=False)

    def train(self, filepath_or_buffer):
        """
        Train model on input dataset.

        :param filepath_or_buffer: str, pathlib.Path, py._path.local.LocalPath
            or any object with a read() method (such as a file handle or
            StringIO)
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.
        """
        self._parser.parse_train_data(filepath_or_buffer)

        if self._config_parser["selected_model"] == "CatBoostModel":
            train_samples, train_labels = self._parser.get_train_data()
            train_num = int(self._parser_parameters[2]["proportion"] *
                            len(train_samples))
            self._model.train(
                train_samples[:train_num], train_labels[:train_num],
                eval_set=(train_samples[train_num:], train_labels[train_num:])
            )
        else:
            self._model.train(*self._parser.get_train_data())

        validation_samples, self._validation_labels = \
            self._parser.get_validation_data()

        self._predictions = self._model.predict(validation_samples)

    def predict(self, filepath_or_buffer_set, filepath_or_buffer_menu):
        """
        Make predictions on input dataset.

        :param filepath_or_buffer_set: same as train filepath_or_buffer.

        :param filepath_or_buffer_menu: same as train filepath_or_buffer.
        """
        self._parser.parse_test_data(filepath_or_buffer_set,
                                     filepath_or_buffer_menu)

        self._predictions = self._model.predict(self._parser.get_test_data())

    def test(self):
        """
        Test prediction quality of algorithm.

        :return tuple (float, float)
            Pair of two values from tester class.
        """
        test_result = self._tester.test(self._validation_labels,
                                        self._predictions)

        quality = self._tester.quality_control(self._validation_labels,
                                               self._predictions)

        return test_result, quality

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
