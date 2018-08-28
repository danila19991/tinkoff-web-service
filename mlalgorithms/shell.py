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

    def __init__(self, existing_model_name=None,
                 existing_parsed_json_dict=None):
        """
        Constructor which initializes class fields.

        :param existing_model_name: str, optional (default=None)
            Name of the existing model file.

        :param existing_parsed_json_dict: dict, optional (default=None)
            If config file was parsed, you can pass it to this class.
        """
        self._validation_labels = None
        self._predictions = None
        self._config_parser = ConfigParser(existing_parsed_json_dict,
                                           ml_config_path)
        self._tester = Tester(
            self._config_parser.get_metric(),
            **self._config_parser.get_tester_params()
        )

        self._model_parameters = self._config_parser.get_params_for("model")
        self._parser_parameters = self._config_parser.get_params_for("parser")

        if existing_model_name is None:
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

        # ATTENTION: pickle dumps is not equal to created model and parser
        # classes.
        if existing_model_name is None:
            self._check_interfaces()

    @property
    def predictions(self):
        """
        Get current results of prediction.

        :return: list
            Current predictions.
        """
        return self._predictions

    def _check_interfaces(self):
        """
        Checks parser and model classes on the according interfaces.
        """
        if not isinstance(self._parser, IParser):
            raise ValueError(f"Parser is not subclass of IParser. "
                             f"Provided type: {type(self._parser)}")

        if not isinstance(self._model, IModel):
            raise ValueError(f"Model is not subclass of IModel. "
                             f"Provided type: {type(self._parser)}")

    def _format_predictions_by_menu(self, chknums, predictions):
        """
        Remove goods which are not in menu on day.

        :param chknums: list
            List of checks.

        :param predictions: list
            List of predictions returned by predict method. Need to round float
            values in the lists and transform all np.arrays to list.

        :return: list
            Right predictions without inconsistencies with the menu.
        """
        for chknum, pred_goods in zip(chknums, predictions):
            daily_menu = self._parser.get_menu_on_day_by_chknum(chknum)
            for it, pred_good in enumerate(pred_goods):
                if pred_good not in daily_menu:
                    pred_goods.pop(it)

    def _process_empty_predictions(self, predictions):
        """
        If we have empty prediction, extend them by most popular goods.

        :param predictions: list
            List of predictions returned by predict method. Need to round float
            values in the lists and transform all np.arrays to list.
        """
        for prediction in predictions:
            if not prediction:
                prediction.extend(self._parser.most_popular_good_ids)

    def _format_predictions(self):
        if self._predictions is None:
            return

        self._predictions = [x.tolist() for x in self._predictions]

        self._predictions = [[int(round(x)) for x in lst]
                             for lst in self._predictions]
        self._predictions = [CommonParser.to_final_label(x)
                             for x in self._predictions]

        self._process_empty_predictions(self._predictions)
        self._format_predictions_by_menu(self._parser.chknums,
                                         self._predictions)

    def _get_formatted_predictions(self):
        """
        Format raw results of prediction.

        :return: pd.DataFrame
            Formatted predictions.
        """
        formatted_output = [{
                "chknum": chknum,
                "pred": " ".join(str(x) for x in pred)
            } for chknum, pred in zip(self._parser.chknums, self._predictions)
        ]
        return pd.DataFrame(formatted_output, dtype=np.int64)

    def is_debug(self, flag_name="debug"):
        """
        Return debug status of the program.

        :param flag_name: str, optional (default="debug")
            Name of the debug flag in config.

        :return: bool
            Value of debug flag.
        """
        return self._config_parser[flag_name]

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

        train_samples, train_labels = self._parser.get_train_data()
        if (self._config_parser["selected_model"] == "MostPopular" or
                self._config_parser["selected_model"] == "SameAsBefore"):
            self._model.train(
                train_samples, train_labels,
                most_popular_goods=self._parser.to_interim_label(
                    self._parser.most_popular_good_ids
                )
            )
        elif (self._config_parser["selected_model"] ==
              "MostPopularFromOwnOrders"):
            self._model.train(
                train_samples, train_labels,
                most_popular_goods=self._parser.to_interim_label(
                    self._parser.most_popular_good_ids
                ),
                most_popular_good_ids=self._parser.most_popular_good_ids,
                max_good_id=self._parser.max_good_id()
            )
        else:
            self._model.train(train_samples, train_labels)

        if self._parser_parameters["params"]["proportion"] != 1.0:
            validation_samples, self._validation_labels = \
                self._parser.get_validation_data()

            if self._config_parser["selected_model"] == "TestModel":
                self._predictions = self._model.predict(
                    validation_samples,
                    labels=self._validation_labels
                )
            else:
                self._predictions = self._model.predict(validation_samples)

            self._format_predictions()

    def predict(self, filepath_or_buffer_set, filepath_or_buffer_menu):
        """
        Make predictions on input dataset.

        :param filepath_or_buffer_set: str, pathlib.Path,
            py._path.local.LocalPath or any object with a read() method
            (such as a file handle or StringIO)
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.

        :param filepath_or_buffer_menu: str, pathlib.Path,
            py._path.local.LocalPath or any object with a read() method
            (such as a file handle or StringIO)
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.
        """
        self._parser.parse_test_data(filepath_or_buffer_set,
                                     filepath_or_buffer_menu)

        self._predictions = self._model.predict(self._parser.get_test_data())
        self._format_predictions()

    def test(self):
        """
        Test prediction quality of algorithm.

        :return: tuple (float, float) or tuple (None, None)
            Pair of two values from tester class. Or None if nothing to test.
        """
        if self._predictions is None:
            print("Nothing to test!")
            return None, None

        test_result = self._tester.test(self._parser.answers_for_train,
                                        self._predictions)
        quality = self._tester.quality_control(self._parser.answers_for_train,
                                               self._predictions)

        return test_result, quality

    def output(self, output_filename="result.csv"):
        """
        Output current prediction to filename.

        :param output_filename: str, file or buffer
            optional (default="result.csv")
            Filename to output.
        """
        if self._predictions is None:
            print("Nothing to output!")
            return

        out = self._get_formatted_predictions()
        out.to_csv(output_filename, index=False)

    def load_model(self, filename="model.mdl"):
        """
        Load trained model with all parameters from file.

        :param filename: str, optional (default="model.mdl")
            Filename of model.
        """
        with open(filename, "rb") as input_stream:
            self._model = pickle.loads(input_stream.read())

    def save_model(self, filename="model.mdl"):
        """
        Save trained model with all parameters to file.

        :param filename: str, optional (default="model.mdl")
            Filename of model.
        """
        with open(filename, "wb") as output_stream:
            output_stream.write(pickle.dumps(self._model))
