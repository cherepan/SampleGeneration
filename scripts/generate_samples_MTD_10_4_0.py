import os
import sys

def writeln(f, line):
    f.write(line + '\n')

#######################################################################################################

# ###### mu+mu- guns in pt / 1overpt
# tot_jobs = 500
# events_per_job = 1000

# # gen_fragment = 'MuMuFlatOneOverPt2To2000_cfi.py'
# # generation_tag = 'MuMu_2to2000_flatOneOverPt_8Mar2018' ## the folder where to store the stuff
# gen_fragment = 'MuMuFlatPt2To500_cfi.py'
# generation_tag = 'MuMu_2to500_flatPt_8Mar2018' ## the folder where to store the stuff
# out_LFN_base = '/store/group/l1upgrades/L1MuTrks'
# seed_offset = 511 ## to change for extended samples. NOTE: it must be larger than njobs in the previous production!



###### mu+mu- guns in at fixed pT
# tot_jobs = 5000
# events_per_job = 1000

tot_jobs = 250
events_per_job = 10000

# gen_fragment = 'MuMuFlatOneOverPt2To2000_cfi.py'
# generation_tag = 'MuMu_2to2000_flatOneOverPt_8Mar2018' ## the folder where to store the stuff

# gen_fragment = 'SingleMuPt100_endcap_pythia8_cfi.py'
# generation_tag = 'SingleMuPt100_endcap_11Mar2018' ## the folder where to store the stuff

# gen_fragment = 'bbgun_BjetToMu_endcap_neg_pythia8_cfi.py'
# generation_tag = 'PROVA' ## the folder where to store the stuff

###### tau -> 3mu
# gen_fragment = 'Ds_to_Tau3Mu_pythia8_14TeV_cfi.py'
# generation_tag = 'Ds_to_Tau3Mu_pythia8_5Apr2019_5MEvts' ## the folder where to store the stuff

# gen_fragment = 'TauTau_mp_To3muFlatPt1To10_cfi.py'
# generation_tag = 'TauTau_mp_To3muFlatPt1To10_6Apr2019_2p5MEvts' ## the folder where to store the stuff

gen_fragment = 'TauTau_pm_To3muFlatPt1To10_cfi.py'
generation_tag = 'TauTau_pm_To3muFlatPt1To10_6Apr2019_2p5MEvts' ## the folder where to store the stuff


out_LFN_base = '/store/group/l1upgrades/L1MuTrks'
# seed_offset = 1 ## to change for extended samples. NOTE: it must be larger than njobs in the previous production!
seed_offset = 301 ## to change for extended samples. NOTE: it must be larger than njobs in the previous production!
## NOTE : seed_offset = 0 also causes problems with GEANT in the _mtd1 release... bah

filename_proto     = 'Tau3Mu_{0}.root'
# gen_cfg_name_proto = 'gen_cfg_{0}.py'

gensim_name = 'gensim.root'

#### debug options - True for a normal execution of the job
do_tar   = True
do_xrdcp = True
launch   = True

# ########################################################################################################

#########################
## CMSSW stuff

cmssw_base    = os.environ['CMSSW_BASE']
cmssw_version = os.environ['CMSSW_VERSION']
scram_arch    = os.environ['SCRAM_ARCH']
cmssw_v_mtd5  = 'CMSSW_10_4_0_mtd5'

print '** INFO: CMSSW located in: ', cmssw_base

tarName      = '%s_tar.tgz' % cmssw_version
cmsswWorkDir = os.path.abspath(os.path.join(cmssw_base, '..'))
tarLFN       = cmsswWorkDir + '/' + tarName

# ########################################################################################################

## a long command, on multiple lines
## remember to leave a space at the end of each line to correctly separate the different chunks!
## MuMuFlatOneOverPt2To2000_cfi.py

## note: to produce mu in jets filters are applied --> need to specify output number of events
## this cannot control exactly the number of events, so if you need to produce something that has no filter, better just use -n <num_evts>

