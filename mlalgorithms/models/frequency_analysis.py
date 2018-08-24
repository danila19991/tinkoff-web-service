import numpy as np

from . import model


class EatMostPopular(model.IModel):

    def __init__(self, **kwargs):
        self.most_popular_goods = dict()

    def train(self, train_samples, train_labels, **kwargs):
        assert len(train_samples) == len(train_labels), \
            f"Samples and labels have different sizes: " \
            f"{len(train_samples)} != {len(train_labels)}"
        self.most_popular_goods = kwargs["most_popular_goods"]

    def predict(self, samples, **kwargs):
        predictions = []
        for _ in samples:
            prediction = np.array(self.most_popular_goods)
            predictions.append(prediction)
        return predictions


class EatSameAsBefore(model.IModel):

    def __init__(self, **kwargs):
        self.latest_orders = dict()
        self.most_popular_goods = dict()

    def train(self, train_samples, train_labels, **kwargs):
        assert len(train_samples) == len(train_labels), \
            f"Samples and labels have different sizes: " \
            f"{len(train_samples)} != {len(train_labels)}"

        self.most_popular_goods = kwargs["most_popular_goods"]

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


class EatMostPopularFromOwnOrders(model.IModel):

    def __init__(self, **kwargs):
        self.latest_orders = dict()
        self.most_popular_goods = dict()

    def train(self, train_samples, train_labels, **kwargs):
        assert len(train_samples) == len(train_labels), \
            f"Samples and labels have different sizes: " \
            f"{len(train_samples)} != {len(train_labels)}"

        self.most_popular_goods = kwargs["most_popular_goods"]

        persons_ids = [person_data[0] for person_data in train_samples]
        for persons_id, label in zip(persons_ids, train_labels):
            if self.latest_orders.get(persons_id) is None:
                self.latest_orders[persons_id] = label
            else:
                self.latest_orders[persons_id].extend(label)

    def predict(self, samples, **kwargs):
        predictions = []
        for sample in samples:
            if self.latest_orders.get(sample[0]) is None:
                prediction = np.array(self.most_popular_goods)
            else:
                prediction = np.array(self.latest_orders[sample[0]])
            predictions.append(prediction)
        return predictions
