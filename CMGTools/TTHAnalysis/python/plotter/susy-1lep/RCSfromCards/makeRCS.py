#!/usr/bin/env python
#Script to read data cards and turn them either into a table that can be copied to Excel/OpenOffice
#1;2cor print out in latex format.

import shutil
import subprocess
import os
import sys
import glob
from multiprocessing import Pool
from ROOT import *
import math

def _getYieldsFromInput(inargs, QCDoff = True):

    (sample, cardDir, binName, ratDict) = inargs

    if len(inargs) < 1:
        return (binName,[0,0])

    cardName = cardDir+"/common/CnC2015X_"+binName+".input.root"

    #print "# Starting Bin:", binName

    cardf = TFile(cardName,"READ")

    hTT_DiLep = cardf.Get("x_TT_DiLep")
    nTT_DiLep = hTT_DiLep.Integral()
    nTTErr_DiLep = hTT_DiLep.GetBinError(1)
                             
    hTT_SemiLep = cardf.Get("x_TT_SemiLep")
    nTT_SemiLep = hTT_SemiLep.Integral()
    nTTErr_SemiLep = hTT_SemiLep.GetBinError(1)

    hTT_FullHad = cardf.Get("x_TT_FullHad")
    nTT_FullHad = hTT_FullHad.Integral()
    nTTErr_FullHad = hTT_FullHad.GetBinError(1)

    nTT_SemiLep=nTT_SemiLep+nTT_FullHad
    nTTErr_SemiLep = math.sqrt(nTTErr_SemiLep*nTTErr_SemiLep + nTTErr_FullHad*nTTErr_FullHad)

    nTT = nTT_SemiLep + nTT_DiLep
    nTTErr = math.sqrt(nTTErr_SemiLep*nTTErr_SemiLep + nTTErr_DiLep*nTTErr_DiLep)

    hSingleT = cardf.Get("x_SingleT")
    nSingleT = hSingleT.Integral()
    nSingleTErr = hSingleT.GetBinError(1)

    hTTV = cardf.Get("x_TTV")
    nTTV = hTTV.Integral()
    nTTVErr = hTTV.GetBinError(1)

    hWJets = cardf.Get("x_WJets")
    nWJets = hWJets.Integral()
    nWJetsErr = hWJets.GetBinError(1)

    hQCD = cardf.Get("x_QCD")
    nQCD = hQCD.Integral()
    nQCDErr = hQCD.GetBinError(1)
    if QCDoff:
        nQCD = 0
        nQCDErr=0

    hDY = cardf.Get("x_DY")
    nDY = hDY.Integral()
    nDYErr = hDY.GetBinError(1)

    cardf.Close()

    binName=binName.replace('CR','')
    binName=binName.replace('SR','')

    return (binName,[nTT, nTTErr, nTT_SemiLep, nTTErr_SemiLep, nTT_DiLep, nTTErr_DiLep, nTT_FullHad, nTTErr_FullHad,nSingleT, nSingleTErr, nTTV, nTTVErr, nWJets,  nWJetsErr, nQCD, nQCDErr, nDY, nDYErr])

def makeTable(yieldDict, yieldDict2, format = "text", option = "CRSR"):
    tableAll ={}
    # sort by bin name
    ykeys = sorted(yieldDict.keys())
    #print 'KEYS', sorted(ykeys)

    if format == "text":

        # Print yields
        print 80*'#'
        print "Yields with zero selected"
        print "Bin: | TT | SingleT | TTV | WJets | QCD | DY | allbkg | sig"

        for bin in ykeys:#yieldDict:

            (nTT, nTTErr, nTT_SemiLep, nTTErr_SemiLep, nTT_DiLep, nTTErr_DiLep, nTT_FullHad, nTTErr_FullHad, nSingleT, nSingleTErr, nTTV, nTTVErr, nWJets,  nWJetsErr, nQCD, nQCDErr, nDY, nDYErr) = yieldDict[bin]
            (nTT2, nTTErr2, nTT_SemiLep2, nTTErr_SemiLep2, nTT_DiLep2, nTTErr_DiLep2, nTT_FullHad2, nTTErr_FullHad2, nSingleT2, nSingleTErr2, nTTV2, nTTVErr2, nWJets2,  nWJetsErr2, nQCD2, nQCDErr2, nDY2, nDYErr2) = yieldDict2[bin]
            
            allbkg = nTT + nSingleT + nTTV + nWJets + nQCD + nDY
            if allbkg > 0.5:
                print "%s:|%2.2f +/- %2.2f|%2.2f +/- %2.2f|%2.2f +/- %2.2f|%2.2f +/- %2.2f|%2.2f +/- %2.2f|%2.2f +/- %2.2f " % ( bin, nTT, nTTErr, nSingleT, nSingleTErr, nTTV, nTTVErr, nWJets,  nWJetsErr, nQCD, nQCDErr, nDY, nDYErr , allbkg1)
            else:
                print "%s:|%2.2f +/- %2.2f|%2.2f +/- %2.2f|%2.2f +/- %2.2f|%2.2f +/- %2.2f|%2.2f +/- %2.2f|%2.2f +/- %2.2f  COMBINE" % ( bin, nTT, nTTErr, nSingleT, nSingleTErr, nTTV, nTTVErr, nWJets,  nWJetsErr, nQCD, nQCDErr, nDY, nDYErr , allbkg)