## to execute in 10_0_4_mtd1 with my custom gen frament
command_proto_gensim = (
    'cmsDriver.py '
    '%s -o %i -n -1 '
    '--mc '
    '--eventcontent RAWSIM '
    '--datatier GEN-SIM '
    '--conditions 103X_upgrade2023_realistic_v2 '
    '--beamspot HLLHC14TeV '
    '--step GEN,SIM '
    '--geometry Extended2023D35 '
    '--era Phase2C4_timing_layer_new ' ## NOTE: this era is available in CMSSW_10_4_0_mtd1 but not in _mtd5. Moving to another era since it should not impact the GEN-SIM (sure for SIM ??)
    # '--era Phase2C4_timing_layer_bar '
    '--fileout file:%s ' ## save it to the scratch area
    '--python_filename gensimstep_cfg.py '
    '--customise_commands "process.RandomNumberGeneratorService.generator.initialSeed = {genSeed} ; process.RandomNumberGeneratorService.VtxSmeared.initialSeed = {vtxSeed}" ' ## sadly, CMSSW cmd line opts..
    '--customise Configuration/DataProcessing/Utils.addMonitoring '
) % (gen_fragment, events_per_job, gensim_name)

## to execute in a plain 10_0_4_mtd5
command_proto_step1 = (
    'cmsDriver.py step1 '
    '-n -1 '
    '--filein "file:../../%s/src/%s" ' ## read it from the scratch area of the other release
    '--fileout file:step1.root '
    '--mc '
    '--eventcontent FEVTDEBUGHLT '
    '--pileup NoPileUp '
    '--datatier GEN-SIM-DIGI-RAW '
    '--conditions 103X_upgrade2023_realistic_v2 '
    '--step DIGI:pdigi_valid,L1,L1TrackTrigger,DIGI2RAW,HLT:@fake2 '
    '--nThreads 8 '
    '--geometry Extended2023D35 '
    '--era Phase2C4_timing_layer_bar '
    '--python_filename step1_cfg.py '
    '--customise Configuration/DataProcessing/Utils.addMonitoring '
) % (cmssw_version, gensim_name)

command_proto_step2 = (
    'cmsDriver.py step2 '
    '-n -1 '
    '--filein file:step1.root '
    '--fileout file:{outputFile} '
    '--mc '
    '--eventcontent FEVTDEBUGHLT '
    '--runUnscheduled '
    '--outputCommand \'keep *_mtdUncalibratedRecHits_*_*\',\'keep *_mtdRecHits_*_*\' '
    '--datatier FEVT '
    '--conditions 103X_upgrade2023_realistic_v2 '
    '--customise_commands \'process.Timing = cms.Service("Timing",  summaryOnly = cms.untracked.bool(False),  useJobReport = cms.untracked.bool(True) )\' '
    '--step RAW2DIGI,L1Reco,RECO '
    '--nThreads 8 '
    '--geometry Extended2023D35 '
    '--era Phase2C4_timing_layer_bar '
    '--python_filename step2_cfg.py '
    '--customise Configuration/DataProcessing/Utils.addMonitoring '
)

# print command_proto_gensim
# print ''
# print command_proto_step1
# print ''
# print command_proto_step2

# command_parts = [
#     'echo \"... starting GEN-SIM\"', command_proto_gensim,
#     'echo \"... starting step 1\"', command_proto_step1,
#     'echo \"... starting step 2\"', command_proto_step2,
# ]

command_parts_MTD1 = [
    'echo \"... starting GEN-SIM\"', command_proto_gensim,
]

command_parts_MTD5 = [
    'echo \"... starting step 1\"', command_proto_step1,
    'echo \"... starting step 2\"', command_proto_step2,
]

# command_proto = '\n'.join(command_parts)
# print command_proto

########################################################################################################

#########################
## folder for stuff
os.system('mkdir ' + generation_tag)

