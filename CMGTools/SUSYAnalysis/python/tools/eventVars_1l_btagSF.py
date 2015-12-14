from CMGTools.TTHAnalysis.treeReAnalyzer import *
import ROOT
import itertools
import PhysicsTools.Heppy.loadlibs

# Basing on macro from Vienna
# https://github.com/HephySusySW/Workspace/blob/74X-master/RA4Analysis/cmgPostProcessing/btagEfficiency.py

# legacy 2012 BtagSFs
import PhysicsTools.Heppy.physicsutils.BTagSF

# Cuts for jets
minJpt = 30
maxJeta = 2.4
btagWP = 0.890

# pt, eta bins
ptBorders = [30, 40, 50, 60, 70, 80, 100, 120, 160, 210, 260, 320, 400, 500, 670]
ptBins = []
etaBins = [[0,0.8], [0.8,1.6], [ 1.6, 2.4]]

for i in range(len(ptBorders)-1):
    ptBins.append([ptBorders[i], ptBorders[i+1]])
    if i == len(ptBorders)-2:
        ptBins.append([ptBorders[i+1], -1])

def partonName (parton):
    if parton==5:  return 'b'
    if parton==4:  return 'c'
    return 'other'

### SF ROOT file
sfFname = "SFs/btagSF.root"

# load SFs from csv file
calib = ROOT.BTagCalibration("csvv2", sfFname)

# SF readers (from CMSSW)
readerCombUp      = ROOT.BTagCalibrationReader(calib, 1, "comb", "up")
readerCombCentral = ROOT.BTagCalibrationReader(calib, 1, "comb", "central")
readerCombDown    = ROOT.BTagCalibrationReader(calib, 1, "comb", "down")
readerMuUp        = ROOT.BTagCalibrationReader(calib, 1, "mujets", "up")
readerMuCentral   = ROOT.BTagCalibrationReader(calib, 1, "mujets", "central")
readerMuDown      = ROOT.BTagCalibrationReader(calib, 1, "mujets", "down")

def getSF2015(parton, pt, eta):
    if abs(parton)==5: #SF for b
        sf   = readerMuCentral.eval(0, eta, pt)
        sf_d = readerMuDown.eval(0, eta, pt)
        sf_u = readerMuUp.eval(0, eta, pt)
    elif abs(parton)==4: #SF for c
        sf   = readerMuCentral.eval(1, eta, pt)
        sf_d = readerMuDown.eval(1, eta, pt)
        sf_u = readerMuUp.eval(1, eta, pt)
    else: #SF for light flavours
        sf   = readerCombCentral.eval(2, eta, pt)
        sf_d = readerCombDown.eval(2, eta, pt)
        sf_u = readerCombUp.eval(2, eta, pt)
    return {"SF":sf, "SF_down":sf_d,"SF_up":sf_u}

# MC eff  -- precomputed
bTagEffFile = "SFs/btagMCeff.pck"
try:
  mcEffDict = pickle.load(file(bTagEffFile))
except IOError:
  print 'Unable to load MC efficiency file!'
  mcEffDict = False

def getMCEff(parton, pt, eta, mcEff, year = 2015):
    for ptBin in ptBins:
        if pt>=ptBin[0] and (pt<ptBin[1] or ptBin[1]<0):
            for etaBin in etaBins:
                if abs(eta)>=etaBin[0] and abs(eta)<etaBin[1]:
                    if year == 2015: res=getSF2015(parton, pt, eta)
                    else: res=getSF(parton, pt, eta, year)
                    if abs(parton)==5:                  res["mcEff"] = mcEff[tuple(ptBin)][tuple(etaBin)]["b"]
                    if abs(parton)==4:                  res["mcEff"] = mcEff[tuple(ptBin)][tuple(etaBin)]["c"]
                    if abs(parton)>5 or abs(parton)<4:  res["mcEff"] = mcEff[tuple(ptBin)][tuple(etaBin)]["other"]
                    return res
    return {} #empty if not found

