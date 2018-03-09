import FWCore.ParameterSet.Config as cms

# reference: https://github.com/cms-sw/genproductions/blob/master/python/EightTeV/SingleMuMinusFlatPt0p2To100_cff.py
generator = cms.EDProducer("FlatRandomPtGunProducer2",
    PGunParameters = cms.PSet(
        MaxPt = cms.double(2000.0),
        MinPt = cms.double(2.0),
        PartID = cms.vint32(-13),
        MinEta = cms.double(1.2),
        MaxEta = cms.double(2.5),
        MinPhi = cms.double(-3.14159265359),
        MaxPhi = cms.double(3.14159265359),
        RandomCharge = cms.bool(True),
        PtSpectrum = cms.string('flatOneOverPt'),
    ),
    Verbosity = cms.untracked.int32(0),
    psethack = cms.string('mu+ mu- pt 2 to 2000 flat in 1/pt'),
    AddAntiParticle = cms.bool(True),
    firstRun = cms.untracked.uint32(1)
)
