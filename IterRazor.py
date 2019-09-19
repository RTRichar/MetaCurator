#!/usr/bin/env python

import sys
import subprocess
import argparse
import time

parser = argparse.ArgumentParser("IterRazor is a tool which uses hidden Markov models to identify and extract precise DNA barcode sequences of interest from the full diversity of reference sequence data available through sources such as NCBI (e.g. whole genome sequences, whole chloroplast sequences or Sanger seuqnces representative of variable portions of the locus of interest)")
# required
parser.add_argument('-r', '--ReferencesFile', required = True, help = "\nFasta file of sequences trimmed to exact region of interest (header format should conform to --InputFile header format). This should be 5 to 10 sequences spanning a diversity of the phylogenetic tree of interest, so as to build a relatively broadly inclusive HMM from the first iteration (REQUIRED)\n")
parser.add_argument('-i', '--InputFile', required = True, help = "\nInput file of reference sequences to be extracted (e.g. whole chloroplast genome sequences from NCBI). Sequence headers should include a unique sequence identifier, NCBI accessions are recomended, preceded only by '>' (REQUIRED)\n")
parser.add_argument('-o', '--OutPutFile', required = True, help = "\n Output file for extracted sequences (REQUIRED)\n")
# optional
parser.add_argument('-t', '--threads', required = False, default = 1, help = "\n Number of processors to use\n")
parser.add_argument('--SaveTemp', default=False, type=lambda x: (str(x).lower() == 'true'), help = "\nOption for saving alignments and HMM files produced during extraction\n")
parser.add_argument('-e', '--HmmEvalue', required = False, default = 0.05, help = "\nEvalue threshold for hmm search\n")
parser.add_argument('-is', '--IterationSeries', required = False, default = '20,10,5,5,3', help = "\nThe IterationSeries and CoverageSeries arguments dictate the number of iterative searches to run and the minimum HMM coverege required for each round of extracting. This argument consists of a comma-separated list specifying the number of searches to run during each round of extraction. The list can vary in length, changing the total number of extraction rounds conducted. However, if a search iteration fails to yield any new reference sequence amplicons, IterRazor will break out of that round of searching and move to the next. By default, the software conducts four rounds of extraction with 20, 10, 5 and 5 search iterations per round (-is 20,10,5,5).\n")
parser.add_argument('-cs', '--CoverageSeries', required = False, default = '1.0,0.98,0.95,0.9,0.85', help = "\nThis argument consists of a comma-separated list specifying the minimum HMM coverage required per round for an extracted amplicon reference sequence to be added to the reference sequence fasta. The list can vary in length but must be equal in length to the IterationSeries list. By default, the software conducts four rounds of extraction with coverage limits of 1.0, 0.95, 0.9 and 0.65 for each respective search round (-cs 1.0,0.95,0.9,0.65).\n")
args = parser.parse_args()

def reverse_complement(dna):
	complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A', 'U': 'A', 'R': 'Y', 'Y': 'R', 'S': 'W', 'W': 'S', 'K': 'M', 'M': 'K', 'B': 'V', 'D': 'H', 'H': 'D', 'V': 'B', 'N': 'N'}
	return ''.join([complement[base] for base in dna[::-1]])

############################## Prep working environment ###########################################
# set temp working directory
TEMPDIR = str('IterRazor_tmp_' + '_'.join(time.ctime(time.time()).replace(':','_').split()[1:]))
subprocess.call(['mkdir', TEMPDIR])
# copy reference file to output name so output can be iteratively added to in place
subprocess.call(['cp', args.ReferencesFile, args.OutPutFile])
# make copy of input references for 
DeltaInput = str(TEMPDIR + '/tmp_DeltaInput')
subprocess.call(['cp', args.InputFile, DeltaInput])
# make dictionary of InputFile target sequences
InputFasta = {}
FastStatus = str('\n') # printed after fasta is parsed, tells user if fasta had duplicates
with open(args.InputFile, 'r') as Fasta:
	for line in Fasta:
		if not line.strip():
			continue
		if line.startswith('>'):
			if str(line.strip())[1:] not in InputFasta:
				header = str(line.strip())[1:]
				continue
			else:
				FastStatus = str('\n# WARNING: IterRazor: duplicate sequence headers skipped')
		InputFasta[header] = line.strip()
sys.stderr.write(FastStatus)
# get list of extracted Sequence IDs (append each new addition so same seq isn't added twice)
RefDbIds = []
with open(args.ReferencesFile) as Refs:
	for line in Refs:
		line = line.strip()
		if not line:
			continue
		if line.startswith(">"):
			RefDbIds.append(line[1:])
# create preliminary MAFFT alignment
PreAlnOut = str(TEMPDIR + '/AlnOut_-2')
AlnOut = str(TEMPDIR + '/AlnOut_0_-1')
with open(PreAlnOut,'w') as AlnFile:
	subprocess.call(['mafft', '--quiet', '--auto', args.OutPutFile], stdout=AlnFile)
