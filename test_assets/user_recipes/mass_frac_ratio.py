import numpy as np

# Types
ArrayLike = np.ndarray


def recipe(field_indexes: list[int], box_array: ArrayLike) -> ArrayLike:
    """
    Y_ratio_H2_CH4
    """
    id_YH2 = field_indexes["Y(H2)"]
    id_YCH4 = field_indexes["Y(CH4)"]
    Y_H2 = box_array[:, :, :, id_YH2]
    Y_CH4 = box_array[:, :, :, id_YCH4]
    return Y_CH4 / Y_H2
