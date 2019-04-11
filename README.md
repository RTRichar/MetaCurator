# CurateDB
### Software for curating reference sequence databases used in barcoding, metabarcoding and metagenetics
CurateDB uses HMMER (http://hmmer.org/) and VSEARCH (https://github.com/torognes/vsearch) to search through sequences available from broad origions (such as NCBI Nucleotide, NCBI Genome and/or BOLD), identify and extract the precise barcode marker region of interest, discard irrelevent sequences, and dereplicate the resulting reference data in a taxonimcaly-supervized fashion.
### Dependencies  
CurateDB is a command-line only toolkit which runs on typical Unix/Linux environments. It requires the following software to be installed and globally accesible. 

Python 2.7.5 or greater  
Perl 5.16.0 or compatible  
VSEARCH 2.8.1 or compatible  
HMMER3 3.1b2 or compatible  
MAFFT 7.270 or compatible  
