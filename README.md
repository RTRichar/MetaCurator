# MetaCurator
### Software for curating reference sequence databases used in barcoding, metabarcoding and metagenomics
MetaCurator uses HMMER (http://hmmer.org/), MAFFT (https://mafft.cbrc.jp/alignment/software/linux.html) and VSEARCH (https://github.com/torognes/vsearch) to search through sequences available from broad origions (such as NCBI Nucleotide, NCBI Genome and/or BOLD), identify and extract the precise barcode marker region of interest, discard irrelevent sequences and sequence regions, and dereplicate the resulting reference data in a taxonomically-supervised fashion.

The goal of MetaCurator is to create a flexible and generalizable alternative to the CRUX module of ANACAPA (https://github.com/limey-bean/Anacapa/) and the conserved marker curation mode of Metaxa2_dbb (https://doi.org/10.1093/bioinformatics/bty482).
 
### Dependencies  
MetaCurator is a command-line only toolkit which runs on typical Unix/Linux environments. It requires the following software to be installed and globally accessible. 

Python 2.7.5 or greater  
Perl 5.16.0 or compatible  
VSEARCH 2.8.1 or compatible  
HMMER3 3.1b2 or compatible  
MAFFT 7.270 or compatible  

### Installation
Download and unpack tarfile of current release
```
wget https://github.com/RTRichar/MetaCurator/archive/MetaCurator_vX.Y.Z.tar.gz
tar xzf MetaCurator_vX.Y.Z.tar.gz   # replace 'X.Y.Z' with current release numbers
```
After unpacking, export the MetaCurator directory to $PATH if you're using a local machine, or add the directory path to the appropriate login configuration file if you are using a remote cluster

### Test MetaCurator Installation
An example dataset of 10,000 sequences annotated as *rbcL* in NCBI Nucleotide is provided along with a Taxonomizr formated taxonomy file and a set of 8 hand-picked *rbcL* sequences manually trimmed to be representative of a commonly used barcoding region. Running the software on this test set should take approximately one hour on a typical single core machine with 4 GB of RAM.  
```
cd MetaCurator-1.0beta.1/TestMetaCurator
MetaCurator.py -r rbcL_Reps.fa -i rbcL_sample.fa -it rbcL_sample.tax -tf True -ct True -of Test.fa -ot Test.tax --SaveTemp True 2> rbcL_log.txt
```

### Citation and further information
Richardson, RT, DB Sponsler, H McMinn-Sauder & RM Johnson. (2019). MetaCurator: A hidden Markov model-based toolkit for extracting and curating sequences from taxonomically-informative genetic markers. *Methods in Ecology and Evolution*. https://doi.org/10.1111/2041-210X.13314

**Contact: rtr87@yorku.ca**
