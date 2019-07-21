#!/bin/bash

export ES_URL=http://127.0.0.1:9200
#curl -f $ES_URL/nameresults
#if [ ! $? -eq 0 ]; then
#  curl -H "Content-type: application/json" -XPUT $ES_URL/nameresults -d@elasticsearch-templates/nameresults.json
#fi

#curl -f $ES_URL/namedatabase
#if [ ! $? -eq 0 ]; then
#  curl -H "Content-type: application/json" -XPUT $ES_URL/namedatabase -d@elasticsearch-templates/namedatabase.json
#fi
#curl -f $ES_URL/nameresults
#if [ ! $? -eq 0 ]; then
#  curl -H "Content-type: application/json" -XPUT $ES_URL/nameresults -d@elasticsearch-templates/nameresults.json
#fi
FLASK_APP=babynamesweb.py flask  run --host=0.0.0.0
