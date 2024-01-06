#!/bin/bash
PYTHONVER=python3.11
#cp -rpv *.py  $HOME/.coursetools/
rm -f /opt/conda/lib/${PYTHONVER}/site-packages/casstools
ln -sf $PWD /opt/conda/lib/${PYTHONVER}/site-packages/casstools
