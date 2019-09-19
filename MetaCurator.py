#!/usr/bin/env python

import subprocess, argparse, sys, time

parser = argparse.ArgumentParser(description="")
# required
required = parser.add_argument_group('required arguments')
optional = parser.add_argument_group('universal optional arguments')
Ioptional = parser.add_argument_group('IterRazor optional arguments')
Doptional = parser.add_argument_group('DerepByTaxonomy-specific optional arguments')
required.add_argument('-r', '--ReferencesFile', required = True, help = "\nFasta file of sequences trimmed to exact region of interest (header format should conform to inputfile header format). This should be approximately 10 sequences spanning a diversity of the phylogenetic tree of interest, so as to build an appropriately inclusive HMM from the first iteration.\n")
required.add_argument('-i', '--InputFile', required = True, help = "\n Input file of reference sequences to be extracted (sequence headers should include a unique sequence identifier, NCBI accessions are recomended, preceded only by '>')\n")
required.add_argument('-it', '--InTax', required = True, help = "\nInput taxonomic lineages (a tab-delimited file with the first column containing unique sequence identifiers compatible with the files provided under '-r' and '-i'). Normally, this would be in Metaxa2-compatible format, however, if lineages come directly from Taxonomizr, you can skip reformatting and declare '-tf True.' See below for more details.\n")
required.add_argument('-ot', '--OutTax', required = True, help = "\nFilename for output taxonomic lineages\n")
required.add_argument('-of', '--OutFasta', required = True, help = "\nFilename for output fasta formatted sequences\n")
# optional universal
optional.add_argument('-t', '--threads', required = False, default = 1, help = "\n Number of processors to use\n")
optional.add_argument('--SaveTemp', default=False, type=lambda x: (str(x).lower() == 'true'), help = "\nOption for saving alignments and HMM files produced during extraction and dereplication (True or False)\n")
# optional Iterazor-specific
Ioptional.add_argument('-e', '--HmmEvalue', required = False, default = 0.05, help = "\nEvalue threshold for HMM search\n")
optional.add_argument('-tf', '--TaxonomizrFormat', required = False, type=bool, default = False, help = "\nSpecify if tax lineages are in Taxonomizr format and must first be converted to Metaxa2-compatible tab-delimited format (True or False)\n")
optional.add_argument('-ct', '--CleanTax', required = False, type=bool, default = False, help = "\nSpecify if tax lineages are to be cleaned of common NCBI artifacts and revised at unresolved midpoints (True or False)\n")
Ioptional.add_argument('-is', '--IterationSeries', required = False, default = '20,10,5,5', help = "\nThe IterationSeries and CoverageSeries arguments dictate the number of iterative searches to run and the minimum HMM coverege required for each round of extracting. This argument consists of a comma-separated list specifying the number of searches to run during each round of extraction. The list can vary in length, changing the total number of extraction rounds conducted. However, if a search iteration fails to yield any new reference sequence amplicons, IterRazor will break out of that round of searching and move to the next. By default, the software conducts four rounds of extraction with 20, 10, 5 and 5 search iterations per round (i.e. '-is 20,10,5,5').\n")
Ioptional.add_argument('-cs', '--CoverageSeries', required = False, default = '1.0,0.95,0.9,0.65', help = "\nThis argument consists of a comma-separated list specifying the minimum HMM coverage required per round for an extracted amplicon reference sequence to be added to the reference sequence fasta. The list can vary in length but must be equal in length to the IterationSeries list. By default, the software conducts four rounds of extraction with coverage limits of 1.0, 0.95, 0.9 and 0.65 for each respective search round (i.e. '-cs 1.0,0.95,0.9,0.65').\n")
# optional DerepByTaxonomy-specific
Doptional.add_argument('-mh', '--MaxHits', required=False, default=1000, help = "\nMax hits to find before ending search for any given query using VSEARCH (default: 1000)\n")
Doptional.add_argument('-di', '--Iterations', default='10', required=False, help = "\nNumber of iterative VSEARCH searches to run (default: 10). This is important in case the number of replicates for a given sequence greatly exceeds '--MaxHits'\n")
args = parser.parse_args()

### Test input fasta
n = int(0)
with open(str(args.InputFile), 'r') as Fasta:
	for line in Fasta.readlines()[:3]:
		if not line.strip():
			sys.stderr.write('\n### Fasta contains empty line. Reformate fasta.\n')
			sys.exit()
		if not line.startswith('>'):
			n += 1
if n == int(2):
	sys.stderr.write('\n### Check fasta, it appears sequences are not continuous. Remove next line instances.\n')
	sys.exit()

### test -is and -cs length
if len(args.IterationSeries.split(',')) != len(args.CoverageSeries.split(',')):
	sys.stderr.write('\n\n### -is and -cs lists are of unequal length. Please correct!\n\n')
	sys.exit()