#                print bin, "| | | | | | | %2.2f | %2.2f +/- %2.2f " % (allbkg, nSig,nSigErr)

    if format == "latex":
        print '%',80*'#'
        print '%Going to print out LaTeX tables'
        print '%',80*'#'

        nColumns = 11
        if option == "ratio":
            nColumns = 16
        if option == "CRSR":
            nColumns = 12

        print "\\begin{table}[!hbtp]"
        print "\\begin{center}"
        print "\\scriptsize"
        print "\\caption{}"
#        print "\\caption{Expected event yields for search bins as defined in Table~\\ref{tab:1b_sigreg_3fb}. The \\DF is adjusted for each \\ST bin.}"
        print "\\label{tab:qcdYieldsHTbin}"
        print "\\begin{tabular}{|l|"+(nColumns-1)*'c|'+"}"

        print "\\hline"
        if option == "ratio":
            print "Bin                 &  \multicolumn{ 1 } {c} {      TT (2l)   }  & \multicolumn{ 1 } {c} {      TT (rest)   } & \multicolumn{ 1 } {c} {      frac dilep SR  } & \multicolumn{ 1 } {c} {      frac semil SR  }  & \multicolumn{ 1 } {c} {      TT (2l)   } &  \multicolumn{ 1 } {c} {      TT (rest)    }  & \multicolumn{ 1 } {c} {      frac dilep CR   \
 }& \multicolumn{ 1 } {c} {      frac semil CR  } & \multicolumn{ 1 } {c} {      RCS   }\\\ "
        elif option == "CRSR":
            print "Bin                 &  \multicolumn{ 1 } {c} {      TT (2l) SR  }  & \multicolumn{ 1 } {c} {      TT (rest)SR   } & \multicolumn{ 1 } {c} {      Rest SR   } & \multicolumn{ 1 } {c} {    AllBkg SR }   &  \multicolumn{ 1 } {c} {      TT (2l) CR   }  & \multicolumn{ 1 } {c} {      TT (rest) CR   } & \multicolumn{ 1 } {c} {      Rest CR  } & \multicolumn{ 1 } {c} {    AllBkg CR} & \multicolumn{ 1 } {c} {      RCSall }\\\ "
        else:
            print "Bin                 &  \multicolumn{ 1 } {c} {      TT (2l)   }  & \multicolumn{ 1 } {c} {      TT (rest)   } & \multicolumn{ 1 } {c} {      Single top   } & \multicolumn{ 1 } {c} {      TTV    } & \multicolumn{ 1 } {c} {     WJets  } & \multicolumn{ 1 } {c} {   QCD } & \multicolumn{ 1 } {c} {      DY   } & \multicolumn{ 1 } {c} {    ALL BKG } \\\ "
        print "\\hline"
        print "\\hline"

        for bin in ykeys:#yieldDict:
            (nTT, nTTErr, nTT_SemiLep, nTTErr_SemiLep, nTT_DiLep, nTTErr_DiLep, nTT_FullHad, nTTErr_FullHad, nSingleT, nSingleTErr, nTTV, nTTVErr, nWJets,  nWJetsErr, nQCD, nQCDErr, nDY, nDYErr) = yieldDict[bin]
            (nTT2, nTTErr2, nTT_SemiLep2, nTTErr_SemiLep2, nTT_DiLep2, nTTErr_DiLep2, nTT_FullHad2, nTTErr_FullHad2, nSingleT2, nSingleTErr2, nTTV2, nTTVErr2, nWJets2,  nWJetsErr2, nQCD2, nQCDErr2, nDY2, nDYErr2) = yieldDict2[bin]
            
            allbkg = nTT + nSingleT + nTTV + nWJets + nQCD + nDY
            allbkgErr = math.sqrt(nTTErr*nTTErr + nSingleTErr*nSingleTErr +nTTVErr*nTTVErr+ nWJetsErr*nWJetsErr +nQCDErr*nQCDErr+nDYErr*nDYErr)

            allbkg2 = nTT2 + nSingleT2 + nTTV2 + nWJets2 + nQCD2 + nDY2
            allbkgErr2 = math.sqrt(nTTErr2*nTTErr2 + nSingleTErr2*nSingleTErr2 +nTTVErr2*nTTVErr2+ nWJetsErr2*nWJetsErr2 +nQCDErr2*nQCDErr2+nDYErr2*nDYErr2)

            allbkgNoTT = nSingleT + nTTV + nWJets + nQCD + nDY
            allbkgErrNoTT = math.sqrt(nSingleTErr*nSingleTErr +nTTVErr*nTTVErr+ nWJetsErr*nWJetsErr +nQCDErr*nQCDErr+nDYErr*nDYErr)

            allbkgNoTT2 = nSingleT2 + nTTV2 + nWJets2 + nQCD2 + nDY2
            allbkgErrNoTT2 = math.sqrt(nSingleTErr2*nSingleTErr2 +nTTVErr2*nTTVErr2+ nWJetsErr2*nWJetsErr2 +nQCDErr2*nQCDErr2+nDYErr2*nDYErr2)
            binName = bin
            bin = bin.replace('_', ' $;$ ')

            RCSall = 0
            if (allbkg2)>0:
                RCSall = (allbkg)/(allbkg2)
            if option == "CRSR":

                print "%s & %2.2f & %2.2f &%2.2f  & %2.2f  & %2.2f  & %2.2f  & %2.2f  & %2.2f & %2.4f  \\\ " % ( bin, nTT_DiLep,nTT_SemiLep, allbkgNoTT, allbkg, nTT_DiLep2,nTT_SemiLep2, allbkgNoTT2, allbkg2, RCSall)
                tableAll[binName] =[nTT_DiLep,nTT_SemiLep, allbkgNoTT, allbkg, nTT_DiLep2,nTT_SemiLep2, allbkgNoTT2, allbkg2, RCSall]
