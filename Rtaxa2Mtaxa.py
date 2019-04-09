#!/usr/bin/env python

import sys
import subprocess
import argparse
import time

parser = argparse.ArgumentParser("Rtaxa2Metaxa takes the output of the R module, Taxonomizr, and reformats the taxonomy information to conform to the expectations of the Metaxa2 classifier (Bengtsson-Palme et al. 2015)")
# required
parser.add_argument('-i', '--InputFile', required = True, help = "\nFile containing R taxonomizr output\n")
parser.add_argument('-o', '--OutputFile', required = True, help = "\nOutput filename for lineages cleaned and reformated for Metaxa2\n")
args = parser.parse_args()

LinDct = {}
with open(args.InputFile, 'r') as InFile:
	for line in InFile:
		LinDct[line.strip().replace('"','').split(',')[1]] = line.strip().replace('"','').split(',')[3:]

with open(args.OutputFile, 'w') as OutFile:
	for key in LinDct:
		L = str('k__' + LinDct[key][0] + ';p__' + LinDct[key][1] + ';c__' + LinDct[key][2] + ';o__' + LinDct[key][3] + \
			';f__' + LinDct[key][4] + ';g__' + LinDct[key][5] + ';s__' + LinDct[key][6])
		OutFile.write(str(key) + '\t' + L + '\n')
