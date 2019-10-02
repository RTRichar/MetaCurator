#!/usr/bin/env python

import argparse
import sys

parser = argparse.ArgumentParser("TaxFastaConsensus identifies and removes sequences which don't have taxonomic lineages and lineages which don't have corresponding sequences")
parser.add_argument('-it', '--InTax', required = True, help = "\nInput taxnomic lineages (tab-delimited)\n")
parser.add_argument('-if', '--InFasta', required = True, help = "\nInput sequences in fasta format\n")
parser.add_argument('-ot', '--OutTax', required = True, help = "\nFilename for output taxonomic lineages\n")
parser.add_argument('-of', '--OutFasta', required = True, help = "\nFilename for output fasta formatted sequences\n")
args = parser.parse_args()

InTax = {}
with open(args.InTax, 'r') as InputTax:
	for line in InputTax:
		InTax[line.strip().split('\t')[0]] = line.strip().split('\t')[1]

InFasta = {}
with open(args.InFasta, 'r') as InputFasta:
	for line in InputFasta:
		if not line.strip():
			continue
		if line.startswith('>'):
			if str(line.strip())[1:] not in InFasta:
				header = str(line.strip())[1:]
				continue
			else:
				sys.stderr.write('\n# WARNING: TaxFastCons: duplicate sequence header skipped - ' + str(line.strip())[1:])
		InFasta[header] = line.strip()

OutTax = {}
for key in InTax:
	if key in InFasta:
		OutTax[key] = InTax[key]

OutFasta = {}
for key in InFasta:
	if key in InTax:
		OutFasta[key] = InFasta[key]

with open(args.OutTax, 'w') as OutputTax:
	for key in OutTax:
		OutputTax.write(key + '\t' + OutTax[key] + '\n')

with open(args.OutFasta, 'w') as OutputFasta:
	for key in OutFasta:
		OutputFasta.write('>' + key + '\n' + OutFasta[key] + '\n')