#            print "%s & %2.2f & %2.2f &%2.2f  & %2.2f  & %2.2f  & %2.2f  & %2.2f  & %2.2f  \\\ " % ( bin, nTT_DiLep,nTT_SemiLep, nSingleT,  nTTV, nWJets,  nQCD,  nDY, allbkgNoTT)
            RCS = 0
            if (nTT_SemiLep+nTT_DiLep)>0:
                RCS = (nTT_SemiLep+nTT_DiLep)/(nTT_SemiLep2+nTT_DiLep2)
            fSemilep = 0
            fDilep = 0
            fSemilep2 = 0
            fDilep2 = 0
            if nTT_SemiLep+nTT_DiLep >0 :
                fSemilep = nTT_SemiLep/(nTT_DiLep+nTT_SemiLep)
                fDilep = nTT_DiLep/(nTT_DiLep+nTT_SemiLep)
            if nTT_SemiLep2+nTT_DiLep2 >0 :
                fSemilep2 = nTT_SemiLep2/(nTT_DiLep2+nTT_SemiLep2)
                fDilep2 = nTT_DiLep2/(nTT_DiLep2+nTT_SemiLep2)
#            print "%s & %2.2f & %2.2f &%2.2f  & %2.2f &  %2.2f & %2.2f &%2.2f  & %2.2f & %2.4f\\\ " % ( bin, nTT_DiLep,nTT_SemiLep, fDilep, fSemilep, nTT_DiLep2,nTT_SemiLep2, fDilep2, fSemilep2, RCS)
#            print nTT, nTT_DiLep, nTT_SemiLep, nTT_FullHad
        print "\\hline"
        print "\end{tabular}"
        print"\\end{center}"

        print "\\end{table}"
        

    return tableAll 

