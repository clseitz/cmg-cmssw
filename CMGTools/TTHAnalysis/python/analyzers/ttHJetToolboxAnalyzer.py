import math, os
from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.Heppy.physicsobjects.PhysicsObjects import Jet
from PhysicsTools.HeppyCore.utils.deltar import deltaR2, deltaPhi, matchObjectCollection, matchObjectCollection2, bestMatch
from PhysicsTools.Heppy.physicsutils.JetReCalibrator import JetReCalibrator
import PhysicsTools.HeppyCore.framework.config as cfg

from PhysicsTools.Heppy.physicsutils.QGLikelihoodCalculator import QGLikelihoodCalculator



def cleanNearestJetOnly(jets,leptons,deltaR):
    dr2 = deltaR**2
    good = [ True for j in jets ]
    for l in leptons:
        ibest, d2m = -1, dr2
        for i,j in enumerate(jets):
            d2i = deltaR2(l.eta(),l.phi(), j.eta(),j.phi())
            if d2i < d2m:
                ibest, d2m = i, d2i
        if ibest != -1: good[ibest] = False
        return [ j for (i,j) in enumerate(jets) if good[i] == True ] 

def cleanJetsAndLeptons(jets,leptons,deltaR,arbitration):
    dr2 = deltaR**2
    goodjet = [ True for j in jets ]
    goodlep = [ True for l in leptons ]
    for il, l in enumerate(leptons):
        ibest, d2m = -1, dr2
        for i,j in enumerate(jets):
            d2i = deltaR2(l.eta(),l.phi(), j.eta(),j.phi())
            if d2i < dr2:
                if arbitration(j,l) == j:
                   # if the two match, and we prefer the jet, then drop the lepton and be done
                   goodlep[il] = False
                   break 
            if d2i < d2m:
                ibest, d2m = i, d2i
        # this lepton has been killed by a jet, then we clean the jet that best matches it
        if not goodlep[il]: continue 
        if ibest != -1: goodjet[ibest] = False
    return ( [ j for (i ,j) in enumerate(jets)    if goodjet[i ] == True ], 
             [ l for (il,l) in enumerate(leptons) if goodlep[il] == True ] )


