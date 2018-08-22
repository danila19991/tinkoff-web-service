import math

import pandas as pd

from . import parser


# Header: chknum, person_id, month, day, good, good_id
class CommonParser(parser.IParser):

    def __init__(self, proportion=0.7, raw_date=True, n_rows=None,
                 not_parse_data=False, debug=False):
        self._train_samples_num = 0
        self._list_of_instances = []
        self._list_of_labels = []
        self._list_of_samples = []
        self._menu = set()
        self._chknums = list()

        self._proportion = proportion
        self._raw_date = raw_date
        self._n_rows = n_rows
        self._not_parse_data = not_parse_data
        self._debug = debug

    @staticmethod
    def _parse_menu(filepath_or_buffer):
        df = pd.read_csv(filepath_or_buffer)
        indices = list(df["good_id"])
        indices = set(sorted(indices))
        return indices

    def _load_raw_data(self, filepath_or_buffer):
        df = pd.read_csv(filepath_or_buffer, nrows=self._n_rows)

        indices = list(df["good_id"])
        self._menu = set(sorted(indices))

        self._chknums = df["chknum"].tolist()
        list_of_instances = list(
            df.drop("good_id", axis=1).values.tolist()
        )
        list_of_labels = list(df["good_id"])
        return list_of_instances, list_of_labels

    def _load_train_data(self, filepath_or_buffer):
        df = pd.read_csv(filepath_or_buffer, nrows=self._n_rows)

        indices = list(df["good_id"])
        self._menu = set(sorted(indices))

        result = df.groupby(["chknum", "person_id", "month", "day"],
                            as_index=False).agg(list)
        self._chknums = df["chknum"].tolist()
        list_of_instances = list(
            result.drop("good_id", axis=1).T.to_dict().values()
        )
        list_of_labels = list(result["good_id"])
        return list_of_instances, list_of_labels

    def _load_formatted_train_data(self, filepath_or_buffer):
        df = pd.read_csv(filepath_or_buffer, nrows=self._n_rows)
        dfgroup = df[["chknum", "month", "day", "person_id"]] \
            .groupby(["chknum", "month", "day", "person_id"], as_index=False) \
            .agg(list)
        dictionary = {}
        for index, row in dfgroup.iterrows():
            dictionary.setdefault((row['month'], row['day']), []).append(
                {"chknum": row["chknum"],
                 "person_id": row["person_id"],
                 "good_id": row["good_id"]})
        return dictionary

    @staticmethod
    def _load_menu_from_data(df):
        dfgroup = df[['month', 'day', 'good_id']] \
            .groupby(['month', 'day'], as_index=False) \
            .agg(list)
        dfgroup['good_id'] = dfgroup['good_id'] \
            .apply(lambda x: list(pd.Series(x).unique()))
        return dfgroup.set_index(['month', 'day']).to_dict('index')

    def _load_test_data(self, filepath_or_buffer_set, filepath_or_buffer_menu):
        df = pd.read_csv(filepath_or_buffer_set)
        self._chknums = df["chknum"].tolist()
        self._menu = self._parse_menu(filepath_or_buffer_menu)

        list_of_instances = list(df.T.to_dict().values())

        return list_of_instances

    def _get_person_id(self, instance):
        if self._not_parse_data:
            return [instance[1]]
        return [instance["person_id"]]

    def _get_absolute_date(self, instance):
        if self._not_parse_data:
            if self._raw_date:
                return [instance[2]] + [instance[3]]
            return [12 * instance[2] + 365 * instance[3]]

        if self._raw_date:
            return [instance["month"]] + [instance["day"]]
        return [12 * instance["month"] + 365 * instance["day"]]

    def _to_sample(self, instance):
        return self._get_person_id(instance) + \
               self._get_absolute_date(instance)

    def to_interim_label(self, label):
        result = [0] * (max(self._menu) + 1)
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

    @property
    def chknums(self):
        return self._chknums

    def parse_train_data(self, filepath_or_buffer):
        if not self._not_parse_data:
            self._list_of_instances, self._list_of_labels = \
                self._load_train_data(filepath_or_buffer)
        else:
            self._list_of_instances, self._list_of_labels = \
                self._load_raw_data(filepath_or_buffer)

        assert len(self._list_of_instances) == len(self._list_of_labels)
        assert self.to_final_label(self.to_interim_label(
            [24, 42, 42])) == [24, 42, 42]

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

        func = self.to_interim_label
        if self._not_parse_data:
            func = self.to_interim_label_math
        train_labels = list(
            map(func, self._list_of_labels[:self._train_samples_num])
        )

        if self._debug:
            print(train_samples[:3], end="\n\n")
            print(train_labels[:3])
        return train_samples, train_labels

    def get_validation_data(self):
        validation_samples = self._list_of_samples[self._train_samples_num:]

        func = self.to_interim_label
        if self._not_parse_data:
            func = self.to_interim_label_math
        validation_labels = list(
            map(func, self._list_of_labels[self._train_samples_num:])
        )

        if self._debug:
            print(validation_samples[:3], end="\n\n")
            print(validation_labels[:3])
        return validation_samples, validation_labels

    def get_test_data(self):
        if self._debug:
            print(self._list_of_samples[:3])
        return self._list_of_samples
