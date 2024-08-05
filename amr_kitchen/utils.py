import numpy as np

# Types
ArrayLike = np.ndarray

class TastesBadError(Exception):
    """
    Custom exception to tell that something
    is wrong with a plotfile
    """

    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return repr(self.value)


# TODO: replace with more specific errors
# depending on where the problem is
class BadTastingHeadersError(Exception):
    pass


class BadTastingBinariesError(Exception):
    pass


def expand_array3d(arr, factor: int) -> ArrayLike:
    """
    Data reading utility
    ----
    Expand lower resolution 2D array by [factor]
    to broadcast it to a higher level grid.
    This allows broadcasting lower resolution arrays to a higher
    AMR level grid without altering the data.
    ----
    """
    return np.repeat(
        np.repeat(np.repeat(arr, factor, axis=0),
                  factor, axis=1),
        factor, axis=2
    )


def shape_from_header(h: str) -> list[int]:
    """
    Infer the shape the box and the number of fields
    from the header in a plotfile binary file
    (Only works for 3D plotfiles)
    h: string of the header line
    """
    start, stop, _, nfields = h.split()[-4:]
    nfields = int(nfields)
    start = np.array(start.split("(")[-1].replace(")", "").split(","),
                     dtype=int)
    stop = np.array(stop.replace("(", "").replace(")", "").split(","),
                    dtype=int)
    shape = stop - start + 1
    total_shape = np.append(shape, nfields)
    return total_shape


def indices_from_header(h: str) -> list[ArrayLike]:
    """
    Infer the shape the box and the number of fields
    from the header in a plotfile binary file
    (Only works for 3D plotfiles)
    header: bytestring of the header line
    """
    start, stop, _, nfields = h.split()[-4:]
    nfields = int(nfields)
    start = np.array(start.split("(")[-1].replace(")", "").split(","),
                     dtype=int)
    stop = np.array(stop.replace("(", "").replace(")", "").split(","),
                    dtype=int)
    return [start, stop]


def header_from_indices(start: list[int], stop: list[int], nfields: int) -> bytes:
    """
    Creates a binary file header from the box
    global indices and number of fields
    start: start indices
    stop: stop indices
    nfields: number of fields in the plotfile
    """
    header_const = "FAB ((8, (64 11 52 0 1 12 0 1023)),(8, (8 7 6 5 4 3 2 1)))"
    header_indices = ("((" + ','.join([f"{s}" for s in start]) + ")"
                      " (" + ','.join([f"{s}" for s in stop]) + ")"
                      " (" + ','.join(["0" for _ in start]) + f")) {nfields}\n")
    header = header_const + header_indices
    return header.encode("ascii")


def indexes_and_shape_from_header(header: bytes) -> tuple[list[list],
                                                          list[list],
                                                          tuple[int, ...]]:
    """
    This takes the byte string of a box header in a plotfile binary
    file and infers the indexes of the box and the number of fields
    in the plotfile
    """
    h = header.decode("ascii")
    start, stop, _, nfields = h.split()[-4:]
    nfields = int(nfields)
    start = np.array(start.split("(")[-1].replace(")", "").split(","),
                     dtype=int)
    stop = np.array(stop.replace("(", "").replace(")", "").split(","),
                    dtype=int)
    shape = stop - start + 1
    shape = [s for s in shape]
    shape.append(nfields)
    return [start, stop], tuple(shape)


def shapes_from_header_vardims(header: bytes, ndim: int) -> list[int]:
    """
    Function to infer the data shape from the
    binary header which also words for 2D
    plotfiles
    """
    h = header.decode("ascii")
    start, stop, _, nfields = h.split()[-4:]
    nfields = int(nfields)
    start = np.array(start.split("(")[-1].replace(")", "").split(","),
                     dtype=int)
    stop = np.array(stop.replace("(", "").replace(")", "").split(","),
                    dtype=int)
    shape = stop - start + 1
    total_shape = []
    for i in range(ndim):
        total_shape.append(shape[i])
    total_shape.append(nfields)
    return total_shape


def global2local(indices: list[list], refindices: list[list], n_ghost: int=1) -> list[list]:
    """
    Convert global box indexes to indexes in a
    ghost cell padded reference box
    """
    i_start = max(refindices[0][0] - n_ghost, 0)
    j_start = max(refindices[0][1] - n_ghost, 0)
    k_start = max(refindices[0][2] - n_ghost, 0)
    return [
        [indices[0][0] - i_start, indices[0][1] - j_start, indices[0][2] - k_start],
        [indices[1][0] - i_start, indices[1][1] - j_start, indices[1][2] - k_start],
    ]