#########################
## tar CMSSW for condor
toExclude = [
    '{0}/src/MuMu_2to2000_flatOneOverPt_8Mar2018',
    '{0}/src/MuMu_2to500_flatPt_8Mar2018',
    '{0}/src/SingleMuPt50_endcap_11Mar2018',
    '{0}/src/SingleMuPt75_endcap_11Mar2018',
    '{0}/src/{1}'.format(cmssw_version, generation_tag),
    '{0}/src/.git'.format(cmssw_version),
    '{0}/src/Ds_to_Tau3Mu_pythia8_5Apr2019_5MEvts'.format(cmssw_version),
    '{0}/src/Ds_to_Tau3Mu_pythia8_5Apr2019'.format(cmssw_version),
    '{0}/src/TauTau_mp_To3muFlatPt1To10_6Apr2019_2p5MEvts'.format(cmssw_version),
]

# command = 'tar --exclude="{0}" --exclude="{1}" -zcf {2} -C {3} {4}'.format(excludePath, excludePath2, tarLFN, cmsswWorkDir, cmssw_version)
command = 'tar'
for te in toExclude:
    command += ' --exclude="{0}"'.format(te)
command += ' -zcf {0} -C {1} {2}'.format(tarLFN, cmsswWorkDir, cmssw_version)

print '** INFO: Going to tar CMSSW folder into', tarName
print "** INFO: executing:", command
if do_tar: os.system(command)
else: print " >>> DEBUG: skipping tar"
print '** INFO: tar finished and saved in:', tarLFN

#########################
## ship CMSSW to EOS
xroootdServ    = 'root://cmsxrootd.fnal.gov/'
baseEOSout     = 'root://cmseos.fnal.gov/{0}/{1}'.format(out_LFN_base, generation_tag)
tarEOSdestLFN  = baseEOSout + '/CMSSW_tar'
outScriptNameBareProto = 'job_{0}.sh'
outScriptNameProto     = (generation_tag + '/' + outScriptNameBareProto)

command = 'eos root://cmseos.fnal.gov mkdir -p %s' % tarEOSdestLFN.replace('root://cmseos.fnal.gov/', '/eos/uscms')
tarEOSdestLFN += ('/' + tarName)
print "** INFO: copying CMSSW tarball to:", tarEOSdestLFN
command = 'xrdcp -f -s %s %s' % (tarLFN, tarEOSdestLFN)
if do_xrdcp: os.system(command)
else: print " >>> DEBUG: skipping xrdcp"
print "** INFO: executing:", command

