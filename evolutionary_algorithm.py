import subprocess
import random
import mcc.lcparquet as lcpq
import data.dm as dm
import matplotlib.pyplot as plt
import dask.array as da

#Run tracking algorithm n times with` different values of z max/min

#Population size n 

#Function to calculate efficiency

def marlin_eff(z):
    
    subprocess.run('deactivate', shell=True)
    subprocess.run('--MyCKFTracking.SeedFinding_ZMax=z', shell=True, input = z)
    subprocess.run('shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash', shell=True)
    subprocess.run('source LBLMuCWorkspace/setup.sh', shell=True)
    subprocess.run('Marlin ${MYBUILD}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=muonGun_sim_MuColl_v1.slcio', shell=True)
    subprocess.run('source myenv/bin/activate', shell=True)
    
    #Run eff_calc.py

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
    return eff

    #deactivate, shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash, setup.sh,
    #Marlin ${MYBUILD}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=/path/to/events.slcio,source myenv/bin/activate, eff_calc
    

    #calculates eff for a given z
    # number between 0 and 1 

#Generate z values
z_values = []
for z in range(5):
    z_values.append(random.uniform(0,200))

#Generations 
for i in range(10):

    #Ranks z values with value for efficiency as a function of z
    rankedsolutions = []
    for z in z_values:
    #z is an element of z_values which was 100 z values generated prior in a for loop
        rankedsolutions.append((marlin_eff(z), z))
    rankedsolutions.sort()
    rankedsolutions.reverse()
    #At this point there's an ordered list of pairs of values each with an efficiency and a z value for that efficiency from highest to lowest
    print(f'=== gen {i} best solutions ===')
    #Prints generation number corresponding to ranked solutions and z values
    print(rankedsolutions[0])
    #Prints first efficiency z value pair
    if rankedsolutions[0][0] > .9:
        break
    #Terminates the loop if eff is found to be higher than .9
    bestsolutions = rankedsolutions[:10]
    #takes first 10 pairs in ranked solutions
    elements = []
    #Creates an empty list called elements
    for s in bestsolutions:
        elements.append(s[0][1])
    #Loops through 10 best solutions, adding the z value of each pair to the elements list
    newGen = []
    for _ in range(3):
        e = random.choice(elements) * random.uniform(0.99, 1.01)
    #Loops through 100 times, choosing a random z value from elements to mutate
        newGen.append(e)
    #Adds mutated elements to newGen which is the new generation 
    z_values = newGen
    #newGen becomes the new input for the next iteration i 
