import abc
import math

import pandas as pd


class IParser(abc.ABC):

    @property
    @abc.abstractmethod
    def chknums(self):
        """
        Return chknum lists for formatted output.

        :return: list.
            List with chknums.
        """
        raise NotImplementedError("Called abstract class method!")

    @property
    @abc.abstractmethod
    def most_popular_good_ids(self):
        """
        Return most popular good ids calculated during parsing.

        :return: list.
            List with most popular good ids.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def max_good_id(self):
        """
        Calculate max good id for transforming to interim labels.

        :return: int.
            Max good id from parsed data.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def get_menu_on_day_by_chknum(self, chknum):
        """
        Find daily menu by chknum number.

        :param chknum: str.
            Chknum identifier.

        :return: list.
            List with daily menu which contains good ids for day with chknum.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def to_interim_label(self, label):
        """
        Transform label to interim label for model training.

        :param label: float.
            Value to transform.

        :return: float.
            Transformed value.
        """
        raise NotImplementedError("Called abstract class method!")

    @staticmethod
    @abc.abstractmethod
    def to_final_label(interim_label):
        """
        Restore the original value of interim label.

        :param interim_label: float.
            Value to restore.

        :return: float.
            Restored value.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def parse_train_data(self, filepath_or_buffer):
        """
        Parse data from csv, clean and return it as data frame or list. Used to
        work with train data.

        :param filepath_or_buffer: str, pathlib.Path, py._path.local.LocalPath
            or any object with a read() method (such as a file handle or
            StringIO)
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.

        :return: pd.DataFrame, list
            Returns result of pd.read_csv method or converted list.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def parse_test_data(self, filepath_or_buffer_set, filepath_or_buffer_menu):
        """
        Parse data from csv, clean and return it as data frame or list. Used to
        work with test data.

        :param filepath_or_buffer_set: str, pathlib.Path,
            py._path.local.LocalPath or any object with a read() method
            (such as a file handle or StringIO).
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.

        :param filepath_or_buffer_menu: str, pathlib.Path,
            py._path.local.LocalPath or any object with a read() method
            (such as a file handle or StringIO).
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.

        :return: pd.DataFrame, list.
            Returns result of pd.read_csv method or converted list.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def get_train_data(self):
        """
        Get data for model training from training set.

        :return: tuple of two array-like, sparse matrix.
            Returns parsed data.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def get_validation_data(self):
        """
        Get data for test model prediction from validate set.

        :return: tuple of two array-like, sparse matrix.
            Returns parsed data.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def get_test_data(self):
        """
        Get data for model prediction from test set.

        :return: tuple of two array-like, sparse matrix.
            Returns parsed data.
        """
        raise NotImplementedError("Called abstract class method!")


class SimpleParser:

    @staticmethod
    def clean_data(df):
        """
        Clean data frame from NaN values.
        Method will be improved when we get dataset.

        :param df: pd.DataFrame.
            Data frame object.

        :return: pd.DataFrame.
            Cleaned data frame object.
        """
        return df.dropna()

    @staticmethod
    def to_list(df):
        """
        Convert data frame to list.

        :param df: pd.DataFrame.
            Data frame object.

        :return: list.
            Converted list.
        """
        return df.values.tolist()

    @staticmethod
    def one_hot_encoding(df):
        """
        Convert categorical variable into dummy/indicator variables.

        :param df: pd.DataFrame.
            Data frame object.

        :return: pd.DataFrame.
            Converted with one-hot encoding data frame.
        """
        return pd.get_dummies(df)

    def parse(self, filepath_or_buffer, to_list=False, **kwargs):
        """
        Parse data from csv, clean and return it as data frame or list.

        :param filepath_or_buffer: str, pathlib.Path, py._path.local.LocalPath
            or any object with a read() method (such as a file handle or
            StringIO).
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.

        :param to_list: bool, optional (default=False).
            Specifies whether to return the list.

        :param kwargs: dict, optional(default={}).
            Passes additional arguments to the pd.read_csv method.

        :return: pd.DataFrame, list.
            Returns result of pd.read_csv method or converted list.
        """
        df = pd.read_csv(filepath_or_buffer, **kwargs)
        df = self.clean_data(df)
        if to_list:
            return self.to_list(df)
        return df

    @staticmethod
    def to_interim_label(label):
        """
        Transform label to interim label for model training.

        :param label: float.
            Value to transform.

        :return: float.
            Transformed value.
        """
        return math.log(label + 1)

    @staticmethod
    def to_final_label(interim_label):
        """
        Restore the original value of interim label.

        :param interim_label: float.
            Value to restore.

        :return: float.
            Restored value.
        """
        return math.exp(interim_label) - 1
