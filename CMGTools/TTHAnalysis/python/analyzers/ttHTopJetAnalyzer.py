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
        self.handles['jets'] = AutoHandle( self.cfg_ana.jetCol, 'vector<reco::BasicJet>' )
        self.handles['pfjets'] = AutoHandle( 'ca15PFJetsCHSsoftdropz15b00', 'vector<reco::PFJet>' )
        self.handles['basicjets'] = AutoHandle( 'cmsTopTagCa15PFJetsCHS', 'vector<reco::BasicJet' )

        self.handles['toptaginfo'] = AutoHandle( self.cfg_ana.tagCol,'vector<reco::CATopJetTagInfo>')
        self.handles['njettinestau1'] = AutoHandle( (self.cfg_ana.jettinesCol,"tau1"),'edm::ValueMap<float>')
        self.handles['njettinestau2'] = AutoHandle( (self.cfg_ana.jettinesCol,"tau2"),'edm::ValueMap<float>')
        self.handles['njettinestau3'] = AutoHandle( (self.cfg_ana.jettinesCol,"tau3"),'edm::ValueMap<float>')

    def beginLoop(self, setup):
        super(ttHTopJetAnalyzer,self).beginLoop(setup)
        
    def process(self, event):
        self.readCollections( event.input )

        ## Read jets, if necessary recalibrate and shift MET
        allJets = self.handles['jets'].product()
        allTopInfo = self.handles['toptaginfo'].product()
        allTopTau1 = self.handles['njettinestau1'].product()
        allTopTau2 = self.handles['njettinestau2'].product()
        allTopTau3 = self.handles['njettinestau3'].product()

        print len(allJets), len(allTopTau1)
        ## Apply jet selection
        event.topJets     = []
        event.topJetsInfo = []
        event.njettines = []

#        for (jet,topinfo,tau1,tau2,tau3) in zip(allJets, allTopInfo, allTopTau1, allTopTau2, allTopTau3):
        for i in range(0,len(allJets)):
            taus = []
            if self.testJetNoID( allJets[i] ): 
                event.topJets.append(allJets[i]) 
                event.topJetsInfo.append(allTopInfo[i])
                taus.append(allTopTau1.get(i))
                taus.append(allTopTau2.get(i))
                taus.append(allTopTau3.get(i))
                event.njettines.append(taus)
                
    def testJetNoID( self, jet ):
        return jet.pt() > self.cfg_ana.jetPt and \
               abs( jet.eta() ) < self.cfg_ana.jetEta;
 
