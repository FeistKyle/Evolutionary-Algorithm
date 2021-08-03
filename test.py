import subprocess
import random

def marlin_eff(z):
    
    #shifter ='shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8'
    #setup ='source LBLMuCWorkspace/setup.sh'
    z_change = '--MyCKFTracking.SeedFinding_ZMax=' + str(z)
    Marlin = 'shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash -c \'source LBLMuCWorkspace/setup.sh LBLMuCWorkspace/build && Marlin ${MYBUILD}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=muonGun_sim_MuColl_v1.slcio\''

    #cmd = arg + marlin
    print(Marlin)
    #print(str(setup) + str(arg) + str(Marlin))
    #subprocess.run(delete, shell = True)
    #subprocess.run(str(arg), shell = True)
    subprocess.run(Marlin, shell = True)

    import mcc.lcparquet as lcpq
    import data.dm as dm
    import matplotlib.pyplot as plt
    import dask.array as da

    data=dm.DataManager('mccplots/data.yaml')  
    # Load all necessary dataframes
    samples=['actsseed0']
    mc=lcpq.concat_load([data.samples[sample] for sample in samples], 'mc')
    tr=lcpq.concat_load([data.samples[sample] for sample in samples], 'tr')
    mc2tr=lcpq.concat_load([data.samples[sample] for sample in samples], 'mc2tr')
    # the single muon
    mu=mc[mc.colidx==0]
    # need at least two good hits
    mc2tr=mc2tr[mc2tr.weight>0.5]
    # merge to get all info in one dataframe
    tracks=mu.merge(
        mc2tr,left_on=['title','evt','colidx'],right_on=['title','evt','from']).merge(
            tr,left_on=['title','evt','to'],right_on=['title','evt','colidx'])

    eff = len(tracks.index)/len(mu.index)
    print(eff)
    return eff

marlin_eff(4)
