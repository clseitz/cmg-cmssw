from FastSimulation.PileUpProducer.PileUpSimulator8TeV_cfi import PileUpSimulatorBlock as block8TeV
from FastSimulation.Configuration.MixingFamos_cff import *

#define the PU scenario itself
famosPileUp.PileUpSimulator = block8TeV.PileUpSimulator
famosPileUp.PileUpSimulator.averageNumber = 0.000000
