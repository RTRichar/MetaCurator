#!/usr/bin/env python

#--$ python GetOhioSeqs.py -l OhioSpecies.txt -if rbcL_Final.fasta -it rbcL_Final.tax -of rbcL_Ohio.fasta -ot rbcL_Ohio.tax

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--List', required = True, help = "\nInput list of species present in your study region\n")
parser.add_argument('-if', '--InFasta', required = True, help = "\nInput fasta file of globally available references sequences\n")
parser.add_argument('-it', '--InTax', required = True, help = "\nInput taxonomy file of globally available references sequences\n")
parser.add_argument('-of', '--OutFasta', required = True, help = "\nOutbput fasta file of sequences belonging to species present in your provided species list\n")
parser.add_argument('-ot', '--OutTax', required = True, help = "\nOutput taxonomy file of lineages belonging to species present in your provided species list\n")
parser.add_argument('--genus', default=False, type=lambda x: (str(x).lower() == 'true'), help = "\nDesignate 'True' if you wish to obtain sequences from genera present in the study system. The default, 'False' yiels only the sequences from species present in the study system. Since species classifications are often quite error-prone in the first place, this provides the opportunity to constrain the database at the genus level, resulting in a more complete set of reference sequences.\n")
#parser.add_argument('--genus', default=False, type=lambda x: (str(x).lower() == 'true'))
args = parser.parse_args()

USDA_LST = []
if bool(args.genus) == False:
	print "\nanalyzing at Species\n"
	with open(args.List, 'r') as USDA:
               for line in USDA:
                       USDA_LST.append(line.strip())
else:
	print "\nanalyzing at Genus\n"
	with open(args.List, 'r') as USDA:
		for line in USDA:
			line = line.split(' ')[0]
			USDA_LST.append(line.strip())

InputFasta = {}
with open(args.InFasta, 'r') as Fasta:
        for line in Fasta:
                if not line.strip():
                        continue
                if line.startswith('>'):
                        if str(line.strip())[1:] not in InputFasta:
                                header = str(line.strip())[1:]
                                continue
                        else:
                                sys.stderr.write('\n# WARNING: GetSeqsByRegion: duplicate sequence header skipped - ' + str(line.strip())[1:])
                InputFasta[header] = line.strip()

InTax = {}
with open(args.InTax, 'r') as Tax:
	for line in Tax:
		InTax[line.split('\t')[0]] = line.split('\t')[1].strip()

OutFasta = {}
OutTax = {}
if bool(args.genus) == False:
	for key in InputFasta:
		if len(InTax[key].strip().split(';')) >= 7:
			sp = str(InTax[key].split(';')[6])[3:]
			if sp in USDA_LST:
				OutFasta[key] = InputFasta[key]
				OutTax[key] = InTax[key]
else:
	for key in InputFasta:
		if len(InTax[key].strip().split(';')) >= 7:
			g = str(InTax[key].split(';')[5])[3:]
			if g in USDA_LST:
				OutFasta[key] = InputFasta[key]
				OutTax[key] = InTax[key]

with open(args.OutFasta, 'w') as OutFile:
	for key,value in OutFasta.items():
		OutFile.write('>' + str(key) + '\n' + value + '\n')

with open(args.OutTax, 'w') as OutFile:
        for key,value in OutTax.items():
                OutFile.write(str(key) + '\t' + value + '\n')

