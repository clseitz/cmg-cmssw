import PhysicsTools.HeppyCore.framework.config as cfg
import os


################## Triggers
from CMGTools.TTHAnalysis.samples.triggers_13TeV_PHYS14 import *



#####COMPONENT CREATOR

from CMGTools.TTHAnalysis.samples.ComponentCreator import ComponentCreator
kreator = ComponentCreator()



#### Background samples

# TTbar cross section: MCFM with dynamic scale, StandardModelCrossSectionsat13TeV
TTJets = kreator.makeMCComponent("TTJets", "/TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola/Phys14DR-PU20bx25_PHYS14_25_V1-v1/MINIAODSIM", "CMS", ".*root",809.1)


SMS_T1tttt_2J_mGl1500_mLSP100 = kreator.makeMCComponent("SMS_T1tttt_2J_mGl1500_mLSP100", "/SMS-T1tttt_2J_mGl-1500_mLSP-100_Tune4C_13TeV-madgraph-tauola/Phys14DR-PU20bx25_tsg_PHYS14_25_V1-v1/MINIAODSIM", "CMS", ".*root",0.0141903)
SMS_T1tttt_2J_mGl1200_mLSP800 = kreator.makeMCComponent("SMS_T1tttt_2J_mGl1200_mLSP800", "/SMS-T1tttt_2J_mGl-1200_mLSP-800_Tune4C_13TeV-madgraph-tauola/Phys14DR-PU20bx25_tsg_PHYS14_25_V1-v1/MINIAODSIM", "CMS", ".*root",0.0856418)

SMS_T1tttt_2J_mGl1500_mLSP100_toptag = kreator.makeMCComponentFromLocal('SMS_T1tttt_2J_mGl1500_mLSP100_toptag', 
                                                                        '/13TeV_T1tttt_gluino_1500_LSP_100',
                                                                        '/nfs/dust/cms/group/susy-desy/Run2/MC/MiniAOD/PHYS14_PU20_25ns/MINIAOD_Tagger/%s', '.*root',0.0141903)

mcSamples = [TTJets, SMS_T1tttt_2J_mGl1500_mLSP100_toptag,SMS_T1tttt_2J_mGl1500_mLSP100,SMS_T1tttt_2J_mGl1200_mLSP800]
from CMGTools.TTHAnalysis.setup.Efficiencies import *


#Define splitting
for comp in mcSamples:
    comp.isMC = True
    comp.isData = False
    comp.splitFactor = 250


if __name__ == "__main__":
   import sys
   if "test" in sys.argv:
       from CMGTools.TTHAnalysis.samples.ComponentCreator import testSamples
       testSamples(mcSamples)
