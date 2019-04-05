# SampleGeneration

### Install

For the 937 samples (PhaseIIFall17):
```
cmsrel CMSSW_9_3_7
cd CMSSW_9_3_7/src/
cmsenv
git cms-addpkg Configuration/Generator
git clone https://github.com/l-cadamuro/SampleGeneration
scram b -j 8
```

For the MTD PhaseII samples (CMSSW_10_4_0_mtd5)
```
cmsrel CMSSW_10_4_0_mtd5
cd CMSSW_10_4_0_mtd5/src
cmsenv
git cms-addpkg Configuration/Generator
git clone https://github.com/l-cadamuro/SampleGeneration
scram b -j 8
```

Remember to copy the user fragments from `SampleGeneration/Configuration/python` to `Configuration/Generator/python`

### Running the L1T generation GEN-SIM-RAW-DIGI

We are running a mu+mu- gun in the endcaps, flat in 1/pt: MuMuFlatOneOverPt2To2000_cfi.py   
Jobs are submitted to condor.   
The relevant parameter are configured at the top of SampleGeneration/scripts/generate_samples.py   
Note that you might have to create the folder that is set in out_LFN_base  
Also note that the t3submit has been customised to get 8 CPUs and 8 Gb of memory

```
cp SampleGeneration/Configuration/python/MuMuFlatOneOverPt2To2000_cfi.py Configuration/Generator/python/
python SampleGeneration/scripts/generate_samples.py

```

The Particle Gun code and Configurations have been made by Jia Fu and are taken from [here](https://github.com/jiafulow/L1TMuonSimulationsMar2017)
