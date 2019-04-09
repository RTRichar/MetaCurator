#!/usr/bin/env python

import subprocess
import argparse
import sys
import time

parser = argparse.ArgumentParser(description="DerepByTaxonomy -- Dereplication by Taxonomy -- This tool is used for removing sequence duplicates from reference sequence libraries used in metagenomic and metabarcoding studies. Since some barcode markers, such as plant rbcL, exhibit extremely low sequence divergence, it is important to check that two identical reference sequences belong to the same species prior to deleting one of them. Thus, DerepByTaxonomy uses an iterative vsearch alignment-based approach to dereplication while checking the taxonomic lineage of each sequence before removing one. If the lineages of a match are different, it removes a sequence duplicate from an exact sequence match as well as the shorted duplicate from exact matches for which a short sequence is contained within a long sequence.")
parser.add_argument('-i', '--InputFile', required = True, help = "\nFasta of sequences trimmed to exact region of interest\n")
parser.add_argument('-t', '--TaxFile', required = True, help = "\nTaxonomic lineages for input reference sequences. Lineages should all be formatted in the same way and the lineage should be tab-separated from the header\n")
parser.add_argument('-o', '--OutputFile', required=True, help = "\nName of output file to be produced\n")
parser.add_argument('-mh', '--MaxHits', required=False, default=1000, help = "\nMax hits to find before ending search for any given query (default: 1000)\n")
parser.add_argument('-p', '--Threads', default=1, required=False, help = "\nNumber of processors (default: 1)\n")
parser.add_argument('-it', '--Iterations', default=10, required=False, help = "\nNumber of iterative searches to run (default: 10). This is important in case the number of replicates exceeds '--MaxHits'\n")
parser.add_argument('--SaveTemp', default=False, type=lambda x: (str(x).lower() == 'true'), help = "\nOption for saving alignments and intermediate files produced during dereplication\n")
args = parser.parse_args()
# set temp working directory
TEMPDIR = str('Derep_tmp_' + '_'.join(time.ctime(time.time()).replace(':','_').split()[1:]))
subprocess.call(['mkdir', TEMPDIR])
# copy input file into output file name
DeltaInputOld = str(TEMPDIR + '/tmp_DeltaInput_-1')
subprocess.call(['cp', args.InputFile, DeltaInputOld])
# read fasta file into dictionary
FastaDct = {}
with open(args.InputFile, 'r') as Fasta:
	for line in Fasta:
		if not line.strip():
			continue
		if line.startswith('>'):
			if str(line.strip())[1:] not in FastaDct:
				header = str(line.strip())[1:]
				continue
			else:
				sys.stderr.write('\n# WARNING: DerepByTax: duplicate sequence header skipped - ' + str(line.strip())[1:])
		FastaDct[header] = line.strip()
# read tax file into dictionary
TaxDct = {}
with open(args.TaxFile, 'r') as TaxFile:
	for line in TaxFile:
		TaxDct[line.strip().split('\t')[0]] = line.strip().split('\t')[1]
DupLst = [] # make list to keep track of duplicates
DupTDct = {}
SumDct = {} # make dictionary to keep track of duplicates removed per round
################################################################################################
# iteratively run alignment, add hits to DupLst, delete old DeltaDct, make new DeltaDct while excluding new and old duplicate hits, write DeltaDct to file
for i in range(0,int(args.Iterations)):
	sys.stderr.write('\n### ' + time.ctime(time.time()) + ' Starting round ' + str(i) + ' ###\n\n') # iter init timestamp
	DeltaDct = {}
	PreLength = len(DupLst)
	DeltaInputOld = str(TEMPDIR + '/tmp_DeltaInput_' + str((int(i) - 1)))
	DeltaInputNew = str(TEMPDIR + '/tmp_DeltaInput_' + str(i))
	AlnOutPut = str(TEMPDIR + '/tmp_AlnOutput_' +  str(i))
	TxtAlnOutPut = str(TEMPDIR + '/tmp_TxtAlnOutput_' +  str(i))
	subprocess.call(['vsearch', '--usearch_global', str(DeltaInputOld), '-db', str(DeltaInputOld), '--blast6out', str(AlnOutPut), '--self', \
	'--maxaccepts', str(args.MaxHits), '--id', '1', '--gapopen', '*I/0E', '--query_cov', '1', '--threads', str(args.Threads), \
	'--alnout', str(TxtAlnOutPut)])
	TList = []
	with open(AlnOutPut, 'r') as Results:
		for line in Results:
			Q = line.split('\t')[0]
			T = line.split('\t')[1]
			if TaxDct[Q] == TaxDct[T]: # if seqs are duplicates and taxonomies are the same, add Q to DupLst
				if Q not in DupLst:
					if Q not in TList:
						DupLst.append(Q)
						DupTDct[Q] = T
						TList.append(T)
	with open(DeltaInputNew, 'w') as DeltaFasta:
		for key in FastaDct:
			if key not in DupLst: # if key doesn't represent duplicate, add to the DeltaFasta
				DeltaFasta.write('>' + str(key) + '\n' + FastaDct[key] + '\n')
	PostLength = len(DupLst)
	SumDct[('Iteration_' + str(i))] = (int(PostLength) - int(PreLength))
	sys.stderr.write('\n### ' + time.ctime(time.time()) + ' ' + str(int(PostLength) - int(PreLength)) + ' Sequences removed' + ' ###\n\n')
	if (int(PostLength) - int(PreLength)) == 0:
		IterBreak = i
		break
	if i == int(args.Iterations):
		IterBreak = int(args.Iterations)
################################################################################################
# report findings to standard out
for key, value in sorted(SumDct.items()):
	sys.stderr.write(key + '\t' + str(value) + '\n')
sys.stderr.write('>>> Total Seqs Removed: ' + str(sum(SumDct.values())) + '\n\n')
# copy findings to final outfile
subprocess.call(['cp', DeltaInputNew, args.OutputFile]) 
# clean up temp directory
if bool(args.SaveTemp) == False:
	subprocess.call(['rm','-rf',TEMPDIR])
else:
	DupsRemoved = str(TEMPDIR + '/DupsRemoved.txt')
	with open(DupsRemoved, 'w') as CheckFile:
		for key in DupTDct:
			CheckFile.write(str(key) + '_Q\t' + TaxDct[key] + '\n' + FastaDct[key] + '\n' + \
			DupTDct[key] + '_T\t' + TaxDct[DupTDct[key]] + '\n' + FastaDct[DupTDct[key]] + '\n')
		