### create temp directory
CTEMPDIR = str('curate_tmp_' + '_'.join(time.ctime(time.time()).replace(':','_').split()[1:]))
subprocess.call(['mkdir', CTEMPDIR])
### if tax lineages are straight from NCBI-compatible taxonomizr, or if additional curation features on, or if both
subprocess.call(['cp', str(args.InTax), str(CTEMPDIR + '/StartTax.tax')])  
if args.CleanTax == True and args.TaxonomizrFormat == True:
	sys.stderr.write('\n### ' + time.ctime(time.time()) + ': TAXONOMIZR formated lineages specified: Cleaning lineages and revising unresolved mid-points ###\n')
	subprocess.call(['Rtaxa2Mtaxa.py', '-i', str(CTEMPDIR + '/StartTax.tax'), '-o', str(CTEMPDIR + '/MtxaFrm.tax')])
	subprocess.call(['CleanTax.sh', str(CTEMPDIR + '/MtxaFrm.tax')])
	subprocess.call(['ReviseIntNAs.py', '-i', str(CTEMPDIR + '/MtxaFrm_clean.tax'), '-o', str(CTEMPDIR + '/CleanInTax.tax')])
elif args.CleanTax == True:
	sys.stderr.write('\n### ' + time.ctime(time.time()) + ': METAXA2 Formated lineages specified: Cleaning lineages and revising unresolved mid-points ###\n')
	subprocess.call(['CleanTax.sh', str(CTEMPDIR + '/StartTax.tax')])
	subprocess.call(['ReviseIntNAs.py', '-i', str(CTEMPDIR + '/StartTax_clean.tax'), '-o', str(CTEMPDIR + '/CleanInTax.tax')])
elif args.TaxonomizrFormat == True:
	sys.stderr.write('\n### ' + time.ctime(time.time()) + ': TAXONOMIZR formated lineages specified: Not cleaning lineages or revisising unresolved mid-points ###\n')
	subprocess.call(['Rtaxa2Mtaxa.py', '-i', str(CTEMPDIR + '/StartTax.tax'), '-o', str(CTEMPDIR + '/CleanInTax.tax')])
else:
	sys.stderr.write('\n### ' + time.ctime(time.time()) + ': Default processing mode: Proceeding to IterRazor ###\n')
	subprocess.call(['cp', str(args.InTax), str(CTEMPDIR + '/CleanInTax.tax')])
### run IterRazor
sys.stderr.write('\n### ' + time.ctime(time.time()) + ': Extracting amplicon region of interest from input reference sequences ###\n')
with open(str(CTEMPDIR + '/HmmerLog.txt'),'w') as HmmLog:
	if bool(args.SaveTemp) == False:
		subprocess.call(['IterRazor.py', '-r', str(args.ReferencesFile), '-i', str(args.InputFile), '-o', str(CTEMPDIR + '/IterOut.fa'), '-t', \
			str(args.threads), '-e', str(args.HmmEvalue), '-is', str(args.IterationSeries), '-cs', str(args.CoverageSeries)], stdout=HmmLog)
	else:
		subprocess.call(['IterRazor.py', '-r', str(args.ReferencesFile), '-i', str(args.InputFile), '-o', str(CTEMPDIR + '/IterOut.fa'), '-t', \
			str(args.threads), '-e', str(args.HmmEvalue), '-is', str(args.IterationSeries), '-cs', str(args.CoverageSeries), '--SaveTemp', \
			'True'], stdout=HmmLog)
# get consensus
sys.stderr.write('\n### ' + time.ctime(time.time()) + ': Getting taxonomy and fasta consensus entries from IterRazor output ###\n')
subprocess.call(['TaxFastaConsensus.py', '-it', str(CTEMPDIR + '/CleanInTax.tax'), '-if', str(CTEMPDIR + '/IterOut.fa'), '-ot', \
	str(CTEMPDIR + '/ConTaxOne.tax'), '-of', str(CTEMPDIR + '/ConFastaOne.fa')])
### run DerepByTaxonomy
sys.stderr.write('\n\n### ' + time.ctime(time.time()) + ': Dereplicating extracted reference sequences using DerepByTaxonomy ###\n\n')
if str(args.SaveTemp) == 'False':
	subprocess.call(['DerepByTaxonomy.py', '-i', str(CTEMPDIR + '/ConFastaOne.fa'), '-t', str(CTEMPDIR + '/ConTaxOne.tax'), '-o', \
	str(CTEMPDIR + '/DerepOut.fa'), '-p', str(args.threads), '-mh', str(args.MaxHits), '-it', str(args.Iterations)]) # add threads and iterations flags
else:
	subprocess.call(['DerepByTaxonomy.py', '-i', str(CTEMPDIR + '/ConFastaOne.fa'), '-t', str(CTEMPDIR + '/ConTaxOne.tax'), '-o', \
	str(CTEMPDIR + '/DerepOut.fa'), '-p', str(args.threads), '-mh', str(args.MaxHits), '-it', str(args.Iterations), '--SaveTemp', 'True'])
# get consensus
sys.stderr.write('\n### ' + time.ctime(time.time()) + ': Getting taxonomy and fasta consensus entries from DerepByTaxonomy output ###\n')
subprocess.call(['TaxFastaConsensus.py', '-it', str(CTEMPDIR + '/CleanInTax.tax'), '-if', str(CTEMPDIR + '/DerepOut.fa'), '-ot', str(args.OutTax), \
	'-of', str(args.OutFasta)])
# calc stats
subprocess.call(['CalcStats.py','--Before',str(CTEMPDIR + '/CleanInTax.tax'),'--After',str(args.OutTax),'--AfterFasta',str(args.OutFasta)])
# remove temps 
if bool(args.SaveTemp) == False:
	subprocess.call(['rm', '-rf', str(CTEMPDIR)]) 
