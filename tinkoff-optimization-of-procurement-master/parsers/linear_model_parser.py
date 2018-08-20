import math

import pandas as pd

from parsers import parser


class LinearModelParser(parser.IParser):

    __PROPORTION = 0.7

    def __init__(self):
        self.__train_samples_num = 0
        self.__list_of_instances = []
        self.__list_of_labels = []
        self.__list_of_samples = []
        self.__menu = set()

    @staticmethod
    def __parse_menu(filepath_or_buffer):
        df = pd.read_csv(filepath_or_buffer)
        indices = list(df["good_id"])
        indices = set(sorted(indices))
        return indices

    def __load_data(self, filepath_or_buffer, debug=True):
        n_rows = None
        if debug:
            n_rows = 10_000
        df = pd.read_csv(filepath_or_buffer, nrows=n_rows)

        indices = list(df["good_id"])
        self.__menu = set(sorted(indices))

        result = df.groupby(["chknum", "person_id", "month", "day"],
                            as_index=False).agg(list)
        list_of_instances = list(
            result.drop("good_id", axis=1).T.to_dict().values()
        )
        list_of_labels = list(result["good_id"])
        return list_of_instances, list_of_labels

    @staticmethod
    def __get_person_id(instance):
        return [instance["person_id"]]

    @staticmethod
    def __get_absolute_date(instance):
        return [365 * instance["day"] + 12 * instance["month"]]

    def __to_sample(self, instance):
        return self.__get_person_id(instance) \
               + self.__get_absolute_date(instance)

    @staticmethod
    def __to_interim_label(label):
        return math.log(label + 1)

    @staticmethod
    def __to_final_label(interim_label):
        return math.exp(interim_label) - 1

    def to_interim_label2(self, label):
        result = [0] * (max(self.__menu) + 1)
        for elem in label:
            result[elem] += 1
        return result

    @staticmethod
    def to_final_label2(interim_label):
        result = []
        for i, elem in enumerate(interim_label):
            if elem == 0:
                continue
            result += [i] * elem
        return result

    def parse(self, filepath_or_buffer, to_list=False, debug=False, **kwargs):
        self.__list_of_instances, self.__list_of_labels = self.__load_data(
            filepath_or_buffer
        )
        assert len(self.__list_of_instances) == len(self.__list_of_labels)
        assert self.to_final_label2(self.to_interim_label2(
            [24, 42, 42])) == [24, 42, 42]

        self.__list_of_samples = list(
            map(self.__to_sample, self.__list_of_instances)
        )

        if debug:
            print(self.__list_of_instances[:3])
            print(self.__list_of_labels[:3])
            print(self.__list_of_samples[:3])

        self.__train_samples_num = int(self.__PROPORTION
                                       * len(self.__list_of_labels))

    def get_train_data(self, debug=False):
        train_samples = self.__list_of_samples[:self.__train_samples_num]
        train_labels = list(
            map(self.to_interim_label2,
                self.__list_of_labels[:self.__train_samples_num])
        )
        if debug:
            train_labels = self.__list_of_labels[:self.__train_samples_num]
            print(train_samples, end="\n\n")
            print(train_labels)
        return train_samples, train_labels

    def get_validation_data(self, debug=False):
        validation_samples = self.__list_of_samples[self.__train_samples_num:]
        validation_labels = list(
            map(self.to_interim_label2,
                self.__list_of_labels[self.__train_samples_num:])
        )
        if debug:
            validation_labels = self.__list_of_labels[self.__train_samples_num:]
            print(validation_samples, end="\n\n")
            print(validation_labels)
        return validation_samples, validation_labels
