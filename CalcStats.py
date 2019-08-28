#!/usr/bin/env python

#--$ python CalcStats.py --Before Before.tax --After After.tax 

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-bf', '--Before', required = True, help = "\nBefore\n")
parser.add_argument('-af', '--After', required = True, help = "\nAfter\n")
args = parser.parse_args()

Ranks = ['Kingdom','Phylum','Class','Order','Family','Genus','Species']
RankLsts = []
for i in range(len(Ranks)): # need to create list of lists to hold taxon names
	i = []
	RankLsts.append(i)
BeforeCount = []
AfterCount = []

# before
with open(args.Before, 'r') as BeforeTax:
	for line in BeforeTax:
		line = line.strip().split('\t')[1].split(';')
		line = list(filter(None, line))
		for i in range(len(Ranks)):
			if len(line) >= int(i+1):
				if line[i] not in RankLsts[i]:
					RankLsts[i].append(line[i])
for i in range(len(Ranks)):
	count = len(RankLsts[i])
	BeforeCount.append(count)

# after
RankLsts = [] # clear RankLsts
for i in range(len(Ranks)): # need to create list of lists to hold taxon names
        i = []
        RankLsts.append(i)

with open(args.After, 'r') as AfterTax:
        for line in AfterTax:
                line = line.strip().split('\t')[1].split(';')
                line = list(filter(None, line))
                for i in range(len(Ranks)):
                        if len(line) >= int(i+1):
                                if line[i] not in RankLsts[i]:
                                        RankLsts[i].append(line[i])
for i in range(len(Ranks)):
        count = len(RankLsts[i])
        AfterCount.append(count)

# Calculate difference and write to std out
sys.stderr.write(','.join(['Rank','Taxa Input','Taxa Curated','ProportionCurated','\n']))
for i in range(len(Ranks)):
	sys.stderr.write(str(Ranks[i]+','+str(BeforeCount[i])+','+str(AfterCount[i])+','+str(float(AfterCount[i])/BeforeCount[i])+'\n'))
