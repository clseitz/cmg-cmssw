from CMGTools.TTHAnalysis.treeReAnalyzer import *
from ROOT import TLorentzVector, TVector2, std
import ROOT
import time
import itertools
import PhysicsTools.Heppy.loadlibs
import array
import operator

def deltaR(eta1,eta2,phi1,phi2):        
  deta = eta1-eta2                                                                                                          
  dphi = ROOT.TVector2.Phi_mpi_pi(phi1-phi2);                                                                               
  return sqrt( deta*deta+dphi*dphi )  

class ExtraJets1L:
	def __init__(self):
          self.branches = [("nGenTop","I"),("GenTopidx","I",10,"nGenTop"),
                           ("GenTopDRdecay","F",10,"nGenTop"), ("GenTopPt","F",10,"nGenTop"),
                           ("nGenW","I"),("GenWidx","I",10,"nGenW"),
                           ("GenWDRdecay","F",10,"nGenW"), ("GenWPt","F",10,"nGenW"),
                           ("nJetTEST30","I"),("JetTEST30idx","I",100,"nJetTEST30"),
                           
                           ("nJetTopMatch","I"),("JetTopMatchidx","I",100,"nJetTopMatch"),
                           ("TopMatchidx","I",100,"nJetTopMatch"),
                            ("nJetWMatch","I"),("JetWMatchidx","I",100,"nJetWMatch"),
                            ("WMatchidx","I",100,"nJetWMatch"),
                            ("nJetQGMatch","I"),("JetQGMatchidx","I",100,"nJetQGMatch"),

                           ("nAk8TopMatch","I"),("Ak8TopMatchidx","I",100,"nAk8TopMatch"),
                           ("Ak8TopGenidx","I",100,"nAk8TopMatch"),
                           ("nAk8WMatch","I"),("Ak8WMatchidx","I",100,"nAk8WMatch"),
                           ("Ak8WGenidx","I",100,"nAk8WMatch"),
                           ("nAk8QGMatch","I"),("Ak8QGMatchidx","I",100,"nAk8QGMatch"),
                           
                           "nWTagAk4", "nWTagPlusTau21Ak4",
                            "nWTagAk8", "nWTagPlusTau21Ak8",
                           "nTopTagAk8", "nTopTagAk8PlusTau23"
                            ]


        def listBranches(self):
          return self.branches[:]


	def __call__(self,event,keyvals):
		jets = [j for j in Collection(event,"JetTEST","nJetTEST")]
		genpart = [g for g in Collection(event,"GenPart","nGenPart")]
                fatjets = [j for j in Collection(event,"FatJet","nFatJet")] 

                genTop = []
                genTopidx = []
                genW = []
                genWidx = []
                genBfromTop = []
                genQfromW = []
                genQG = []

                #find tops and W for matching
                for i,g in enumerate(genpart):
                  if (g.pt > 01.0):
                    if abs(g.pdgId) == 6:
                      genTop.append(g)
                      genTopidx.append(i)
                    if abs(g.pdgId) == 24:
                      genW.append(g)
                      genWidx.append(i)
                    if abs(g.pdgId) == 5 and abs(g.motherId) == 6:
                      genBfromTop.append(g)
                    if abs(g.pdgId) >= 1 and abs(g.pdgId) <=4 and abs(g.motherId) == 24 and abs(g.grandmotherId) == 6:
                      genQfromW.append(g)
                     





                genTdecay = dict()
                genWdecay = dict()

                genTopidx = []
                genTopDRdecay = []
                genTopPt = []
                
                genWidx = []
                genWDRdecay = []
                genWPt = []
                for i,g in enumerate(genpart):                                                                      
                  if (g.pt > 01.0): 
                    if abs(g.pdgId) == 6:
                      genTdecay[i]=[]
                    if abs(g.pdgId) == 24:
                      genWdecay[i]=[]
                    if abs(g.pdgId) == 5 and abs(g.motherId) == 6:
                      if g.motherIndex  in genTdecay:
                        genTdecay[g.motherIndex].append(g)
                    if abs(g.pdgId) >= 1 and abs(g.pdgId) <= 4 and abs(g.motherId) == 24 and abs(g.grandmotherId)== 6:
                      if genpart[g.motherIndex].motherIndex in genTdecay:
                        genTdecay[genpart[g.motherIndex].motherIndex].append(g)
                      if g.motherIndex in genWdecay:
                        genWdecay[g.motherIndex].append(g)  


                
                for i in genTdecay:
                  genTopidx.append(int(i))
                  t = genpart[int(i)]
                  maxDR = -99
                  #only use hadronic tops -> 3 decay products
                  if len(genTdecay[i]) >= 3:
                    for j in genTdecay[i]:
                      if deltaR(j.eta, t.eta, j.phi, t.phi) > maxDR:
                        maxDR =  deltaR(j.eta, t.eta, j.phi, t.phi)
                  genTopDRdecay.append(maxDR)
                  genTopPt.append(t.pt)



                for i in genWdecay:
                  genWidx.append(int(i))
                  w = genpart[int(i)]
                  maxDR = -99
                  #only use hadronic W
                  if len(genWdecay[i]) >=2:
                    for j in genWdecay[i]:
                      if deltaR(j.eta, w.eta, j.phi, w.phi) > maxDR:
                        maxDR =  deltaR(j.eta, w.eta, j.phi, w.phi)
                  genWDRdecay.append(maxDR)
                  genWPt.append(w.pt)
                  
		ret = { 'nGenTop'   : len(genTopidx) }
                ret['GenTopidx'] = genTopidx  
                ret['GenTopDRdecay'] = genTopDRdecay
                ret['GenTopPt'] = genTopPt

                ret['nGenW'] = len(genWidx)
                ret['GenWidx'] = genWidx  
                ret['GenWDRdecay'] = genWDRdecay
                ret['GenWPt'] = genWPt
		njet = len(jets)
		centralEta = 2.4
		### JETS

		JetTEST30 = []
		JetTEST30idx = []
		JetTopMatchidx = []
		JetWMatchidx = []
                TopMatchidx = []
                WMatchidx = []
		JetQGMatchidx = []
                QGMatch = []

		for i,j in enumerate(jets):
			if j.pt>30 and abs(j.eta)<centralEta:
				JetTEST30.append(j)
				JetTEST30idx.append(i)
                                

                                minDrTop = 9999.9                
                                minDrW = 9999.9                
                                minDrQ = 9999.9 
                                
                                part = 0
                                match = False
                                for k in genTopidx:
                                  t = genpart[k]
                                  if (deltaR(j.eta, t.eta, j.phi, t.phi) < minDrTop):
                                    minDrTop = deltaR(j.eta, t.eta, j.phi, t.phi)
                                    part = k
                                if minDrTop <  0.2:
                                  match = True
                                  JetTopMatchidx.append(i)
                                  TopMatchidx.append(part)
                                #match to W
                                part = 0
                                for k in genWidx:
                                  w = genpart[k]
                                  if (deltaR(j.eta, w.eta, j.phi, w.phi) < minDrW):
                                    minDrW = deltaR(j.eta, w.eta, j.phi, w.phi)
                                    part = k
                                if minDrW <  0.2:
                                  match = True
                                  JetWMatchidx.append(i)
                                  WMatchidx.append(part)

                                if match == False:
                                  JetQGMatchidx.append(i)

   

		ret['nJetTEST30'] = len(JetTEST30)
		ret['JetTEST30idx'] = JetTEST30idx
		ret['nJetTopMatch'] = len(JetTopMatchidx)
		ret['JetTopMatchidx'] = JetTopMatchidx
		ret['TopMatchidx'] = TopMatchidx
		ret['nJetWMatch'] = len(JetWMatchidx)
		ret['JetWMatchidx'] = JetWMatchidx
		ret['WMatchidx'] = WMatchidx
		ret['nJetQGMatch'] = len(JetQGMatchidx)
		ret['JetQGMatchidx'] = JetQGMatchidx
                               
 
                ret['nWTagAk4']=0                                                                              
                ret['nWTagPlusTau21Ak4']=0                                                                     
                for i,j in enumerate(JetTEST30):                         
                  if j.prunedMass>70 and j.prunedMass<100:                  
                    ret['nWTagAk4'] += 1                                                                   
                    if j.tau2/j.tau1 < 0.5 and j.tau2/j.tau1 > 0: 
                      ret['nWTagPlusTau21Ak4'] += 1           


		Ak8TopMatchidx = []
		Ak8TopGenidx = []
                Ak8WMatchidx = []
		Ak8WGenidx = []

                Ak8QGMatchidx = []



		for i,j in enumerate(fatjets):
			if j.pt>30 and abs(j.eta)<centralEta:
                                minDrTop = 9999.9                
                                minDrW = 9999.9                
                                minDrQ = 9999.9 
                                
                                part = 0
                                match = False
                                for k in genTopidx:
                                  t = genpart[k]
                                  if (deltaR(j.eta, t.eta, j.phi, t.phi) < minDrTop):
                                    minDrTop = deltaR(j.eta, t.eta, j.phi, t.phi)
                                    part = k
                                if minDrTop <  0.5:
                                  match = True
                                  Ak8TopMatchidx.append(i)
                                  Ak8TopGenidx.append(part)
                                #match to W
                                part = 0
                                for k in genWidx:
                                  w = genpart[k]
                                  if (deltaR(j.eta, w.eta, j.phi, w.phi) < minDrW):
                                    minDrW = deltaR(j.eta, w.eta, j.phi, w.phi)
                                    part = k
                                if minDrW <  0.5:
                                  match = True
                                  Ak8WMatchidx.append(i)
                                  Ak8WGenidx.append(part)

                                if match == False:
                                  Ak8QGMatchidx.append(i)
                                 

		ret['nAk8TopMatch'] = len(Ak8TopMatchidx)
		ret['Ak8TopMatchidx'] = Ak8TopMatchidx
		ret['Ak8TopGenidx'] = Ak8TopGenidx
		ret['nAk8WMatch'] = len(Ak8WMatchidx)
		ret['Ak8WMatchidx'] = Ak8WMatchidx
		ret['Ak8WGenidx'] = Ak8WGenidx

		ret['Ak8QGMatchidx'] = Ak8QGMatchidx


                ret['nWTagAk8']=0                                                                              
                ret['nWTagPlusTau21Ak8']=0                                                                     
                ret['nTopTagAk8']=0
                ret['nTopTagAk8PlusTau23']=0

                for i,j in enumerate(fatjets):
                  if j.nSubJets >2 and j.minMass>50 and j.topMass>140 and j.topMass<250:
                    ret['nTopTagAk8'] += 1
                    if j.tau3 < 0.6 * j.tau2: # instead of division
                      ret['nTopTagAk8PlusTau23'] += 1
                  if j.prunedMass>60 and j.prunedMass<100:                  
                    ret['nWTagAk8'] += 1                                                                   
                    if j.tau2/j.tau1 < 0.5 and j.tau2/j.tau1> 0:
                      ret['nWTagPlusTau21Ak8'] += 1
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
