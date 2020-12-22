import numpy as np
from matplotlib.dates import date2num
from matplotlib.transforms import Transform
import datetime as dt


class PathTranform(Transform):
    """
    Transforms a plot so that its x-axis is anchored to a given path.
    """
    input_dims = 2
    output_dims = 2
    has_inverse = False

    def __init__(self, path_x, path_y, xmin, xmax, scale=0.2):
        super().__init__()
        self._path_x = path_x
        self._path_y = path_y
        self._scale = scale

        self._xmin = date2num(xmin) if isinstance(xmin, dt.datetime) else xmin
        self._xmax = date2num(xmax) if isinstance(xmax, dt.datetime) else xmax

    def transform_non_affine(self, values):
        x_in = values[:, 0]
        y_in = values[:, 1]

        # find indices of corresponding path points
        n = len(self._path_x) - 1
        indices = ((x_in - self._xmin) / (self._xmax - self._xmin) * n).astype(int)
        indices[indices > n] = n
        indices[indices < 0] = 0

        # calculate normals on line segments
        nx = (self._path_y[indices] - self._path_y[indices - 1])
        ny = - (self._path_x[indices] - self._path_x[indices - 1])
        norm = np.sqrt(nx ** 2 + ny ** 2)
        nx /= norm
        ny /= norm

        x_out = self._path_x[indices] + y_in * nx * self._scale
        y_out = self._path_y[indices] + y_in * ny * self._scale

        return np.array([x_out, y_out]).T