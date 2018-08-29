import numpy as np
import pandas as pd

from sklearn.cluster import KMeans

import mlalgorithms.checks as checks

from . import model


class ClusteringModel(model.SimpleModel):

    def __init__(self, **kwargs):
        super().__init__(KMeans(**kwargs))

        self.COL_NAME = "cluster"
        self.CLUSTER_BORDER = 6

        self.orders = {}
        self.clustering_table = pd.DataFrame()
        self.largest_cluster_goods = []

    def train(self, train_samples, train_labels, **kwargs):
        checks.check_equality(len(train_samples), len(train_labels),
                              message="Samples and labels have different "
                                      "sizes")

        persons_ids = [person_data[0] for person_data in train_samples]
        for persons_id, label in zip(persons_ids, train_labels):
            if self.orders.get(persons_id) is None:
                self.orders[persons_id] = np.array(label)
            else:
                self.orders[persons_id] += np.array(label)

        self.clustering_table = pd.DataFrame(
            self.model.fit_predict(pd.DataFrame.from_dict(self.orders,
                                                          orient="index")),
            columns=[self.COL_NAME]
        )

        cluster_id = self.clustering_table[self.COL_NAME]\
            .value_counts().index[0]
        larg_clust_center = self.model.cluster_centers_[cluster_id]
        self.largest_cluster_goods = (larg_clust_center >=
                                      self.CLUSTER_BORDER).astype(np.int)

    def predict(self, samples, **kwargs):
        predictions = []
        for i in samples:
            if i[0] in self.clustering_table.index:
                cluster_id = self.clustering_table.at[i[0], self.COL_NAME]
                clust_center = self.model.cluster_centers_[cluster_id]
                prediction = (clust_center >=
                              self.CLUSTER_BORDER).astype(np.int)
            else:
                prediction = np.array(self.largest_cluster_goods)
            predictions.append(prediction)
        return predictions
