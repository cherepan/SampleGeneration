import FWCore.ParameterSet.Config as cms


generator = cms.EDFilter("Pythia8PtGun",
                         PGunParameters = cms.PSet(
        MaxPt = cms.double(500.0),
        MinPt = cms.double(15.0),
        ParticleID = cms.vint32(5),
        AddAntiParticle = cms.bool(True),
        MaxEta = cms.double(2.7),
        MaxPhi = cms.double(3.14159265359),
        MinEta = cms.double(1.0),
        MinPhi = cms.double(-3.14159265359) ## in radians
        ),
                         Verbosity = cms.untracked.int32(0), ## set to 1 (or greater)  for printouts
                         psethack = cms.string('bb gun pt 15 500'),
                         firstRun = cms.untracked.uint32(1),
                         PythiaParameters = cms.PSet(parameterSets = cms.vstring())
                         )

MuMuFilter = cms.EDFilter("MCParticlePairFilter",
                          Status = cms.untracked.vint32(1, 1),
                          MinPt = cms.untracked.vdouble(2., 2.),
                          MinP  = cms.untracked.vdouble(0., 0.),
                          MinEta = cms.untracked.vdouble(1.2, -2.5),
                          MaxEta = cms.untracked.vdouble(2.5, -1.2),
                          ParticleCharge = cms.untracked.int32(0),
                          ParticleID1 = cms.untracked.vint32(13),
                          ParticleID2 = cms.untracked.vint32(13),
                          )

ProductionFilterSequence = cms.Sequence(generator*MuMuFilter)