# friend tree style
# get MC efficiencies and scale factors for all jets of one event, uses getMCEff
def getMCEfficiencyForBTagSF(event, mcEff, onlyLightJetSystem = False, isFastSim = False):

    # jets from event collection
    cjets = [j for j in Collection(event,"Jet","nJet")]
    jets = [] # list of jets for bTagSF

    for jet in cjets:
       jPt     = jet.pt
       jEta    = jet.eta
       jParton = jet.mcFlavour

       if jPt <= minJpt or abs(jEta) >=maxJeta or (not jet.id): continue

       if onlyLightJetSystem:
           if jet.btagCSV > btagWP: continue
           jParton=1

       jets.append([jParton, jPt, jEta])

    # set jParton to 4 for a random jet
    if onlyLightJetSystem and len(jets)>0:
        nc = randint(0, len(jets)-1)
        jets[nc][0] = 4

    # append corresp. jet bTag MC eff
    for jet in jets:
        jParton, jPt, jEta = jet
        r = getMCEff(jParton, jPt, jEta, mcEff, 2015) #getEfficiencyAndMistagRate(jPt, jEta, jParton )
        jet.append(r)

    if len(jets) != len(cjets):
        print "!! Different number of jets:", len(jets), 'vs', len(cjets)
        return 0

    # Compute and apply the SFs

    #effNames = ['','SF','SF_b_Up','SF_b_Down','SF_light_Up','SF_light_Down']
    #mcEffs = {name:tuple() for name in effNames}

    mceffs = tuple()
    mceffs_SF = tuple()
    mceffs_SF_b_Up = tuple()
    mceffs_SF_b_Down = tuple()
    mceffs_SF_light_Up = tuple()
    mceffs_SF_light_Down = tuple()

    for jParton, jPt, jEta, r in jets:
        if isFastSim:
            fsim_SF = ROOT.getFastSimCorr(partonName(abs(jParton)),jPt,"mean",jEta)
            fsim_SF_up = ROOT.getFastSimCorr(partonName(abs(jParton)),jPt,"up",jEta)
            fsim_SF_down = ROOT.getFastSimCorr(partonName(abs(jParton)),jPt,"down",jEta)
        else:
            fsim_SF = 1.
            fsim_SF_up = 1.
            fsim_SF_down = 1.
        mceffs += (r["mcEff"],)
        mceffs_SF += (r["mcEff"]*r["SF"]*fsim_SF,)
        if abs(jParton)==5 or abs(jParton)==4:
            mceffs_SF_b_Up   += (r["mcEff"]*r["SF_up"]*fsim_SF_up,)
            mceffs_SF_b_Down += (r["mcEff"]*r["SF_down"]*fsim_SF_down,)
            mceffs_SF_light_Up   += (r["mcEff"]*r["SF"],)
            mceffs_SF_light_Down += (r["mcEff"]*r["SF"],)
        else:
            mceffs_SF_b_Up   += (r["mcEff"]*r["SF"],)
            mceffs_SF_b_Down += (r["mcEff"]*r["SF"],)
            mceffs_SF_light_Up   += (r["mcEff"]*r["SF_up"]*fsim_SF_up,)
            mceffs_SF_light_Down += (r["mcEff"]*r["SF_down"]*fsim_SF_down,)

    return {"mceffs":mceffs, "mceffs_SF":mceffs_SF, "mceffs_SF_b_Up":mceffs_SF_b_Up, "mceffs_SF_b_Down":mceffs_SF_b_Down, "mceffs_SF_light_Up":mceffs_SF_light_Up, "mceffs_SF_light_Down":mceffs_SF_light_Down}
    #return mcEffs

# Flags
isFastSim = False

class EventVars1L_btagSF:
    def __init__(self):
        self.branches = [ "btagSF" ]

    def listBranches(self):
        return self.branches[:]

    def __call__(self,event,base):

        # output dict:
        ret = {}

        zeroTagWeight = 1.

        # Get MC efficiencies for this event
        mceff = getMCEfficiencyForBTagSF(t, mcEffDict[sampleKey], isFastSim)

        print mceff["mceffs"]

        # return branches
        return ret

if __name__ == '__main__':
    from sys import argv
    file = ROOT.TFile(argv[1])
    tree = file.Get("tree")
    class Tester(Module):
        def __init__(self, name):
            Module.__init__(self,name,None)
            self.sf = EventVars1L()
        def analyze(self,ev):
            print "\nrun %6d lumi %4d event %d: leps %d" % (ev.run, ev.lumi, ev.evt, ev.nLepGood)
            print self.sf(ev)
    el = EventLoop([ Tester("tester") ])
    el.loop([tree], maxEvents = 50)