def makeRCS(yieldDictSR, yieldDictCR):
    RCSval={}
    print "                                                          "
    print "bin | Nsignal +/- Err| NControl +/- Err |  RCS +/- Err| "
    
    ykeys = sorted(yieldDictSR.keys())
    for bin in ykeys:
        (nTTSR, nTTSRErr, nTTSR_SemiLep, nTTSRErr_SemiLep, nTTSR_DiLep, nTTSRErr_DiLep, nTTSR_FullHad, nTTSRErr_FullHad, nSingleTSR, nSingleTSRErr, nTTVSR, nTTVSRErr, nWJetsSR,  nWJetsSRErr, nQCDSR, nQCDSRErr, nDYSR, nDYSRErr) = yieldDictSR[bin]
        
        (nTTCR, nTTCRErr, nTTCR_SemiLep, nTTCRErr_SemiLep, nTTCR_DiLep, nTTCRErr_DiLep, nTTCR_FullHad, nTTCRErr_FullHad, nSingleTCR, nSingleTCRErr, nTTVCR, nTTVCRErr, nWJetsCR,  nWJetsCRErr, nQCDCR, nQCDCRErr, nDYCR, nDYCRErr) = yieldDictCR[bin]
        
        allBkgSR = nTTSR + nSingleTSR + nTTVSR + nWJetsSR + nQCDSR + nDYSR
        allBkgSRErr = math.sqrt(nTTSRErr*nTTSRErr + nSingleTSRErr*nSingleTSRErr +nTTVSRErr*nTTVSRErr+ nWJetsSRErr*nWJetsSRErr +nQCDSRErr*nQCDSRErr+nDYSRErr*nDYSRErr)
        
        allBkgCR = nTTCR + nSingleTCR + nTTVCR + nWJetsCR + nQCDCR + nDYCR
        allBkgCRErr = math.sqrt(nTTCRErr*nTTCRErr + nSingleTCRErr*nSingleTCRErr +nTTVCRErr*nTTVCRErr+ nWJetsCRErr*nWJetsCRErr +nDYCRErr*nDYCRErr) 
        
        RCS = allBkgSR/allBkgCR
        RCS_Err = RCS * math.sqrt(allBkgSRErr/allBkgSR*allBkgSRErr/allBkgSR + allBkgCRErr/allBkgCR*allBkgCRErr/allBkgCR)
        print "%s:|%2.2f +/- %2.2f | %2.2f +/- %2.2f |%2.4f +/- %2.4f" % ( bin, allBkgSR, allBkgSRErr,allBkgCR, allBkgCRErr, RCS, RCS_Err)

        RCSval[bin] = [RCS, RCS_Err] 

    return RCSval

