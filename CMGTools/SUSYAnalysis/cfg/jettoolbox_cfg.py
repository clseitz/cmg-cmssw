import FWCore.ParameterSet.Config as cms

process = cms.Process('jetToolbox')

process.load("Configuration.EventContent.EventContent_cff")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.GlobalTag.globaltag = 'MCRUN2_74_V7'

process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 10
process.MessageLogger.suppressWarning = cms.untracked.vstring('ecalLaserCorrFilter','manystripclus53X','toomanystripclus53X')
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
process.options.allowUnscheduled = cms.untracked.bool(True)

from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox
jetToolbox( process, 'ak4', 'ak4JetSubs', 'out', addQGTagger=True, PUMethod='CHS', addPUJetID=True, addPruning=True, addSoftDrop=True, addNsub=True, maxTau=3, addTrimming=True, addFiltering=True )

process.endpath = cms.EndPath(process.out)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )
process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring('file:/nfs/dust/cms/group/susy-desy/Run2/MC/MiniAOD/RunIISpring15DR74/FromGiovanni/T1tttt_mGo1500_mChi100/T1tttt_mGo1500_mChi100.MINIAODSIM01.root'
                                                              )
                            )
