import os
import multiprocessing
from p_tqdm import p_map
import time
import numpy as np
import argparse


def main():
    # Argument parser
    parser = argparse.ArgumentParser(
            description="Post processing utilisty for AMReX plotfiles")

    parser.add_argument(
            "plotfile", type=str,
            help="Path of the plotfile to cook")
    parser.add_argument(
            "--recipe", "-r", type=str,
            help=("Path to a script containing a recipe function, or"
                  "key of a predetermine function (see --help)"))
    parser.add_argument(
            "--mech", "-m", type=str,
            help=("Path to a Cantera kinetics mechanism (if the recipe"
                  " uses Cantera)"))
    parser.add_argument(
            "--output", "-o", type=str,
            help="Output path to store the post processing")

    args = parser.parse_args()

    if args.mech is not None:
        os.environ["CANTERA_MECH"] = args.mech

    from mandoline import HeaderData, parallel_cook

    # what are we cooking
    if args.recipe.split('.')[-1] == 'py':
        pass
    else:
        from mandoline.cookbook import recipes
        recipe = recipes[args.recipe]

    # Header data
    hdr = HeaderData(args.plotfile)
    # Create the output structure
    hdr.make_dir_tree(args.output)

    # Store new file offsets
    new_offsets = {}
    # START COOKING
    for Lv in range(hdr.limit_level + 1):
        cook_start = time.time()
        print(f"Cooking Level {Lv}...")
        level_files = np.array(hdr.cells[f"Lv_{Lv}"]["files"])
        cell_head_r = os.path.join(hdr.pfile,
                                   hdr.cell_paths[Lv] + '_H')
        # So we can use index
        call_args = []
        # For unique(cell_files)
        for bfile in np.unique(level_files):

            # Indexes of cells in the binary file
            cell_indexes = np.arange(level_files.shape[0])[level_files == bfile]
            # Path to the new binary file
            bfile_w = os.path.join(args.output,
                                   hdr.cell_paths[Lv].split('/')[0],
                                   bfile.split('/')[-1])
            mp_args = {"bfile":bfile,
                       "bfile_w":bfile_w,
                       "indexes":np.array(hdr.cells[f"Lv_{Lv}"]["indexes"])[cell_indexes],
                       "cell_indexes":cell_indexes,
                       "offsets_r":np.array(hdr.cells[f"Lv_{Lv}"]["offsets"])[cell_indexes],
                       "nvars":hdr.nvars,
                       "fields":hdr.fields,
                       "recipe":recipe,
                       "ncells":len(level_files)}
            call_args.append(mp_args)
        # One process per file
        #with multiprocessing.Pool() as pool:
        new_offsets_stack = p_map(parallel_cook, call_args)
        print(f"Done!", f"({np.around(time.time() - cook_start, 2)} s)")
        # Reduce arrays together
        new_offsets[Lv] = np.sum(new_offsets_stack, axis=0)

        # Update the new Cell header
        cell_head_w = os.path.join(args.output, hdr.cell_paths[Lv] + "_H")

        with open(cell_head_w, 'w') as ch_w, open(cell_head_r, 'r') as ch_r:
            # First two lines
            for i in range(2):
                l = ch_r.readline()
                ch_w.write(l)
            _ = ch_r.readline()
            ch_w.write("1\n")
            while True:
                l = ch_r.readline()
                if "FabOnDisk:" in l:
                    new_l = l.split()[:-1]
                    new_l.append(str(new_offsets[Lv][0]))
                    ch_w.write(' '.join(new_l) + "\n")
                    break
                else:
                    ch_w.write(l)
            for fst in new_offsets[Lv][1:]:
                l = ch_r.readline()
                new_l = l.split()[:-1]
                new_l.append(str(fst))
                ch_w.write(' '.join(new_l) + "\n")
            for l in ch_r:
                ch_w.write(l)

    # Update the plotfile header
    header_r = os.path.join(hdr.pfile, 'Header')
    header_w = os.path.join(args.output, 'Header')
    with open(header_r, 'r') as hr, open(header_w, 'w') as hw:
        # Version
        hw.write(hr.readline())
        _ = hr.readline()
        # Number of fields
        hw.write("1\n")
        for i in range(hdr.nvars):
            _ = hr.readline()
        # First word in recipe function
        hw.write(recipe.__doc__.split()[0] + '\n')
        # Rest of header (test if can be removed)
        for l in hr:
            hw.write(l)

if __name__ == "__main__":
    main()