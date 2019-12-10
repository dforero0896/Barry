import os
import pickle
import logging
import inspect
from abc import ABC

import numpy as np

from barry.datasets.dataset import Dataset


class CorrelationFunction(Dataset, ABC):
    def __init__(self, filename, name=None, min_dist=30, max_dist=200, recon=True, reduce_cov_factor=1, realisation=None):
        current_file = os.path.dirname(inspect.stack()[0][1])
        self.data_location = os.path.normpath(current_file + f"/../data/{filename}")
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.recon = recon

        with open(self.data_location, "rb") as f:
            self.data_obj = pickle.load(f)
        name = name or self.data_obj["name"] + " Recon" if recon else " Prerecon"
        super().__init__(name)

        self.cosmology = self.data_obj["cosmology"]
        self.all_data = self.data_obj["post-recon"] if recon else self.data_obj["pre-recon"]
        self.reduce_cov_factor = reduce_cov_factor
        if self.reduce_cov_factor == -1:
            self.reduce_cov_factor = len(self.all_data)
            self.logger.info(f"Setting reduce_cov_factor to {self.reduce_cov_factor}")

        self.cov, self.icov, self.data, self.mask = None, None, None, None
        self.set_realisation(realisation)
        self.set_cov()

    def set_realisation(self, realisation):
        if realisation is None:
            self.data = np.array(self.all_data).mean(axis=0)
        else:
            self.data = self.all_data[realisation]
        self.mask = (self.data[:, 0] >= self.min_dist) & (self.data[:, 0] <= self.max_dist)
        self.data = self.data[self.mask, :]

    def set_cov(self):
        covname = "post-recon cov" if self.recon else "pre-recon cov"
        if covname in self.data_obj:
            npoles = self.data.shape[1] - 1
            nin = len(self.mask)
            nout = self.data.shape[0]
            self.cov = np.empty((npoles * nout, npoles * nout))
            for i in range(npoles):
                iinlow, iinhigh = i * nin, (i + 1) * nin
                ioutlow, iouthigh = i * nout, (i + 1) * nout
                for j in range(npoles):
                    jinlow, jinhigh = j * nin, (j + 1) * nin
                    joutlow, jouthigh = j * nout, (j + 1) * nout
                    self.cov[ioutlow:iouthigh, joutlow:jouthigh] = self.data_obj[covname][iinlow:iinhigh, jinlow:jinhigh][np.ix_(self.mask, self.mask)]
        else:
            self._compute_cov()
        print(self.cov)
        self.cov /= self.reduce_cov_factor
        self.icov = np.linalg.inv(self.cov)

    def _compute_cov(self):
        # TODO: Generalise for other multipoles poles
        ad = np.array(self.all_data)
        if ad.shape[2] > 2:
            x0 = ad[:, self.mask, 2]
        else:
            x0 = ad[:, self.mask, 1]
        cov = np.cov(x0.T)
        self.set_cov(cov)

    def get_data(self):
        d = {"dist": self.data[:, 0], "cov": self.cov, "icov": self.icov, "name": self.name, "cosmology": self.cosmology, "num_mocks": len(self.all_data)}
        # Some data has xi0, xi0+xi2 or xi0+xi2+xi4
        d.update({"xi0": self.data[:, 1]})
        if self.data.shape[1] > 2:
            d.update({"xi2": self.data[:, 2]})
            if self.data.shape[1] > 3:
                d.update({"xi4": self.data[:, 3]})
        return [d]


if __name__ == "__main__":
    print("Calling a Generic model class as main does not do anything. Try running the Concrete class: ")
    print("dataset_correlation_function.py")