for ijob in range(0, tot_jobs):
    filename     = filename_proto.format(ijob)
    # gen_cfg_name = gen_cfg_name_proto.format(ijob)
    rnd_seed = 100*(ijob + seed_offset) ## in multithread mpde it is possible that this increases the seed as seed+0, seed+1, .., seed+N for N in number of threads,
    ## for safety I will have a seed split between each job that is larger that the number of threads
    outputEOSName  = '%s/output/%s' % (baseEOSout, filename)

    # command = command_proto.format(filename, gen_cfg_name, rnd_seed, rnd_seed+25)
    # command = command_proto.format(outputFile=filename, genSeed=rnd_seed, vtxSeed=rnd_seed+25)
    
    outScriptName  = outScriptNameProto.format(ijob)
    outScript      = open(outScriptName, 'w')
    writeln(outScript, '#!/bin/bash')
    writeln(outScript, '{') ## start of redirection..., keep stderr and stdout in a single file, it's easier
    writeln(outScript, 'echo "... starting job on " `date` #Date/time of start of job')
    writeln(outScript, 'echo "... running on: `uname -a`" #Condor job is running on this node')
    writeln(outScript, 'echo "... system software: `cat /etc/redhat-release`" #Operating System on that node')
    writeln(outScript, 'source /cvmfs/cms.cern.ch/cmsset_default.sh')

    #### PART 1 : GEN-SIM : to do in MTD1, with my custom GEN fragment
    writeln(outScript, 'echo "... DOING PART 1 - GEN-SIM"')
    writeln(outScript, 'echo "... retrieving CMSSW tarball"')
    writeln(outScript, 'xrdcp -f -s %s .' % tarEOSdestLFN) ## force overwrite CMSSW tar
    writeln(outScript, 'echo "... uncompressing CMSSW tarball"')
    writeln(outScript, 'tar -xzf %s' % tarName)
    writeln(outScript, 'rm %s' % tarName)
    writeln(outScript, 'export SCRAM_ARCH=%s' % scram_arch)
    writeln(outScript, 'cd %s/src/' % cmssw_version)
    writeln(outScript, 'scramv1 b ProjectRename')
    writeln(outScript, 'eval `scramv1 runtime -sh`')
    writeln(outScript, 'echo "... starting CMSSW run"')
    # writeln(outScript, "echo '%s'" % command) ## ah, the quotes...
    # writeln(outScript, "%s" % command)
    for cp_proto in command_parts_MTD1:
        cp = cp_proto.format(outputFile=filename, genSeed=rnd_seed, vtxSeed=rnd_seed+25)
        # writeln(outScript, "echo '%s'" % cp.replace("'", "\\'").replace('"', '\\"')) ## ah, the quotes... ### >> removed since it messes up with quptes. Fuck bash
        writeln(outScript, "%s" % cp)
    writeln(outScript, 'echo "... cmsRun - GENSIM - finished with status $?"')
    
    #### PART 2 : DIGI-RAW : to do in MTD5, plain release
    writeln(outScript, 'echo "... DOING PART 2 - DIGI-RAW"')
    writeln(outScript, 'cd ${_CONDOR_SCRATCH_DIR}')
    writeln(outScript, 'scramv1 project CMSSW %s' % cmssw_v_mtd5)
    writeln(outScript, 'cd %s/src' % cmssw_v_mtd5)
    writeln(outScript, 'eval `scramv1 runtime -sh`')
    for cp_proto in command_parts_MTD5:
        cp = cp_proto.format(outputFile=filename, genSeed=rnd_seed, vtxSeed=rnd_seed+25)
        # writeln(outScript, "echo '%s'" % cp.replace("'", "\\'").replace('"', '\\"')) ## ah, the quotes... ### >> removed since it messes up with quptes. Fuck bash
        writeln(outScript, "%s" % cp)
        # writeln(outScript, 'echo "... cmsRun finished with status $?"')
        if 'cmsDriver' in cp:
            if 'step1' in cp and not 'step2' in cp: ## the step1
                writeln(outScript, 'echo "... cmsRun - step1 - finished with status $?"')
            elif 'step1' in cp and 'step2' in cp: ## step2 has both keywords - from input file
                writeln(outScript, 'echo "... cmsRun - step2 - finished with status $?"')
            else:
                writeln(outScript, 'echo "... cmsRun - another step - finished with status $?"')

    #### PART 3 : stageout and cleaning
    writeln(outScript, 'echo "... copying output file %s to EOS in %s"' % (filename, outputEOSName))
    writeln(outScript, 'xrdcp -s %s %s' % (filename, outputEOSName)) ## no not force overwrite output in destination
    writeln(outScript, 'echo "... copy done with status $?"')
    # writeln(outScript, 'remove the input and output files if you dont want it automatically transferred when the job ends')
    # writeln(outScript, 'rm nameOfOutputFile.root')
    # writeln(outScript, 'rm Filename1.root')
    # writeln(outScript, 'rm Filename2.root')
    writeln(outScript, 'cd ${_CONDOR_SCRATCH_DIR}')
    writeln(outScript, 'echo "... listing the dir content"')
    writeln(outScript, 'ls')
    writeln(outScript, 'rm -rf %s' % cmssw_version) ## remove my gen-sim area
    writeln(outScript, 'rm -rf %s' % cmssw_v_mtd5)  ## remove my digi-reco area
    writeln(outScript, 'rm -rf %s' % gensim_name)   ## remove the gensim file
    writeln(outScript, 'echo "... job finished with status $?"')
    writeln(outScript, 'echo "... finished job on " `date`')
    writeln(outScript, 'echo "... exiting script"')
    writeln(outScript, '} 2>&1') ## end of redirection
    outScript.close()

print "** INFO: ready to submit the jobs"
## set directory to job directory, so that logs will be saved there
os.chdir(generation_tag)
for n in range(0, tot_jobs):
    command = "../SampleGeneration/scripts/t3submit %s" % outScriptNameBareProto.format(n)
    print "** INFO: submit job with command", command
    if launch: os.system(command)
    else: print " >>> DEBUG: skipping launch of jobs"