class ttHJetToolboxAnalyzer( Analyzer ):
    def __init__(self, cfg_ana, cfg_comp, looperName):
        super(ttHJetToolboxAnalyzer,self).__init__(cfg_ana, cfg_comp, looperName)
        mcGT   = cfg_ana.mcGT   if hasattr(cfg_ana,'mcGT')   else "PHYS14_25_V2"
        dataGT = cfg_ana.dataGT if hasattr(cfg_ana,'dataGT') else "GR_70_V2_AN1"
        self.shiftJEC = self.cfg_ana.shiftJEC if hasattr(self.cfg_ana, 'shiftJEC') else 0
        self.recalibrateJets = self.cfg_ana.recalibrateJets
        if   self.recalibrateJets == "MC"  : self.recalibrateJets =     self.cfg_comp.isMC
        elif self.recalibrateJets == "Data": self.recalibrateJets = not self.cfg_comp.isMC
        elif self.recalibrateJets not in [True,False]: raise RuntimeError, "recalibrateJets must be any of { True, False, 'MC', 'Data' }, while it is %r " % self.recalibrateJets
        self.doJEC = self.recalibrateJets or (self.shiftJEC != 0)
        if self.doJEC:
          if self.cfg_comp.isMC:
            self.jetReCalibrator = JetReCalibrator(mcGT,"AK4PFchs", False,cfg_ana.jecPath)
          else:
            self.jetReCalibrator = JetReCalibrator(dataGT,"AK4PFchs", True,cfg_ana.jecPath)

        self.doPuId = getattr(self.cfg_ana, 'doPuId', True)
        self.jetLepDR = getattr(self.cfg_ana, 'jetLepDR', 0.4)
        self.jetLepArbitration = getattr(self.cfg_ana, 'jetLepArbitration', lambda jet,lepton: lepton) 
        self.lepPtMin = getattr(self.cfg_ana, 'minLepPt', -1)
        self.lepSelCut = getattr(self.cfg_ana, 'lepSelCut', lambda lep : True)
        self.jetGammaDR =  getattr(self.cfg_ana, 'jetGammaDR', 0.4)
        if(self.cfg_ana.doQG):
            self.qglcalc = QGLikelihoodCalculator("/afs/cern.ch/user/t/tomc/public/qgTagger/QGLikelihoodDBFiles/QGL_v1a/pdfQG_AK4chs_antib_13TeV_v1.root")

    def declareHandles(self):
        super(ttHJetToolboxAnalyzer, self).declareHandles()
        self.handles['jets']   = AutoHandle( self.cfg_ana.jetCol, 'std::vector<pat::Jet>' )
        self.handles['genJet'] = AutoHandle( (self.cfg_ana.jetCol,"genJets"), 'vector<reco::GenJet>' )
        self.shiftJER = self.cfg_ana.shiftJER if hasattr(self.cfg_ana, 'shiftJER') else 0
        self.handles['rho'] = AutoHandle( ('fixedGridRhoFastjetAll','',''), 'double' )
    
    def beginLoop(self, setup):
        super(ttHJetToolboxAnalyzer,self).beginLoop(setup)
        
    def process(self, event):
        self.readCollections( event.input )
        rho  = float(self.handles['rho'].product()[0])

        ## Read jets, if necessary recalibrate and shift MET
        allJets = map(Jet, self.handles['jets'].product()) 

        deltaMetFromJEC = [0.,0.]
        if self.doJEC:
            self.jetReCalibrator.correctAll(allJets, rho, delta=self.shiftJEC, metShift=deltaMetFromJEC)
        allJetsUsedForMET = allJets

        if self.cfg_comp.isMC:
            genJets = [ x for x in self.handles['genJet'].product() ]
            self.matchJets(event, allJets)
            if getattr(self.cfg_ana, 'smearJets', False):
                self.smearJets(event, allJets)
        
	##Sort Jets by pT 
        allJets.sort(key = lambda j : j.pt(), reverse = True)
        
	## Apply jet selection
        jets = []

        for jet in allJets:
            if self.testJetID (jet ):
                jets.append(jet)
                
        ## Clean Jets from leptons
        leptons = []
        if hasattr(event, 'selectedLeptons'):
            leptons = [ l for l in event.selectedLeptons if l.pt() > self.lepPtMin and self.lepSelCut(l) ]
            
        cleanJetsAll, cleanLeptons = cleanJetsAndLeptons(jets, leptons, self.jetLepDR, self.jetLepArbitration)
        cleanJets    = [j for j in cleanJetsAll if  ( abs(j.eta()) <  self.cfg_ana.jetEtaCentral and j.pt() >  self.cfg_ana.jetPt )]

        #MC stuff
        if self.cfg_comp.isMC:
            deltaMetFromJetSmearing = [0, 0]
            for j in cleanJetsAll:
                if hasattr(j, 'deltaMetFromJetSmearing'):
                    deltaMetFromJetSmearing[0] += j.deltaMetFromJetSmearing[0]
                    deltaMetFromJetSmearing[1] += j.deltaMetFromJetSmearing[1]
                cleanGenJets = cleanNearestJetOnly(genJets, leptons, self.jetLepDR)
            

        event.ToolboxJets = []

        event.ToolboxJets = cleanJets
    
        return True

        

    def testJetID(self, jet):
        jet.pfJetIdPassed = jet.jetID('POG_PFID_Loose') 
        
        return jet.pfJetIdPassed

    def matchJets(self, event, jets):
        match = matchObjectCollection2(jets,
                                       event.genbquarks + event.genwzquarks,
                                       deltaRMax = 0.3)
        for jet in jets:
            gen = match[jet]
            jet.mcParton    = gen
            jet.mcMatchId   = (gen.sourceId     if gen != None else 0)
            jet.mcMatchFlav = (abs(gen.pdgId()) if gen != None else 0)

        match = matchObjectCollection2(jets,
                                       event.genJets,
                                       deltaRMax = 0.3)
        for jet in jets:
            jet.mcJet = match[jet]


 
    def smearJets(self, event, jets):
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TWikiTopRefSyst#Jet_energy_resolution
       for jet in jets:
            gen = jet.mcJet 
            if gen != None:
               genpt, jetpt, aeta = gen.pt(), jet.pt(), abs(jet.eta())
               # from https://twiki.cern.ch/twiki/bin/view/CMS/JetResolution
               factor = 1.052 + self.shiftJER*math.hypot(0.012,0.062);
               if   aeta > 2.3: factor = 1.288 + self.shiftJER*math.hypot(0.127,0.154)
               elif aeta > 1.7: factor = 1.134 + self.shiftJER*math.hypot(0.035,0.066)
               elif aeta > 1.1: factor = 1.096 + self.shiftJER*math.hypot(0.017,0.063)
               elif aeta > 0.5: factor = 1.057 + self.shiftJER*math.hypot(0.012,0.056)
               ptscale = max(0.0, (jetpt + (factor-1)*(jetpt-genpt))/jetpt)
               #print "get with pt %.1f (gen pt %.1f, ptscale = %.3f)" % (jetpt,genpt,ptscale)
               jet.deltaMetFromJetSmearing = [ -(ptscale-1)*jet.rawFactor()*jet.px(), -(ptscale-1)*jet.rawFactor()*jet.py() ]
               if ptscale != 0:
                  jet.setP4(jet.p4()*ptscale)
               # leave the uncorrected unchanged for sync
               jet._rawFactorMultiplier *= (1.0/ptscale) if ptscale != 0 else 1
            #else: print "jet with pt %.1d, eta %.2f is unmatched" % (jet.pt(), jet.eta())



setattr(ttHJetToolboxAnalyzer,"defaultConfig", cfg.Analyzer(
    class_object = ttHJetToolboxAnalyzer,
    jetCol = 'slimmedJets',
    jetPt = 25.,
    jetEta = 4.7,
    jetEtaCentral = 2.4,
    jetLepDR = 0.4,
    jetLepArbitration = (lambda jet,lepton : lepton), # you can decide which to keep in case of overlaps; e.g. if the jet is b-tagged you might want to keep the jet
    minLepPt = 10,
    lepSelCut = lambda lep : True,
    doPuId = False, # Not commissioned in 7.0.X
    doQG = False, 
    recalibrateJets = False,
    shiftJEC = 0, # set to +1 or -1 to get +/-1 sigma shifts
    smearJets = True,
    shiftJER = 0, # set to +1 or -1 to get +/-1 sigma shifts    
    jecPath = "",
    )
)
