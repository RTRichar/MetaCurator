#!/bin/bash

args=("$@")
# Input taxonomies fullname: ${args[$i]}

OutBase=`echo ${args[$i]} | cut -d'.' -f1`

mkdir Bash_TempDir

cat ${args[$i]} | perl -pe 's/;s__[A-Za-z]+\ssp\..*$//' | perl -pe 's/;s__[A-Za-z]+\saff\.\s.*$//' | perl -pe 's/;s__[A-Za-z]+\sgen\.\s.*$//' | perl -pe 's/;s__[A-Za-z]+\scf\.\s.*$//' | perl -pe 's/;s__[A-Za-z]+\s[a-z]+\svar\.\s.*$//' > ./Bash_TempDir/taxonomies_0.tax

cat ./Bash_TempDir/taxonomies_0.tax | perl -pe 's/;s__NA$//' | perl -pe 's/;g__NA$//' | perl -pe 's/;f__NA$//' | perl -pe 's/;o__NA$//' | perl -pe 's/;c__NA$//' | perl -pe 's/;p__NA$//' | sed '/k__NA$/d' > ./Bash_TempDir/taxonomies_1.tax

cat ./Bash_TempDir/taxonomies_1.tax | perl -pe 's/(s__[A-Za-z]+\sx\s[A-Za-z]+).*/$1/' | perl -pe 's/(s__[A-Za-z]+\s[a-z]+\sx\s[A-Za-z]+).*/$1/' > ./Bash_TempDir/taxonomies_2.tax

cat ./Bash_TempDir/taxonomies_2.tax | perl -pe 's/s__x\s.*//' | sed '/environmental\s/d' | sed '/s__uncultured\s/d' | sed '/s__chlorobiont\s/d' | perl -pe 's/s__[A-Za-z]+\shybrid\scultivar;//' | perl -pe 's/s__\(.*//' |  perl -pe 's/;$s__;/;/' > ./Bash_TempDir/taxonomies_3.tax

cp ././Bash_TempDir/taxonomies_3.tax ${OutBase}_clean.tax

rm -rf ./Bash_TempDir
