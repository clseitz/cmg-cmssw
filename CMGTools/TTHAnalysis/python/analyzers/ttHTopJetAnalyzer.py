import random
import math
from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.PhysicsObjects import Jet

from PhysicsTools.HeppyCore.utils.deltar import *
import PhysicsTools.HeppyCore.framework.config as cfg

class ttHTopJetAnalyzer( Analyzer ):
    """Taken from RootTools.JetAnalyzer, simplified, modified, added corrections    """
    def __init__(self, cfg_ana, cfg_comp, looperName):
        super(ttHTopJetAnalyzer,self).__init__(cfg_ana, cfg_comp, looperName)
        self.jetLepDR = self.cfg_ana.jetLepDR  if hasattr(self.cfg_ana, 'jetLepDR') else 0.5
        self.lepPtMin = self.cfg_ana.minLepPt  if hasattr(self.cfg_ana, 'minLepPt') else -1


    def declareHandles(self):
        super(ttHTopJetAnalyzer, self).declareHandles()
        self.handles['jets_0'] = AutoHandle( self.cfg_ana.jetCol_0, 'vector<reco::BasicJet>' )
        self.handles['toptaginfo_0'] = AutoHandle( self.cfg_ana.tagCol_0,'vector<reco::CATopJetTagInfo>')
        self.handles['njettinestau1_0'] = AutoHandle( (self.cfg_ana.jettinesCol_0,"tau1"),'edm::ValueMap<float>')
        self.handles['njettinestau2_0'] = AutoHandle( (self.cfg_ana.jettinesCol_0,"tau2"),'edm::ValueMap<float>')
        self.handles['njettinestau3_0'] = AutoHandle( (self.cfg_ana.jettinesCol_0,"tau3"),'edm::ValueMap<float>')

        
        self.handles['jets_1'] = AutoHandle( self.cfg_ana.jetCol_1, 'vector<reco::BasicJet>' )
        self.handles['toptaginfo_1'] = AutoHandle( self.cfg_ana.tagCol_1,'vector<reco::CATopJetTagInfo>')
        self.handles['njettinestau1_1'] = AutoHandle( (self.cfg_ana.jettinesCol_1,"tau1"),'edm::ValueMap<float>')
        self.handles['njettinestau2_1'] = AutoHandle( (self.cfg_ana.jettinesCol_1,"tau2"),'edm::ValueMap<float>')
        self.handles['njettinestau3_1'] = AutoHandle( (self.cfg_ana.jettinesCol_1,"tau3"),'edm::ValueMap<float>')

        self.handles['test'] = AutoHandle( 'LooseMultiRHTTJetsCHS','vector<reco::HTTTopJetTagInfo>')

    def beginLoop(self, setup):
        super(ttHTopJetAnalyzer,self).beginLoop(setup)
        
    def process(self, event):
        self.readCollections( event.input )

        
        TestInfo = self.handles['test'].product()

        #print len(allJets), len(allTopTau1)
        ## Apply jet selection
        event.topJets_0     = []
        event.topJetsInfo_0 = []
        event.topNjettines_0 = []

        event.topJets_1     = []
        event.topJetsInfo_1 = []
        event.topNjettines_1 = []

        Jets = [event.topJets_0,event.topJets_1]
        JetsInfo = [event.topJetsInfo_0,event.topJetsInfo_1]
        JetsNjettines = [event.topNjettines_0,event.topNjettines_1]

        for types in range(0,2):
            allJets = self.handles['jets_'+str(types)].product()
            allTopInfo = self.handles['toptaginfo_'+str(types)].product()
            allTopTau1 = self.handles['njettinestau1_'+str(types)].product()
            allTopTau2 = self.handles['njettinestau2_'+str(types)].product()
            allTopTau3 = self.handles['njettinestau3_'+str(types)].product()
            
            for i in range(0,len(allJets)):
                taus = []
                if self.testJetNoID( allJets[i] ): 
                    Jets[types].append(allJets[i]) 
                    JetsInfo[types].append(allTopInfo[i])
                    taus.append(allTopTau1.get(i))
                    taus.append(allTopTau2.get(i))
                    taus.append(allTopTau3.get(i))
                    JetsNjettines[types].append(taus)


    def testJetNoID( self, jet ):
        return jet.pt() > self.cfg_ana.jetPt and \
               abs( jet.eta() ) < self.cfg_ana.jetEta;
 
