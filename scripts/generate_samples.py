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
tot_jobs = 50
events_per_job = 1000

# gen_fragment = 'MuMuFlatOneOverPt2To2000_cfi.py'
# generation_tag = 'MuMu_2to2000_flatOneOverPt_8Mar2018' ## the folder where to store the stuff

# gen_fragment = 'SingleMuPt100_endcap_pythia8_cfi.py'
# generation_tag = 'SingleMuPt100_endcap_11Mar2018' ## the folder where to store the stuff

gen_fragment = 'bbgun_BjetToMu_endcap_neg_pythia8_cfi.py'
generation_tag = 'PROVA' ## the folder where to store the stuff

out_LFN_base = '/store/group/l1upgrades/L1MuTrks'
seed_offset = 0 ## to change for extended samples. NOTE: it must be larger than njobs in the previous production!

filename_proto     = 'MuMu_FEVTDEBUGHLT_{0}.root'
gen_cfg_name_proto = 'gen_cfg_{0}.py'

########################################################################################################


## a long command, on multiple lines
## remember to leave a space at the end of each line to correctly separate the different chunks!
## MuMuFlatOneOverPt2To2000_cfi.py

##### Set of commnands for production in 9_3_5
# command_proto = (
#     'cmsDriver.py '
#     '%s -n %i '
#     '--mc '
#     '--eventcontent FEVTDEBUGHLT '
#     '--datatier GEN-SIM-DIGI-RAW '
#     '--conditions 93X_upgrade2023_realistic_v5 '
#     '--beamspot HLLHC14TeV '
#     '--step GEN,SIM,DIGI:pdigi_valid,L1,L1TrackTrigger,DIGI2RAW,HLT:@fake2 '
#     '--nThreads 8 '
#     '--geometry Extended2023D17 '
#     '--era Phase2_timing  '
#     '--fileout {0} '
#     '--python_filename {1} '
#     '--customise_commands "process.RandomNumberGeneratorService.generator.initialSeed = {2} ; process.RandomNumberGeneratorService.VtxSmeared.initialSeed = {3}" ' ## sadly, CMSSW cmd line opts..
# ) % (gen_fragment, events_per_job)

##### Set of commnands for production in 9_3_7
## note: to produce mu in jets filters are applied --> need to specify output number of events
## this cannot control exactly the number of events, so if you need to produce something that has no filter, better just use -n <num_evts>
command_proto = (
    'cmsDriver.py '
    '%s -o %i -n -1 '
    '--mc '
    '--eventcontent FEVTDEBUGHLT '
    '--datatier GEN-SIM-DIGI-RAW '
    '--conditions 93X_upgrade2023_realistic_v5 '
    '--beamspot HLLHC14TeV '
    '--step GEN,SIM,DIGI:pdigi_valid,L1,L1TrackTrigger,DIGI2RAW,HLT:@fake2 '
    '--nThreads 8 '
    '--geometry Extended2023D17 '
    '--era Phase2_timing  '
    '--fileout {0} '
    '--python_filename {1} '
    '--customise_commands "process.RandomNumberGeneratorService.generator.initialSeed = {2} ; process.RandomNumberGeneratorService.VtxSmeared.initialSeed = {3}" ' ## sadly, CMSSW cmd line opts..
    '--customise=SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000 '
) % (gen_fragment, events_per_job)

########################################################################################################

#########################
## folder for stuff
os.system('mkdir ' + generation_tag)

#########################
## CMSSW stuff

cmssw_base    = os.environ['CMSSW_BASE']
cmssw_version = os.environ['CMSSW_VERSION']
scram_arch    = os.environ['SCRAM_ARCH']
print '** INFO: CMSSW located in: ', cmssw_base

tarName      = '%s_tar.tgz' % cmssw_version
cmsswWorkDir = os.path.abspath(os.path.join(cmssw_base, '..'))
tarLFN       = cmsswWorkDir + '/' + tarName

#########################
## tar CMSSW for condor
toExclude = [
    '{0}/src/MuMu_2to2000_flatOneOverPt_8Mar2018',
    '{0}/src/MuMu_2to500_flatPt_8Mar2018',
    '{0}/src/SingleMuPt50_endcap_11Mar2018',
    '{0}/src/SingleMuPt75_endcap_11Mar2018',
    '{0}/src/{1}'.format(cmssw_version, generation_tag),
    '{0}/src/.git'.format(cmssw_version),
]

# command = 'tar --exclude="{0}" --exclude="{1}" -zcf {2} -C {3} {4}'.format(excludePath, excludePath2, tarLFN, cmsswWorkDir, cmssw_version)
command = 'tar'
for te in toExclude:
    command += ' --exclude="{0}"'.format(te)
command += ' -zcf {0} -C {1} {2}'.format(tarLFN, cmsswWorkDir, cmssw_version)

print '** INFO: Going to tar CMSSW folder into', tarName
print "** INFO: executing:", command
os.system(command)
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
os.system(command)
print "** INFO: executing:", command

for ijob in range(0, tot_jobs):
    filename     = filename_proto.format(ijob)
    gen_cfg_name = gen_cfg_name_proto.format(ijob)
    rnd_seed = 100*(ijob + seed_offset) ## in multithread mpde it is possible that this increases the seed as seed+0, seed+1, .., seed+N for N in number of threads,
    ## for safety I will have a seed split between each job that is larger that the number of threads
    outputEOSName  = '%s/output/%s' % (baseEOSout, filename)

    command = command_proto.format(filename, gen_cfg_name, rnd_seed, rnd_seed+25)
    
    outScriptName  = outScriptNameProto.format(ijob)
    outScript      = open(outScriptName, 'w')
    writeln(outScript, '#!/bin/bash')
    writeln(outScript, '{') ## start of redirection..., keep stderr and stdout in a single file, it's easier
    writeln(outScript, 'echo "... starting job on " `date` #Date/time of start of job')
    writeln(outScript, 'echo "... running on: `uname -a`" #Condor job is running on this node')
    writeln(outScript, 'echo "... system software: `cat /etc/redhat-release`" #Operating System on that node')
    writeln(outScript, 'source /cvmfs/cms.cern.ch/cmsset_default.sh')
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
    writeln(outScript, "echo '%s'" % command) ## ah, the quotes...
    writeln(outScript, "%s" % command)
    writeln(outScript, 'echo "... cmsRun finished with status $?"')
    writeln(outScript, 'echo "... copying output file %s to EOS in %s"' % (filename, outputEOSName))
    writeln(outScript, 'xrdcp -s %s %s' % (filename, outputEOSName)) ## no not force overwrite output in destination
    writeln(outScript, 'echo "... copy done with status $?"')
    # writeln(outScript, 'remove the input and output files if you dont want it automatically transferred when the job ends')
    # writeln(outScript, 'rm nameOfOutputFile.root')
    # writeln(outScript, 'rm Filename1.root')
    # writeln(outScript, 'rm Filename2.root')
    writeln(outScript, 'cd ${_CONDOR_SCRATCH_DIR}')
    writeln(outScript, 'rm -rf %s' % cmssw_version)
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
    # os.system(command)