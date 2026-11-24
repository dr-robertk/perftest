import os

# set number of threads to be used for thread parallel version
os.environ['OMP_NUM_THREADS'] = '4'

from dune.fem import parameter
from dune.femdg.testing import run

# from euler import constant as problem
from euler import sod as problem
# from euler import vortex as problem
# from euler import leVeque as problem
# from euler import radialSod3 as problem

dim = 2
gamma = 1.4

parameter.append({"fem.verboserank": -1})
#parameter.append({"fem.threads.verbose": True})

primitive=lambda Model,uh: {"pressure": Model.toPrim(uh)[2]}
parameters = {"fem.ode.odesolver": "EX",
              "fem.timeprovider.factor": 0.25,
              "fem.ode.order": 3,
              "femdg.limiter.admissiblefunctions": 1,
              "femdg.limiter.tolerance": 1,
              "femdg.limiter.epsilon": 1e-8}
#-----------------
# "dgadvectionflux.method": "EULER-HLLC", "EULER-HLL", "LLF"
# default value is 'LLF'
#-----------------
# femdg.limiter.tolerance: 1 (tolerance for shock indicator)
# femdg.limiter.epsilon: 1e-8 (epsilon to avoid rounding errors)
# femdg.limiter.admissiblefunctions:
#    0 = only dg solution | 1 = only reconstruction | 2 = both
#-----------------

Model = problem()
Model.exact = None

def runDGTest(T = 0.25):
    Model.endTime = T
    solution, counters = run(Model,
            startLevel=4, polOrder=2, limiter="default",
            primitive=primitive, saveStep=1e10, subsamp=2,
            dt=None,threading=False,grid="alucube", space="dgonb",
            parameters=parameters)
    print(f"*** Run time = {counters[1]} sec ***")

# use shorter end time for testing and compilation
runDGTest(T=0.01)

#########################################
##
##  TODO: Add below the timing routines
##
#########################################

runDGTest(T=0.1)