binNameDict = {}
binNameDict['ST1'] = " [250, 350]"                                                                           
binNameDict['ST2'] = " [350, 450]"
binNameDict['ST3'] = " [450, 600]"                                                                              
binNameDict['ST4'] = " $\geq$ 600" 
binNameDict['ST34'] = " $\geq$ 450" 
binNameDict['1B'] = " $=$ 1 "
binNameDict['2B'] = " $=$ 2 "
binNameDict['3B'] = " $\geq$ 3 "
binNameDict['23B'] = " $\geq$ 2 "
binNameDict['123B'] = "$\geq$ 1 "
binNameDict['HT0'] = " [500, 750]"                                                            
binNameDict['HT01'] = " [500, 1250]"
binNameDict['HT1'] = " [750, 1250]"
binNameDict['HT2'] = " $\geq$ 1250"
binNameDict['HT12'] = " $\geq$ 750"
binNameDict['HT012'] = " $\geq$ 500"
def makeBinTable(binCounts , option = "kfac"):

    print '\\begin{table}[ht]'

    binNames = sorted(binCounts.keys())
    if "68" in binNames[0]:
        nJetSR = '6, 8'
    if "9I" in binNames[0]:
        nJetSR = '9, Inf'
    if "for6" in binNames[0]:
        nJetSR = '4, 5 for 6, 8'
    if "for9" in binNames[0]:
        nJetSR = '4, 5 for 9, Inf'

    if option == "kfac":
        print '\\begin{tabular}{|c|c|c|c|c|c|}'
        print '\\hline'
        print '\multicolumn{6}{|c|}{Number of jets: ',nJetSR,'} \\\ \\hline' 
        print ' $L_T$  & nB & $H_T$ & $RCS_{',nJetSR,'}$ $\pm$ stat. err. & $RCS_{4,5j}$ $\pm$ stat. err. & $\kappa$ $\pm$ stat. err. \\\ '
        print ' $[$GeV$]$  &  & $[$GeV$]$ & & &  \\\ '

    if option == "counts":
        print '\\tiny'
        print '\\begin{tabular}{|l|l|l|c|c|c|c|c|c|c|c|c|c|c|}'
        print '\\hline'
        print '\multicolumn{12}{|c|}{Number of jets: ',nJetSR,'} \\\ \\hline' 
        print '$L_T$ & nB & $H_T$                &    TT (2l) SR    &   TT (rest)SR    &     Rest SR    &     AllBkg SR    &     TT (2l) CR     &    TT (rest) CR    &   Rest CR   &    AllBkg CR &   RCSall \\\  '
        print '$[$GeV$]$ &  & $[$GeV$]$      &    & &  &    &   &  &  &  & \\\  '

    binsTable = []
    for binName in binNames:
        splitName=binName.split("_")
        B = splitName[0]
        ST = splitName[1]
        HT = splitName[3]
        splitName=[ST,B,HT,(binCounts[binName])]
        binsTable.append(splitName)

    binsTable= sorted(binsTable)
    for i,bin in enumerate(binsTable):
        ST = bin[0]
        ST0 = ""
        B = bin[1]
        B0 = ""
        HT = bin[2]
        HT0 = ""

        Bname=B.replace(B,binNameDict[B])
        STname = ST.replace(ST,binNameDict[ST])
        HTname =HT.replace(HT,binNameDict[HT])

        if i > 0:
            ST0=binsTable[i-1][0]
            B0=binsTable[i-1][1]
            HT0=binsTable[i-1][2]

        if option == "kfac":
            RCSSB = bin[3][0]
            RCSerrSB = bin[3][1]
            RCSSR = bin[3][2]
            RCSerrSR = bin[3][3]
            kappa = bin[3][4]
            kappaerr = bin[3][5]
        
            if ST != ST0:
                print '\\hline \\hline'
                print '\\cline{1-6} \multirow{1}{*}{',STname,'}&',Bname, '&', HTname, '&', ' %2.3f' % RCSSB, '$\pm$',' %2.3f' % RCSerrSB, ' &', ' %2.3f' % RCSSR, '$\pm$',' %2.3f' % RCSerrSR,'&',' %2.2f' % kappa, '$\pm$',' %2.2f' % kappaerr,' \\\ '
            if ST == ST0 and B!=B0:
                print '\\cline{2-6}' ,'&',Bname, '&', HTname, '&', ' %2.3f' % RCSSB, '$\pm$',' %2.3f' % RCSerrSB, ' &', ' %2.3f' % RCSSR, '$\pm$',' %2.3f' % RCSerrSR,'&',' %2.2f' % kappa, '$\pm$',' %2.2f' % kappaerr,' \\\ '
            elif ST==ST0 and B==B0:
                print ' &', '&', HTname, '&',  ' %2.3f' % RCSSB, '$\pm$',' %2.3f' % RCSerrSB, ' &', ' %2.3f' % RCSSR, '$\pm$',' %2.3f' % RCSerrSR,'&',' %2.2f' % kappa, '$\pm$',' %2.2f' % kappaerr,' \\\ '

        if option == "counts":

            nTT_DiLep = bin[3][0]
            nTT_SemiLep = bin[3][1]
            allbkgNoTT = bin[3][2]
            allbkg = bin[3][3]
            nTT_DiLep2 = bin[3][4]
            nTT_SemiLep2 = bin[3][5]
            allbkgNoTT2 = bin[3][6]
            allbkg2 = bin[3][7]
            RCSall= bin[3][8]

            if ST != ST0:
                print '\\hline \\hline'
                print '\\cline{1-12} \multirow{1}{*}{',STname,'}&',Bname, '&', HTname, '&', ' %2.2f' % nTT_DiLep, ' &', ' %2.2f' % nTT_SemiLep,'&',' %2.2f' % allbkgNoTT, '&',' %2.2f' % allbkg , '&',' %2.2f' % nTT_DiLep2, '&',' %2.2f' % nTT_SemiLep2, '&',' %2.2f' % allbkgNoTT2, '&',' %2.2f' % allbkg2, '&',' %2.4f' % RCSall, ' \\\ '
            if ST == ST0 and B!=B0:
                print '\\cline{2-12}' ,'&',Bname, '&', HTname, '&', ' %2.2f' % nTT_DiLep, ' &', ' %2.2f' % nTT_SemiLep,'&',' %2.2f' % allbkgNoTT, '&',' %2.2f' % allbkg , '&',' %2.2f' % nTT_DiLep2, '&',' %2.2f' % nTT_SemiLep2, '&',' %2.2f' % allbkgNoTT2, '&',' %2.2f' % allbkg2, '&',' %2.4f' % RCSall, ' \\\ '

            elif ST==ST0 and B==B0:
                print ' &', '&', HTname, '&', ' %2.2f' % nTT_DiLep, ' &', ' %2.2f' % nTT_SemiLep,'&',' %2.2f' % allbkgNoTT, '&',' %2.2f' % allbkg , '&',' %2.2f' % nTT_DiLep2, '&',' %2.2f' % nTT_SemiLep2, '&',' %2.2f' % allbkgNoTT2, '&',' %2.2f' % allbkg2, '&',' %2.4f' % RCSall, ' \\\ '


        


        

    print "\\hline"
    print "\end{tabular}"

    print "\\end{table}"
        
