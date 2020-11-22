#/bin/bash

set -e

DIR=`pwd`

CORENLP_DIR=~/.tmp-dep/stanford-corenlp
if [ ! -d $CORENLP_DIR ]
  then
    mkdir -p $CORENLP_DIR
fi

cd $CORENLP_DIR

if [ ! -f ./stanford-corenlp-latest.zip ]
  then
    wget http://nlp.stanford.edu/software/stanford-corenlp-latest.zip
fi

CORENLP_LATEST=stanford-corenlp-*/

if [ ! -d $CORENLP_LATEST ]
  then
    unzip ./stanford-corenlp-latest.zip
fi

cd $CORENLP_LATEST

java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
-preload tokenize,ssplit,pos,lemma,ner,parse,depparse \
-status_port 9000 -port 9000 -timeout 15000 & 

cd $DIR
python3 process.py
