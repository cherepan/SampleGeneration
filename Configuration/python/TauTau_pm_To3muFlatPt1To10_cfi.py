import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.Pythia8CUEP8M1Settings_cfi import *

generator = cms.EDFilter("Pythia8PtGun",
    PGunParameters = cms.PSet(
        MaxPt = cms.double(10.0),
        MinPt = cms.double(1.0),
        ParticleID = cms.vint32(-15), ## one tau : tau+ in endcap+
        MinEta = cms.double(1.0),
        MaxEta = cms.double(3.5),
        AddAntiParticle = cms.bool(True),
        MinPhi = cms.double(-3.14159265359),
        MaxPhi = cms.double(3.14159265359),
    ),
    psethack = cms.string('tau to 3 mu gun with pt flat 1 to 10 GeV'),
    firstRun = cms.untracked.uint32(1),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CUEP8M1SettingsBlock,
        processParameters = cms.vstring(
            'SoftQCD:nonDiffractive = on',
            'SoftQCD:singleDiffractive = on',
            'SoftQCD:doubleDiffractive = on',
            '431:onMode = off',
            '431:onIfAny = 15',
            '15:addChannel = on .01 0 13 13 -13',
            '15:onMode = off',
            '15:onIfMatch = 13 13 13',
          ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
            'pythia8CUEP8M1Settings',
            'processParameters'
        )
    )
)

ProductionFilterSequence = cms.Sequence(generator)