import multiprocessing
import pickle
import time

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from amr_kitchen.utils import expand_array3d, shape_from_header

# from mpi4py.futures import MPIPoolExecutor

# Dict. with field names and their units after a volume integral
field_units = {
    "avg_pressure": "[J]",
    "density": "[kg]",
    "diffcoeff": "[m^5/s]",
    "divu": "[m^3 / s]",
    "enstrophy": "[J]",
    "FunctCall": "[-]",
    "gradp": "[N]",
    "HeatRelease": "[W]",
    "I_R": "[kg / s]",
    "kinetic_energy": "[J]",
    "lambda": "[W m^2 / K]",
    "mag_vort": "[m^3 / s]",
    "mass_fractions": "[-]",
    "mixture_fraction": "[-]",
    "progress_variable": "[-]",
    "Qcrit": "[-]",
    "rhoh": "[J]",
    "RhoRT": "[J]",
    "temp": "[K m^3]",
    "velocity": "[m^4/s]",
    "viscosity": "[J-s]",
    "vorticity": "[m^3 / s]",
}


def increment_sum_masked(args):
    """
    Increments sum with data from each bfile of a level
    """
    with open(args["file"], "rb") as bf:
        bf.seek(args["offset"])
        h = bf.readline()
        shape = shape_from_header(h.decode("ascii"))
        box_shape = (shape[0], shape[1], shape[2])
        # skip field_pos
        bf.seek(np.prod(box_shape) * args["id_int"] * 8, 1)
        # Only read the data from one box
        data = np.fromfile(bf, "float64", np.prod(box_shape))
        data = data.reshape(box_shape, order="F")
        if args["id_vol"] is not None:
            # skip volfrag_pos
            bf.seek(args["offset"])
            h = bf.readline()
            bf.seek(np.prod(box_shape) * args["id_vol"] * 8, 1)
            # Only read the data from one box
            data_volfrag = np.fromfile(bf, "float64", np.prod(box_shape))
            data_volfrag = data_volfrag.reshape(box_shape, order="F")
            return args["dV"] * np.sum(
                data[args["covering_mask"]] * data_volfrag[args["covering_mask"]]
            )
        else:
            return args["dV"] * np.sum(data[args["covering_mask"]])


def increment_sum(args):
    """
    Increments sum with data from each bfile of the finest level
    """
    with open(args["file"], "rb") as bf:
        bf.seek(args["offset"])
        h = bf.readline()
        shape = shape_from_header(h.decode("ascii"))
        box_shape = (shape[0], shape[1], shape[2])
        # skip field_pos
        bf.seek(np.prod(box_shape) * args["id_int"] * 8, 1)
        # Only read the data from one box
        data = np.fromfile(bf, "float64", np.prod(box_shape))
        data = data.reshape(box_shape, order="F")
        if args["id_vol"] is not None:
            # skip volfrag_pos
            bf.seek(args["offset"], 0)
            h = bf.readline()
            bf.seek(np.prod(box_shape) * args["id_vol"] * 8, 1)
            # Only read the data from one box
            data_volfrag = np.fromfile(bf, "float64", np.prod(box_shape))
            data_volfrag = data_volfrag.reshape(box_shape, order="F")
            return args["dV"] * np.sum(data * data_volfrag)
        else:
            return np.sum(data) * args["dV"]


def volume_integral(pck, field, limit_level=None, use_volfrac=False):
    """
    Prints the volume integral of the chosen field
    """
    # Integration field
    id_int = pck.fields[field]
    print(f"Integrating {field} in {pck.pfile}")
    # Lets check if volFrac is in the plotifile
    id_vol = None
    if "volFrac" in pck.fields and use_volfrac:
        id_vol = pck.fields["volFrac"]
        print(f"Using embedded boundary volFrac field")

    covering_masks = []
    for lv in range(pck.limit_level):  # Last level is not masked
        # use box indices in list
        lv_masks = []
        next_lv_factors = pck.grid_sizes[lv + 1] // pck.box_arrays[lv + 1].shape
        for idx, indices in enumerate(pck.cells[lv]["indexes"]):
            # Convert to box array indices at lv + 1
            barr_starts = np.array((indices[0] * 2) // next_lv_factors, dtype=int)
            barr_ends = np.array((indices[1] * 2) // next_lv_factors, dtype=int)
            next_level_boxes = pck.box_arrays[lv + 1][
                barr_starts[0] : barr_ends[0] + 1,
                barr_starts[1] : barr_ends[1] + 1,
                barr_starts[2] : barr_ends[2] + 1,
            ]
            # Convert the upper level box slice to lower level bool
            bcast_factor = next_lv_factors[0] // 2
            next_lv_map = expand_array3d(next_level_boxes, bcast_factor)
            mask = np.zeros_like(next_lv_map, dtype=bool)
            # mask is true where the value is -1
            mask[next_lv_map == -1] = 1
            # -1 means there is no box at this level
            lv_masks.append(mask)
        covering_masks.append(lv_masks)

    integral = 0
    pool = multiprocessing.Pool()
    if not limit_level:
        for lv in range(pck.limit_level):
            mp_calls = []
            dV = np.prod(pck.dx[lv])
            for bid, file, offset in zip(
                range(len(pck.boxes[lv])),
                pck.cells[lv]["files"],
                pck.cells[lv]["offsets"],
            ):
                mp_call = {
                    "file": file,
                    "offset": offset,
                    "id_vol": id_vol,
                    "id_int": id_int,
                    "covering_mask": covering_masks[lv][bid],
                    "dV": dV,
                }
                mp_calls.append(mp_call)
            now = time.time()
            print(f"Integrating level {lv}...")
            for box_int in tqdm(
                pool.imap(increment_sum_masked, mp_calls), total=len(mp_calls)
            ):
                integral += box_int
            print(f"Done! ({time.time() - now:.2f} s)")

    mp_calls = []
    dV = np.prod(pck.dx[pck.limit_level])
    for bid, file, offset in zip(
        range(len(pck.boxes[pck.limit_level])),
        pck.cells[pck.limit_level]["files"],
        pck.cells[pck.limit_level]["offsets"],
    ):

        mp_call = {
            "file": file,
            "offset": offset,
            "id_vol": id_vol,
            "id_int": id_int,
            "dV": dV,
        }
        mp_calls.append(mp_call)
    now = time.time()
    print(f"Integrating level {pck.limit_level}...")
    for box_int in tqdm(pool.imap(increment_sum, mp_calls), total=len(mp_calls)):
        integral += box_int
    print(f"Done! ({time.time() - now:.2f})")

    return integral
