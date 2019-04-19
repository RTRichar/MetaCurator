# MetaCurator
### Software for curating reference sequence databases used in barcoding, metabarcoding and metagenetics
CurateDB uses HMMER (http://hmmer.org/), MAFFT (https://mafft.cbrc.jp/alignment/software/linux.html) and VSEARCH (https://github.com/torognes/vsearch) to search through sequences available from broad origions (such as NCBI Nucleotide, NCBI Genome and/or BOLD), identify and extract the precise barcode marker region of interest, discard irrelevent sequences and sequence regions, and dereplicate the resulting reference data in a taxonimcaly-supervised fashion.
### Dependencies  
CurateDB is a command-line only toolkit which runs on typical Unix/Linux environments. It requires the following software to be installed and globally accesible. 

Python 2.7.5 or greater  
Perl 5.16.0 or compatible  
VSEARCH 2.8.1 or compatible  
HMMER3 3.1b2 or compatible  
MAFFT 7.270 or compatible  

### Installation
Download and unpack tarfile of current release
```
wget https://github.com/RTRichar/CurateDB/archive/CurateDB_v1.0beta.1.tar.gz
tar xzf CurateDB_v1.0beta.1.tar.gz
```
After unpacking, export the CurateDB directory to $PATH if you're using a local machine, or add the directory path to the appropriate login configuration file if you are using a remote cluster

### Test CurateDB Installation
An example dataset of 10,000 sequences annotated as *rbcL* in NCBI Nucleotide is provided along with a Taxonomizr formated taxonomy file and a set of 8 hand-picked *rbcL* sequences manually trimmed to be representative of a commonly used barcoding region. Running the software on this test set should take approximately one hour on a typical single core machine with 4 GB of RAM.  
```
cd CurateDB-1.0beta.1/TestCurateDB
CurateDB.py -r rbcL_Reps.fa -i rbcL_10K_sample.fa -it rbcL_10K_sample.tax -tf True -ct True -of Test_rbcL.fa -ot Test_rbcL.tax
```
