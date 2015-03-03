##########################################################
##       CONFIGURATION FOR SUSY SingleLep TREES       ##
## skim condition: >= 1 loose leptons, no pt cuts or id ##
##########################################################
import PhysicsTools.HeppyCore.framework.config as cfg


#Load all analyzers
from CMGTools.TTHAnalysis.analyzers.susyCore_modules_cff import * 

lepAna.loose_muon_pt  = 5
lepAna.loose_muon_relIso = 0.5
lepAna.mu_isoCorr = "rhoArea" 
lepAna.loose_electron_pt  = 7
lepAna.loose_electron_relIso = 0.5
lepAna.ele_isoCorr = "rhoArea" 


# Redefine what I need
# run miniIso
lepAna.doMiniIsolation = True
lepAna.packedCandidates = 'packedPFCandidates'
lepAna.miniIsolationPUCorr = 'rhoArea'
lepAna.miniIsolationVetoLeptons = None
# --- LEPTON SKIMMING ---
ttHLepSkim.minLeptons = 1
ttHLepSkim.maxLeptons = 999
#LepSkim.idCut  = ""
#LepSkim.ptCuts = []

# --- JET-LEPTON CLEANING ---
jetAna.minLepPt = 10 

jetAna.mcGT = "PHYS14_25_V2_LowPtHenningFix"
jetAna.doQG = True
jetAna.smearJets = False #should be false in susycore, already
jetAna.recalibrateJets = True #should be true in susycore, already
metAna.recalibrate = False #should be false in susycore, already


#ttHReclusterJets = cfg.Analyzer(
#            'ttHReclusterJetsAnalyzer',
#            )

# Event Analyzer for susy multi-lepton (at the moment, it's the TTH one)


isoTrackAna.setOff=False

#from CMGTools.TTHAnalysis.analyzers.ttHReclusterJetsAnalyzer  import ttHReclusterJetsAnalyzer
#ttHReclusterJets = cfg.Analyzer(
#    ttHReclusterJetsAnalyzer, name="ttHReclusterJetsAnalyzer",
#    )


from CMGTools.TTHAnalysis.analyzers.ttHLepEventAnalyzer import ttHLepEventAnalyzer
ttHEventAna = cfg.Analyzer(
    ttHLepEventAnalyzer, name="ttHLepEventAnalyzer",
    minJets25 = 0,
    )

from CMGTools.TTHAnalysis.analyzers.ttHTopJetAnalyzer import ttHTopJetAnalyzer
ttHTopJetAna = cfg.Analyzer(
    ttHTopJetAnalyzer, name = 'ttHTopJetAnalyzer',
    jetCol_0 = 'cmsTopTagCa15PFJetsCHS',
    tagCol_0 = 'ca15CMSTopTagInfos',
    jettinesCol_0 = 'ca15PFJetsCHSNjettiness',
    jetCol_1 = 'cmsTopTagCa08PFJetsCHS',
    tagCol_1 = 'ca08CMSTopTagInfos',
    jettinesCol_1 = 'ca08PFJetsCHSNjettiness',
    jetPt = 100.,
    jetEta = 2.4,
    )
## Insert the SV analyzer in the sequence
susyCoreSequence.insert(susyCoreSequence.index(ttHCoreEventAna),
                        ttHFatJetAna)
susyCoreSequence.insert(susyCoreSequence.index(ttHCoreEventAna),
                        ttHTopJetAna)
susyCoreSequence.insert(susyCoreSequence.index(ttHCoreEventAna),
                        ttHSVAna)
#susyCoreSequence.insert(susyCoreSequence.index(ttHCoreEventAna),
#                        ttHHeavyFlavourHadronAna)

## Single lepton + ST skim
from CMGTools.TTHAnalysis.analyzers.ttHSTSkimmer import ttHSTSkimmer
ttHSTSkimmer = cfg.Analyzer(
    ttHSTSkimmer, name='ttHSTSkimmer',
    minST = 175,
    )


#from CMGTools.TTHAnalysis.samples.samples_13TeV_PHYS14  import *

triggerFlagsAna.triggerBits = {
#put trigger here for data
}

# Tree Producer
from CMGTools.TTHAnalysis.analyzers.treeProducerSusySingleLepton import *
## Tree Producer
treeProducer = cfg.Analyzer(
     AutoFillTreeProducer, name='treeProducerSusySingleLepton',
     vectorTree = True,
     saveTLorentzVectors = False,  # can set to True to get also the TLorentzVectors, but trees will be bigger
     defaultFloatType = 'F', # use Float_t for floating point
     PDFWeights = PDFWeights,
     globalVariables = susySingleLepton_globalVariables,
     globalObjects = susySingleLepton_globalObjects,
     collections = susySingleLepton_collections,
)



#-------- SAMPLES AND TRIGGERS -----------

from CMGTools.TTHAnalysis.samples.samples_13TeV_PHYS14_private import *
#selectedComponents = [ SingleMu, DoubleElectron, TTHToWW_PUS14, DYJetsToLL_M50_PU20bx25, TTJets_PUS14 ]
#SMS_T1bbbb_2J_mGl1500_mLSP100 = kreator.makeMCComponent("SMS_T1bbbb_2J_mGl1500_mLSP100", "/SMS-T1bbbb_2J_mGl-1500_mLSP-100_Tune4C_13TeV-madgraph-tauola/Phys14DR-PU20bx25_tsg_PHYS14_25_V1-v1/MINIAODSIM", "CMS", ".*root",0.0141903)  
#-------- SEQUENCE

sequence = cfg.Sequence(susyCoreSequence+[
    ttHEventAna,
#    ttHReclusterJets,
    ttHSTSkimmer,
    treeProducer,
    ])


#-------- HOW TO RUN
test = 1
if test==1:
    # test a single component, using a single thread.
#    comp = TTJets
    comp = SMS_T1tttt_2J_mGl1500_mLSP100_toptag
#    comp.files = comp.files[:1]
    selectedComponents = [comp]
    comp.splitFactor = 1
elif test==2:    
    # test all components (1 thread per component).
    for comp in selectedComponents:
        comp.splitFactor = 1
        comp.files = comp.files[:1]

from PhysicsTools.HeppyCore.framework.eventsfwlite import Events
config = cfg.Config( components = selectedComponents,
                     sequence = sequence,
                     services = [],
                     events_class = Events)
