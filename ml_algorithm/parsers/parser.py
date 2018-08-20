import abc

import pandas as pd
import matplotlib.pyplot as plt


class IParser(abc.ABC):

    def clean_data(self, df):
        """
        Clean data frame from NaN values.
        Method will be improved when we get dataset.

        :param df: pd.DataFrame
            Data frame object.

        :return: pd.DataFrame
            Cleaned data frame object.
        """
        return df.dropna()

    def to_list(self, df):
        """
        Convert data frame to list.

        :param df: pd.DataFrame
            Data frame object.

        :return: list
            Converted list.
        """
        return df.values.tolist()

    def one_hot_encoding(self, df):
        """
        Convert categorical variable into dummy/indicator variables.

        :param df: pd.DataFrame
            Data frame object.

        :return: pd.DataFrame
            Converted with one-hot encoding data frame.
        """
        return pd.get_dummies(df)

    @abc.abstractmethod
    def parse(self, filepath_or_buffer, to_list=False, **kwargs):
        """
        Parse data from csv, clean and return it as data frame or list.

        :param filepath_or_buffer: str, pathlib.Path, py._path.local.LocalPath
            or any object with a read() method (such as a file handle or
            StringIO)
            The string could be a URL. Valid URL schemes include http, ftp, s3,
            and file. For file URLs, a host is expected. For instance, a local
            file could be file://localhost/path/to/table.csv.

        :param to_list: bool, optional (default=False)
            Specifies whether to return the list.

        :param kwargs: dict
            Passes additional arguments to the pd.read_csv method.

        :return: pd.DataFrame, list
            Returns result of pd.read_csv method or converted list.
        """
        df = pd.read_csv(filepath_or_buffer, **kwargs)
        df = self.clean_data(df)
        if to_list:
            return self.to_list(df)
        return df

    @abc.abstractmethod
    def get_train_data(self):
        """
        Get data for model training.

        :return: tuple of two array-like, sparse matrix
            Returns parsed data.
        """
        raise NotImplementedError("Called abstract class method!")

    @abc.abstractmethod
    def get_validation_data(self):
        """
        Get data for model prediction.

        :return: tuple of two array-like, sparse matrix
            Returns parsed data.
        """
        raise NotImplementedError("Called abstract class method!")


"""
Example of using parsers:
    parser = Parser()
    df = parser.parse("data/food/food.csv", to_list=True)
    print(df)
    df.plot(figsize=(15, 10))
    plt.show()
"""
