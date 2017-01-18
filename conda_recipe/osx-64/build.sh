#!/bin/bash

cd $RECIPE_DIR
cd ../..
python $RECIPE_DIR/build_messenger.py $RECIPE_DIR/local.cfg
python setup.py install build-conda

