import ROOT
import subprocess
from DataFormats.FWLite import Events, Handle
from array import array
import sys

def copyToTLV(dest, source):
    dest.SetPxPyPzE(
        source.Px(),
        source.Py(),
        source.Pz(),
        source.E()
    )

def findPosition (vIn, element):
    idx = -1
    for ival in range(0, vIn.size()):
        if vIn.at(ival) == element:
            idx = ival
    return idx

def dump_part(genparts, idx, offset="", doDaughters=False):
    gp = genparts[idx]
    print "{}{:>4} >> ID={:>4} , mother ID={:>4} , pt={:.2f} eta={:.2f} phi={:.2f}".format(offset, idx, gp.pdgId(), gp.mother(0).pdgId(), gp.pt(), gp.eta(), gp.phi())
    if doDaughters:
        for idx in range(gp.numberOfDaughters()):
            dump_part(genparts, findPosition(genparts, gp.daughter(idx)), offset="  .. ", doDaughters=False)

ROOT.gROOT.SetBatch()
#events = Events ('file:/eos/uscms/store/group/l1upgrades/L1MuTrks/Ds_to_Tau3Mu_pythia8_5Apr2019/output/Tau3Mu_0.root')
events = Events('file:../../gensim_1000ev.root')

handleGenParts = Handle ('vector<reco::GenParticle>')
labelGenParts  = ("genParticles", "", "")

## output of the script
fOut = ROOT.TFile('tau_3mu.root', "recreate")
tOut = ROOT.TTree('treetau3mu', 'treetau3mu')

v_tau = ROOT.TLorentzVector(0.,0.,0.,0.)
v_mu1 = ROOT.TLorentzVector(0.,0.,0.,0.)
v_mu2 = ROOT.TLorentzVector(0.,0.,0.,0.)
v_mu3 = ROOT.TLorentzVector(0.,0.,0.,0.)

tOut.Branch('v_tau', v_tau)
tOut.Branch('v_mu1', v_mu1)
tOut.Branch('v_mu2', v_mu2)
tOut.Branch('v_mu3', v_mu3)


for iEv, event in enumerate(events):
    
    # if iEv > 0: break
    # if iEv > maxEvts and maxEvts > -1: break
    if (iEv % 1000 == 0): print iEv
    # print "... doing event: ", iEv

    event.getByLabel (labelGenParts, handleGenParts)
    genParts = handleGenParts.product()

    # print type(genParts)
    # print "-------------------------------------"
    # print "TOT gen parts : ", len(genParts)
    itau = []
    imu  = []
    for idx, gp in enumerate(genParts):
        pdgId  = gp.pdgId()
        status = gp.status()
        flags  = gp.statusFlags()
        # mother = gp.mother(0)

        if abs(pdgId) == 15 and gp.numberOfDaughters() == 3 and abs(gp.daughter(0).pdgId()) == 13 and abs(gp.daughter(1).pdgId()) == 13 and abs(gp.daughter(2).pdgId()) == 13: ## is a tau -> 3mu
            # print idx, " >> ", pdgId, gp.mother(0).pdgId(), gp.pt(), gp.eta()
            itau.append(idx)
            # if len(itau) != 1:
            #     print "@@@@@@ "
            #     print idx, " >> ", pdgId, gp.mother(0).pdgId(), gp.pt(), gp.eta()
        if abs(pdgId) == 13 and abs(gp.mother(0).pdgId()) == 15: ## is a mu from tau
            # print idx, " >> ", pdgId, gp.mother(0).pdgId(), gp.pt(), gp.eta()
            imu.append(idx)

    ## note: this can happen in case there are two D0 in the events that both decay to tau->3mu
    ## skipping is safe for now
    if len(itau) != 1:
        print "... too many taus? ", len(itau)
        # for i in itau:
            # dump_part(genParts, i, doDaughters=True)
        continue

    if len(imu) != 3:
        print "... could not find the mus? ", len(imu)
        continue

    copyToTLV (v_tau, genParts[itau[0]].p4())
    copyToTLV (v_mu1, genParts[imu[0]].p4())
    copyToTLV (v_mu2, genParts[imu[1]].p4())
    copyToTLV (v_mu3, genParts[imu[2]].p4())

    tOut.Fill()

fOut.cd()
tOut.Write()
