import numpy as np

import mlalgorithms.checks as checks

from . import model


class MostPopular(model.IModel):

    def __init__(self, num_popular_ids=5):
        super().__init__()
        self.num_popular_ids = num_popular_ids
        self.most_popular_goods = dict()

    def train(self, train_samples, train_labels, **kwargs):
        checks.check_equality(len(train_samples), len(train_labels),
                              message="Samples and labels have different "
                                      "sizes")
        self.most_popular_goods = kwargs["most_popular_goods"]

    def predict(self, samples, **kwargs):
        predictions = []
        for _ in samples:
            prediction = np.array(self.most_popular_goods)
            predictions.append(prediction)
        return predictions


class SameAsBefore(model.IModel):

    def __init__(self, num_popular_ids=5):
        super().__init__()
        self.num_popular_ids = num_popular_ids
        self.latest_orders = dict()
        self.most_popular_goods = dict()

    def train(self, train_samples, train_labels, **kwargs):
        checks.check_equality(len(train_samples), len(train_labels),
                              message="Samples and labels have different "
                                      "sizes")

        self.most_popular_goods = kwargs["most_popular_goods"]

        # Get person ids from train samples, samples format:
        # [[person_id, month, day], [person_id, month, day], ...].
        persons_ids = [person_data[0] for person_data in train_samples]
        self.latest_orders = dict(zip(persons_ids, train_labels))

    def predict(self, samples, **kwargs):
        predictions = []
        for sample in samples:
            if self.latest_orders.get(sample[0]) is None:
                prediction = np.array(self.most_popular_goods)
            else:
                prediction = np.array(self.latest_orders[sample[0]])
            predictions.append(prediction)
        return predictions


class MostPopularFromOwnOrders(model.IModel):

    def __init__(self, num_popular_ids):
        super().__init__()
        self.num_popular_ids = num_popular_ids

        checks.check_types(self.num_popular_ids, int,
                           var_name="num_popular_ids")
        checks.check_value(self.num_popular_ids, 0, 100, True, False,
                           var_name="num_popular_ids")

        self.orders = dict()
        self.most_popular_goods = dict()
        self.most_popular_good_ids = list()
        self.max_good_id = 0

    def process_orders(self):
        """
        Find most popular goods, then set popular good identifiers equal to
        one but other good identifiers equal to zero.
        """
        for person_orders in self.orders.values():
            non_zero_count = np.count_nonzero(person_orders)

            if non_zero_count < self.num_popular_ids:
                non_zero_ind = person_orders.argsort()[::-1][:non_zero_count]
                sub_index = []

                for index in self.most_popular_good_ids:
                    if index not in non_zero_ind:
                        sub_index.append(index)
                        non_zero_count += 1
                        if non_zero_count == self.max_good_id:
                            break

                if non_zero_count < self.num_popular_ids:
                    sub_index.extend(
                        np.random.randint(self.max_good_id + 1,
                                          size=(self.num_popular_ids -
                                                non_zero_count)).tolist()
                    )
                person_orders[sub_index] = 1
            else:
                indices = person_orders.argsort()[::-1][:self.num_popular_ids]
                not_in_indices = [x for x in range(len(person_orders))
                                  if x not in indices]
                person_orders[not_in_indices] = 0
                person_orders[indices] = 1

    def train(self, train_samples, train_labels, **kwargs):
        checks.check_equality(len(train_samples), len(train_labels),
                              message="Samples and labels have different "
                                      "sizes")

        self.most_popular_goods = kwargs["most_popular_goods"]
        self.most_popular_good_ids = kwargs["most_popular_good_ids"]

        checks.check_value(len(self.most_popular_good_ids),
                           lower=self.num_popular_ids, strict_less=False,
                           var_name="most_popular_good_ids")

        self.max_good_id = kwargs["max_good_id"]

        # Get person ids from train samples, samples format:
        # [[person_id, month, day], [person_id, month, day], ...].
        persons_ids = [person_data[0] for person_data in train_samples]
        for persons_id, label in zip(persons_ids, train_labels):
            if self.orders.get(persons_id) is None:
                self.orders[persons_id] = np.array(label)
            else:
                self.orders[persons_id] += np.array(label)

        self.process_orders()

    def predict(self, samples, **kwargs):
        predictions = []
        for sample in samples:
            if self.orders.get(sample[0]) is None:
                prediction = np.array(self.most_popular_goods)
            else:
                prediction = self.orders[sample[0]]
            predictions.append(prediction)
        return predictions
