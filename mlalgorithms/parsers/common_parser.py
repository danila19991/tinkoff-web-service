import math

import pandas as pd

from . import parser


# Header: chknum, person_id, month, day, good, good_id
class CommonParser(parser.IParser):

    def __init__(self, proportion=0.7, raw_date=True, n_rows=None,
                 debug=False):
        self._train_samples_num = 0
        self._list_of_instances = []
        self._list_of_labels = []
        self._list_of_samples = []
        self._help_data = dict()
        self._chknums = list()
        self._most_popular_goods = list()

        self._proportion = proportion
        self._raw_date = raw_date
        self._n_rows = n_rows
        self._debug = debug

    @property
    def chknums(self):
        return self._chknums

    @property
    def help_data(self):
        return self._help_data

    @property
    def most_popular_goods(self):
        return self._most_popular_goods

    def max_good_id(self):
        result = 0
        for _, goods_and_chknums in self.help_data.items():
            temp_max = max(goods_and_chknums["good_id"])
            result = max(temp_max, result)
        return result

    @staticmethod
    def _sorted_by_date_train_data(df):
        dfgroup = df[["month", "day", "good_id",
                      "chknum", "person_id"]].groupby(
            ["month", "day"], as_index=False).agg(list)

        def func(x):
            return list(pd.Series(x).unique())

        dfgroup["good_id"] = dfgroup["good_id"].apply(func)
        dfgroup["chknum"] = dfgroup["chknum"].apply(func)
        dfgroup["person_id"] = dfgroup["person_id"].apply(func)

        return dfgroup.set_index(["month", "day"]).to_dict("index")

    @staticmethod
    def _sorted_by_date_test_data(df_set, df_menu):
        dfgroup_set = df_set.groupby(
            ["month", "day"], as_index=False).agg(list)

        dfgroup_menu = df_menu.groupby(
            ["month", "day"], as_index=False).agg(list)

        df = pd.merge(dfgroup_set, dfgroup_menu, on=["month", "day"])
        return df.set_index(["month", "day"]).to_dict("index")

    def _load_formatted_train_data(self, filepath_or_buffer):
        df = pd.read_csv(filepath_or_buffer, nrows=self._n_rows)
        dfgroup = df[["chknum", "person_id", "month", "day"]] \
            .groupby(["chknum", "person_id", "month", "day"], as_index=False) \
            .agg(list)

        dictionary = {}
        for index, row in dfgroup.iterrows():
            dictionary.setdefault((row["month"], row["day"]), []).append({
                "chknum": row["chknum"],
                "person_id": row["person_id"],
                "good_id": row["good_id"]
            })

        return dictionary

    def _load_train_data(self, filepath_or_buffer):
        df = pd.read_csv(filepath_or_buffer, nrows=self._n_rows)

        self._most_popular_goods = df["good_id"].value_counts().head().\
            index.tolist()
        self._help_data = self._sorted_by_date_train_data(df)

        result = df.groupby(["chknum", "person_id", "month", "day"],
                            as_index=False).agg(list)
        self._chknums = df["chknum"].unique().tolist()
        list_of_instances = list(
            result.drop("good_id", axis=1).T.to_dict().values()
        )
        list_of_labels = result["good_id"].tolist()
        return list_of_instances, list_of_labels

    def _load_test_data(self, filepath_or_buffer_set, filepath_or_buffer_menu):
        df_set = pd.read_csv(filepath_or_buffer_set)
        df_menu = pd.read_csv(filepath_or_buffer_menu)

        self._chknums = df_set["chknum"].tolist()
        self._help_data = self._sorted_by_date_test_data(
            df_set, df_menu
        )

        list_of_instances = list(df_set.T.to_dict().values())
        return list_of_instances

    @staticmethod
    def _get_person_id(instance):
        return [instance["person_id"]]

    def _get_absolute_date(self, instance):
        if self._raw_date:
            return [instance["month"], instance["day"]]
        return [12 * instance["month"] + 365 * instance["day"]]

    def _to_sample(self, instance):
        return (self._get_person_id(instance) +
                self._get_absolute_date(instance))

    def to_interim_label(self, label):
        result = [0] * (self.max_good_id() + 1)
        for elem in label:
            result[elem] += 1
        return result

    @staticmethod
    def to_final_label(interim_label):
        result = []
        for i, elem in enumerate(interim_label):
            if elem == 0:
                continue
            result += [i] * elem
        return result

    @staticmethod
    def to_interim_label_math(label):
        return math.log(label + 1)

    @staticmethod
    def to_final_label_math(interim_label):
        return math.exp(interim_label) - 1

    def get_menu_on_day_by_chknum(self, chknum):
        for date, value in self.help_data.items():
            if chknum in value["chknum"]:
                return value["good_id"]
        raise KeyError(f"No checks with given chknum={chknum}")

    def parse_train_data(self, filepath_or_buffer):
        self._list_of_instances, self._list_of_labels = self._load_train_data(
            filepath_or_buffer
        )

        assert len(self._list_of_instances) == len(self._list_of_labels), \
            "Instances of read data art not equal to their labels."
        assert self.to_final_label(self.to_interim_label(
            [24, 42, 42])) == [24, 42, 42], \
            "Processing data methods are not mutually inverse."

        self._list_of_samples = list(
            map(self._to_sample, self._list_of_instances)
        )

        if self._debug:
            print(len(self._list_of_instances))
            print(self._list_of_instances[:3])
            print(self._list_of_labels[:3])
            print(self._list_of_samples[:3])

        self._train_samples_num = int(self._proportion *
                                      len(self._list_of_labels))
        self._chknums = self._chknums[self._train_samples_num:]

    def parse_test_data(self, filepath_or_buffer_set,
                        filepath_or_buffer_menu):
        self._list_of_instances = self._load_test_data(
            filepath_or_buffer_set, filepath_or_buffer_menu
        )

        self._list_of_samples = list(
            map(self._to_sample, self._list_of_instances)
        )

        if self._debug:
            print(len(self._list_of_instances))
            print(self._list_of_instances[:3])
            print(self._list_of_samples[:3])

    def get_train_data(self):
        train_samples = self._list_of_samples[:self._train_samples_num]

        train_labels = list(map(
            self.to_interim_label,
            self._list_of_labels[:self._train_samples_num])
        )

        if self._debug:
            print(train_samples[:3], end="\n\n")
            print(train_labels[:3])
        return train_samples, train_labels

    def get_validation_data(self):
        validation_samples = self._list_of_samples[self._train_samples_num:]

        validation_labels = list(map(
            self.to_interim_label,
            self._list_of_labels[self._train_samples_num:])
        )

        if self._debug:
            print(validation_samples[:3], end="\n\n")
            print(validation_labels[:3])
        return validation_samples, validation_labels

    def get_test_data(self):
        if self._debug:
            print(self._list_of_samples[:3])
        return self._list_of_samples
