#!/usr/bin/env python

#--$ python CalcStats.py --Before Before.tax --After After.tax 

import sys
import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-bf', '--Before', required = True, help = "\nTaxonomies prior to curation\n")
parser.add_argument('-af', '--After', required = True, help = "\nTaxonomies passing curation\n")
parser.add_argument('-aff', '--AfterFasta', required = True, help = "\nSequences passing curation\n")
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
sys.stderr.write('### Summary stats of the number of taxa and proportion of taxa before and after curation' + '\n')
sys.stderr.write(', '.join(['Rank','Taxa_Input','Taxa_Curated','Proportion_Curated','\n']))
for i in range(len(Ranks)):
	sys.stderr.write(str(Ranks[i]+','+str(BeforeCount[i])+','+str(AfterCount[i])+','+str(float(AfterCount[i])/BeforeCount[i])+'\n'))

# Calculate average sequence length and write to std out
FaLngthLst = []
with open(args.AfterFasta, 'r') as AfterFa:
	for line in AfterFa:
		if not line.strip():
			continue
		if not line.startswith('>'):
			FaLngthLst.append(len(str(line.strip())))

Bottom1st = np.percentile(FaLngthLst, 1)
Bottom5th = np.percentile(FaLngthLst, 5)
Bottom10th = np.percentile(FaLngthLst, 10)
Median = np.percentile(FaLngthLst, 50)

sys.stderr.write('\n' + '### Summary stats of database sequence length from bottom 1st percentile to median' + '\n')
sys.stderr.write('1st percentile: ' + str(Bottom1st) + '\n')
sys.stderr.write('5th percentile: ' + str(Bottom5th) + '\n')
sys.stderr.write('10th percentile: ' + str(Bottom10th) + '\n')
sys.stderr.write('Median: ' + str(Median) + '\n')
