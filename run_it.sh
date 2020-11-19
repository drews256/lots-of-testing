#!/bin/bash

git clone https://github.com/drews256/kegmeister.git running
cd running
git log --pretty=oneline | awk '{print $1;}' > shas
input="shas"
while IFS= read -r line
do
  bash ../test.sh $line
done < "$input"
