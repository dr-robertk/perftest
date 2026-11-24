# setup an external venv
python3 -m venv dune-env
. dune-env/bin/activate
pip install matplotlib mpi4py scipy numpy

# now add dune-fem and dune-fem-dg to the toolchain
cd ../repos
dune-common/bin/dunecontrol --module=dune.fem all
dune-common/bin/dunecontrol --module=dune.fem.dg all

cd dune-fem-dg/pydemo/euler
python3 testdg.py