def makeKfactor(RCS_SB, RCS_SR):
    kfactor = {}
    #doesn't quite work
    #would need to add up bjet multiplicity doesn't quite work yet
    STbins = ['ST1','ST2','ST3','ST4','ST34']
    HTbins = ['HT0','HT1','HT2','HT01','HT12','HT012']
    Bbins = ['1B','3B']
    names_SB = sorted(RCS_SB.keys())
    names_SR =  sorted(RCS_SR.keys())

    for name_SR in names_SR:
        name_SR  = name_SR+'_'
        splitName=name_SR.split("_")
        B = splitName[0]
        if B == "2B" or B == "23B" or B == "3B":
            B = "23B"
        ST = splitName[1]
        HT = splitName[3]+'_'
        for name_SB in names_SB:
            if B in name_SB and ST in name_SB and HT in name_SB:
                #print name_SR,"!!!!!!!!!!!!1"
                name_SR =  name_SR[:-1]
                kappa = RCS_SR[name_SR][0]/RCS_SB[name_SB][0]
                kappaErr = kappa*math.sqrt((RCS_SR[name_SR][1]/RCS_SR[name_SR][0])*(RCS_SR[name_SR][1]/RCS_SR[name_SR][0])+(RCS_SB[name_SB][1]/RCS_SB[name_SB][0]*RCS_SB[name_SB][1]/RCS_SB[name_SB][0]))
                print "%s %s | %2.4f +/- %2.4f| %2.4f +/- %2.4f| %2.2f +/- %2.2f " %  ( name_SR, name_SB, RCS_SR[name_SR][0], RCS_SR[name_SR][1], RCS_SB[name_SB][0], RCS_SB[name_SB][1], kappa, kappaErr)        
                kfactor[name_SR] = [RCS_SR[name_SR][0], RCS_SR[name_SR][1],RCS_SB[name_SB][0],RCS_SB[name_SB][1],kappa, kappaErr] 
    return kfactor
# MAIN
if __name__ == "__main__":

    nJobs = 12

    # read f-ratios
    ratDict = {}
