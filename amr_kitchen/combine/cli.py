import sys
from .combine import parse_inputs
import argparse
from amr_kitchen import PlotfileCooker

def list_of_strings(arg):
    arg = [argument.strip() for argument in arg.split(",")]
    return arg

def main():
    # Argument parser
    parser = argparse.ArgumentParser(
            description="Combine two AMReX plotfiles")

    parser.add_argument(
            "plotfile1", type=str,
            help="Path of the first plotfile to combine")
    parser.add_argument(
            "plotfile2", type=str,
            help="Path of the second plotfile to combine")
    
    parser.add_argument(
            "--output", "-o", type=str,
            help="Output path to store the combined plotfile")
    parser.add_argument(
            "--vars1", "-v1", type=list_of_strings,
            help=("""Variables (between " ") to keep from first plotfile"""))
    parser.add_argument(
        "--vars2", "-v2", type=list_of_strings,
        help=("""Variables (between " ") to keep from second plotfile"""))
    parser.add_argument(
            "--serial", "-s", action='store_true',
            help="Flag to disable multiprocessing")
    

    args = parser.parse_args()
    """
    Input arguments sanity check
    """
    if args.plotfile1 is None or args.plotfile2 is None:
        raise ValueError("Must specify two plotfiles to filter")

    # Combining the plotfiles
    parse_inputs(path1=args.plotfile1,
            path2=args.plotfile2,
            pltout=args.output,
            vars1=args.vars1,
            vars2=args.vars2,
            serial=args.serial,)

if __name__ == "__main__":
    main()
