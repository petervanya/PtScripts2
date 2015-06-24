#!/usr/bin/env python
"""Usage:
    extract.py <dir> <cluster> [--save]

New version of parse.py script

Arguments:
    <dir>      Directory with output files
    <cluster>  Pt cluster, e.g. 9_10_9

Options:
    --save     Save into a summary file

pv278@cam.ac.uk, 23/06/15
"""
from docopt import docopt
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame

def summary_plain(inpath):
    pass

def summary_opt(base_dir, cluster, spins, cols):
    """Create summarising table for a given Pt cluster and spin
       by taking file path as argument"""
    A = DataFrame(index=spins, columns=cols)

    for i in spins:
        infile = "run_S" + str(i) + ".out"
        inpath = os.path.join(base_dir, "Pt" + cluster, infile)
        try:
            fin = open(inpath, "r").readlines()
        except IOError:
            print "Error: no output file for", cluster, " S =",i
            continue

        if "Normal" in fin[-1]:
            A.ix[i, "succ"] = "YES"
            A.ix[i, "E"] = ([l for l in fin if "SCF Done" in l][-1].split()[4])
        else:
            A.ix[i, "succ"] = "NO"
            err_word = fin[-4].split()[0]
            if err_word == "Convergence":
                A.ix[i, "reason"] = "Conv fail"
            elif err_word == "Error":
                A.ix[i, "reason"] = "Out of steps"
            else:
                A.ix[i, "reason"] = "Unknown"
                
        regex = re.compile("Step number\s+[0-9]+ out of a maximum of\s+[0-9]+")
        match = re.findall(regex, " ".join(fin))
        if match:
            A.ix[i, "steps"] = match[-1].split()[2]
            A.ix[i, "maxsteps"] = match[-1].split()[-1]
 
        temp = [l for l in fin if " Job cpu" in l][-1].split()
        A.ix[i, "runtime"] = temp[3]+":"+temp[5]+":"+temp[7]+":"+temp[9]
        
        temp = [l for l in fin if "termination" in l][-1].split()
        A.ix[i, "datetime"] = temp[-4]+" "+temp[-3]+" "+temp[-1][0:-1]
    
    return A


if __name__ == "__main__":
    args = docopt(__doc__, version=1.0)
#    print args
    pd.set_option('display.width', 100)

    base_dir = os.path.abspath(os.path.join(os.getcwd(), "..", args["<dir>"]))
    cols = ["succ", "reason", "E", "steps", "maxsteps", "runtime", "datetime"]
    cluster = args["<cluster>"]
    spins = range(11)

    A = summary_opt(base_dir, cluster, spins, cols)

    if args["--save"]:
        outfile = "Pt" + cluster + "_opt_summary.csv"
        outpath = os.path.join(base_dir, "Outfiles", outfile)
        A.to_csv(outpath, sep="\t")
        print "Table saved in", outpath
    else:
        print A