#    ratDict = readRatios()

    ## usage: python read.py cardDir textformat

    if len(sys.argv) > 1:
        cardDirectory = sys.argv[1]
    else:
        cardDirectory="yields/QCD_yields_3fb_test3"

    if len(sys.argv) > 2:
        pfmt = sys.argv[3]
    else:
        pfmt = "text"


    cardDirectory = os.path.abspath(cardDirectory)
    cardDirName = os.path.basename(cardDirectory)

    print 'Using cards from', cardDirName
    commondir = 'common'
    cardPattern = 'CnC2015X'

    limitdict = {}
    sigdict = {}


    #print 80*'#'
    #print "Yields for", QCDdir

    # get card file list
    inDir = cardDirectory+'/'+commondir
    cardFnames = glob.glob(inDir+'/'+ cardPattern + '_*.root')
    cardNames = [os.path.basename(name) for name in cardFnames]

    cardNames = [(name.replace(cardPattern+'_','')).replace('.input.root','') for name in cardNames]

    SB = '45j'
    cardNamesSR_SB_for6 = [name for name in cardNames if name.find('SR_' + SB) > 0 and ( name.find('for6') >0)]
    cardNamesCR_SB_for6 = [name for name in cardNames if name.find('CR_' + SB) > 0 and (name.find('for6') >0)]
    cardNamesSR_SB_for9 = [name for name in cardNames if name.find('SR_' + SB) > 0 and ( name.find('for9') >0)]
    cardNamesCR_SB_for9 = [name for name in cardNames if name.find('CR_' + SB) > 0 and (name.find('for9') >0)]