with open(AlnOut, 'w') as FinalAlnFile: #### output of mafft is lowercase, hmmbuild requires uppercase
	with open(PreAlnOut, 'r') as PreAln:
		for line in PreAln:
			if not line:
				continue
			if line.startswith(">"):
				FinalAlnFile.write(line)
				continue
			FinalAlnFile.write(str(line).upper()) # change to uppercase 
SumDct = {} # create dictionary to hold number of seqs added per iteration

IterDct = {}
CovDct = {}
for i in range(len(args.IterationSeries.split(','))):
	IterDct[i+1] = int(args.IterationSeries.split(',')[i])
for i in range(len(args.CoverageSeries.split(','))):
	CovDct[i+1] = float(args.CoverageSeries.split(',')[i]) 
if len(args.IterationSeries.split(',')) != len(args.CoverageSeries.split(',')):
	sys.stderr.write('\n\n -is and -cs lists are of unequal length. Please try again!\n\n')
	sys.exit()

IterBreak = str(-1)
PrevIterRound = str(0) # placeholder for what round the previous iteration occured in
############################## Run 4 rounds of iterative searches using decreasing coverage requirements ###########################################
for r in range(1,(len(args.IterationSeries.split(','))+1)):
	sys.stderr.write('\n\n###### ' + time.ctime(time.time()) + ' Starting round ' + str(r) + ' ######\n')
	for i in range(0,IterDct[r]):
		sys.stderr.write('### ' + time.ctime(time.time()) + ' Running round ' + str(r) + ' extraction: iteration ' + str(i) + ' ###\n')
		PstAlnOut = str(TEMPDIR + '/AlnOut_' + str(PrevIterRound) + '_' + str(IterBreak)) # set file names and run hmm iteration
		NwAlnOut = str(TEMPDIR + '/AlnOut_' + str(r) + '_' + str(i))
		Hmm = str(TEMPDIR + '/Hmm_' + str(r) + '_' + str(i))
		HmmScan = str(TEMPDIR + '/HmmScan_' + str(r) + '_' + str(i))
		nHmmTblOut = str(TEMPDIR + '/nHmmTblOut_' + str(r) + '_' + str(i))
		nHmmOut = str(TEMPDIR + '/nHmmOut_' + str(r) + '_' + str(i))
		subprocess.call(['hmmbuild', '--cpu', str(args.threads), Hmm, PstAlnOut])
		subprocess.call(['hmmpress', Hmm])
		subprocess.call(['nhmmscan', '--cpu', str(args.threads), '-E', str(args.HmmEvalue), \
			'--tblout', nHmmTblOut, '-o', nHmmOut, Hmm, DeltaInput])
		SumDct[('iteration_' + str(r) + '_' + str(i))] = 0
		with open(nHmmTblOut, 'r') as HmmResults: # identify and trim amplicon from hits
			for line in HmmResults:
				if not line.startswith('#'):
					Q = line.split()[2]
					if Q not in RefDbIds:
						Qst = (int(line.split()[6]) - 1)
						Qend = int(line.split()[7])
						Qcov = float(int(line.split()[5])-(int(line.split()[4])-1))/float(line.split()[10])
						if Qcov >= float(CovDct[r]):
							if Qend > Qst:
								with open(args.OutPutFile, 'a') as AppendFile:
									AppendFile.write(str('>' + Q) + '\n' + InputFasta[Q][Qst:Qend] + '\n')
								RefDbIds.append(Q) # append Q to RefDbIds
								SumDct[('iteration_' + str(r) + '_' + str(i))] += 1
							else: 
								with open(args.OutPutFile, 'a') as AppendFile:
									revcomp = reverse_complement(str(InputFasta[Q][Qend:Qst])) # reverse complement
									AppendFile.write(str('>' + Q) + '\n' + revcomp + '\n')
								RefDbIds.append(Q)
								SumDct[('iteration_' + str(r) + '_' + str(i))] += 1
		subprocess.call(['rm', DeltaInput]) # rebuild DeltaInput while excluding newly extracted seqs
		with open(DeltaInput, 'w') as File:
			for key,value in InputFasta.items():
				if key not in RefDbIds:
					File.write(str('>' + key) + '\n' + value + '\n')
		subprocess.call(['hmmalign', '-o', NwAlnOut, Hmm, args.OutPutFile])
		sys.stderr.write('### ' + str(SumDct[('iteration_' + str(r) + '_' + str(i))]) \
				+ ' sequences extracted at ' + str(CovDct[r]) + ' coverage ###\n\n')
		if SumDct[('iteration_' + str(r) + '_' + str(i))] == 0: # Add in SumDict to keep track of number of seqs added (if none added, break loop)
			IterBreak = i
			PrevIterRound = r
			break
		elif i == int(IterDct[r]):
			IterBreak = int(args.Iterations)
			PrevIterRound = r
		else:
			IterBreak = i
			PrevIterRound = r

############################## Report findings and clean environment ###########################################
# print summary of findings
for key, value in sorted(SumDct.items()):
	sys.stderr.write(key + '\t' + str(value) + '\n')
sys.stderr.write('>>> Total Seqs Added: ' + str(sum(SumDct.values())) + '\n')
#Remove tmp files if --SaveTemp is False
if bool(args.SaveTemp) == False:
	subprocess.call(['rm','-rf',TEMPDIR])