#    SB = '45j'
#    cardNamesSR_SB = [name for name in cardNames if name.find('SR_' + SB) > 0 and (name.find('a') <0 and name.find('012') <0)]
#    cardNamesCR_SB = [name for name in cardNames if name.find('CR_' + SB) > 0 and (name.find('a') <0 and name.find('012') <0)]

    SB = '45j'
    cardNamesSR_SBa = [name for name in cardNames if name.find('SR_' + SB) > 0 and (name.find('a') >0 or name.find('012') >0)]
    cardNamesCR_SBa = [name for name in cardNames if name.find('CR_' + SB) > 0 and (name.find('a') >0 or name.find('012') >0)]

    nj68 = '68j'
    cardNamesSR_nj68 = [name for name in cardNames if name.find('SR_' + nj68) > 0]
    cardNamesCR_nj68 = [name for name in cardNames if name.find('CR_' + nj68) > 0]

    nj9Inf = '9Infj'
    cardNamesSR_nj9Inf = [name for name in cardNames if name.find('SR_' + nj9Inf) > 0]
    cardNamesCR_nj9Inf = [name for name in cardNames if name.find('CR_' + nj9Inf) > 0]

    #for kappa determination
    cardNamesSR_K = [name for name in cardNames if name.find('SRK_6') > 0 or name.find('SRK_9') > 0]
    cardNamesCR_K = [name for name in cardNames if name.find('CRK_6') > 0 or name.find('CRK_9') > 0]


    cardNamesSR_SB_K = [name for name in cardNames if name.find('SRK_4') > 0]
    cardNamesCR_SB_K = [name for name in cardNames if name.find('CRK_4') > 0]


    argTupleSR_SB_for6 = [(commondir, cardDirectory, name, ratDict) for name in cardNamesSR_SB_for6]
    argTupleCR_SB_for6 = [(commondir, cardDirectory, name, ratDict) for name in cardNamesCR_SB_for6]
    pool = Pool(nJobs)
    yieldDictSR_SB_for6 = dict(pool.map(_getYieldsFromInput, argTupleSR_SB_for6))             
    yieldDictCR_SB_for6 = dict(pool.map(_getYieldsFromInput, argTupleCR_SB_for6))                   

    argTupleSR_SB_for9 = [(commondir, cardDirectory, name, ratDict) for name in cardNamesSR_SB_for9]
    argTupleCR_SB_for9 = [(commondir, cardDirectory, name, ratDict) for name in cardNamesCR_SB_for9]
    pool = Pool(nJobs)
    yieldDictSR_SB_for9 = dict(pool.map(_getYieldsFromInput, argTupleSR_SB_for9))             
    yieldDictCR_SB_for9 = dict(pool.map(_getYieldsFromInput, argTupleCR_SB_for9))                   

    argTupleSR_SBa = [(commondir, cardDirectory, name, ratDict) for name in cardNamesSR_SBa]
    argTupleCR_SBa = [(commondir, cardDirectory, name, ratDict) for name in cardNamesCR_SBa]
    pool = Pool(nJobs)
    yieldDictSR_SBa = dict(pool.map(_getYieldsFromInput, argTupleSR_SBa))             
    yieldDictCR_SBa = dict(pool.map(_getYieldsFromInput, argTupleCR_SBa))                   

    argTupleSR_nj68 = [(commondir, cardDirectory, name, ratDict) for name in cardNamesSR_nj68]
    argTupleCR_nj68 = [(commondir, cardDirectory, name, ratDict) for name in cardNamesCR_nj68]
    pool = Pool(nJobs)
    yieldDictSR_nj68 = dict(pool.map(_getYieldsFromInput, argTupleSR_nj68))             
    yieldDictCR_nj68 = dict(pool.map(_getYieldsFromInput, argTupleCR_nj68))                   

    argTupleSR_nj9Inf = [(commondir, cardDirectory, name, ratDict) for name in cardNamesSR_nj9Inf]
    argTupleCR_nj9Inf = [(commondir, cardDirectory, name, ratDict) for name in cardNamesCR_nj9Inf]
    pool = Pool(nJobs)
    yieldDictSR_nj9Inf = dict(pool.map(_getYieldsFromInput, argTupleSR_nj9Inf))             
    yieldDictCR_nj9Inf = dict(pool.map(_getYieldsFromInput, argTupleCR_nj9Inf))                   

    argTupleSR_K = [(commondir, cardDirectory, name, ratDict) for name in cardNamesSR_K]
    argTupleCR_K = [(commondir, cardDirectory, name, ratDict) for name in cardNamesCR_K]
    pool = Pool(nJobs)
    yieldDictSR_K = dict(pool.map(_getYieldsFromInput, argTupleSR_K))             
    yieldDictCR_K = dict(pool.map(_getYieldsFromInput, argTupleCR_K))                   

    argTupleSR_SB_K = [(commondir, cardDirectory, name, ratDict) for name in cardNamesSR_SB_K]
    argTupleCR_SB_K = [(commondir, cardDirectory, name, ratDict) for name in cardNamesCR_SB_K]
    pool = Pool(nJobs)
    yieldDictSR_SB_K = dict(pool.map(_getYieldsFromInput, argTupleSR_SB_K))             
    yieldDictCR_SB_K = dict(pool.map(_getYieldsFromInput, argTupleCR_SB_K))                   

                            

    RCS_SB_for6 = makeRCS(yieldDictSR_SB_for6,yieldDictCR_SB_for6)
    RCS_SB_for9 = makeRCS(yieldDictSR_SB_for9,yieldDictCR_SB_for9)
    RCS_nj68 = makeRCS(yieldDictSR_nj68,yieldDictCR_nj68)
    RCS_nj9Inf = makeRCS(yieldDictSR_nj9Inf,yieldDictCR_nj9Inf)

    RCS_K = makeRCS(yieldDictSR_K,yieldDictCR_K)
    RCS_SB_K = makeRCS(yieldDictSR_SB_K,yieldDictCR_SB_K)


    table45_for6 = makeTable(yieldDictSR_SB_for6,yieldDictCR_SB_for6,"latex")
    table45_for9 = makeTable(yieldDictSR_SB_for9,yieldDictCR_SB_for9,"latex")
#    makeTable(yieldDictSR_SBa,yieldDictCR_SBa,"latex")
#    makeTable(yieldDictSR_K,yieldDictCR_K,"latex")
    table68 = makeTable(yieldDictSR_nj68,yieldDictCR_nj68,"latex")
    table9Inf = makeTable(yieldDictSR_nj9Inf,yieldDictCR_nj9Inf,"latex")



#    printRCSfunction(RCS_SB_for6)

    
    kfactor68=    makeKfactor(RCS_SB_for6, RCS_nj68)
    kfactor9Inf=makeKfactor(RCS_SB_for9, RCS_nj9Inf)
#    makeBinTable(RCS_nj9Inf)
#    makeBiTable(RCS_nj68)

    makeBinTable(table45_for6,"counts")
    makeBinTable(table45_for9,"counts")

    makeBinTable(table68,"counts")
    makeBinTable(table9Inf,"counts")

    makeBinTable(kfactor68,"kfac")
    makeBinTable(kfactor9Inf,"kfac")


#    makeKfactor(RCS_nj68, RCS_SB_for6)
