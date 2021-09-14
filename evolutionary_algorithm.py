import subprocess
import multiprocessing
import random


#Run tracking algorithm n times with different values of z max/min

#Population size n 

#Function to calculate efficiency

def marlin_eff(z):
    
    #source myvenv/bin/activate (activates virtual environment)
    z_change = '--MyCKFTracking.SeedFinding_CollisionRegion=' + str(z)
    track_name = '--MyLCParquet.OutputDir=LBLMuCWorkspace/output/data_seedckf_Zmax{}'.format(z) 
    Marlin = 'shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash -c \'source LBLMuCWorkspace/setup.sh LBLMuCWorkspace/build && Marlin {} {} ${{MYBUILD}}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=LBLMuCWorkspace/muonGun_sim_MuColl_v1.slcio\''.format(z_change, track_name)

    #cmd = arg + marlin
    print(Marlin)
    #print(str(setup) + str(arg) + str(Marlin))
    #subprocess.run(delete, shell = True)
    #subprocess.run(str(arg), shell = True)
    subprocess.run(Marlin, shell = True)

    #import mcc.lcparquet as lcpq
    import mcc.lcparquet as mcpq
    import data.dm as dm
    import matplotlib.pyplot as plt
    import dask.array as da

    data=mcpq.LCParquet('LBLMuCWorkspace/output/data_seedckf_Zmax'+str(z))  
    #data=dm.DataManager('mccplots/data.yaml')  
    # Load all necessary dataframes
    samples=['actsseed0']
    #mc=mcpq.concat_load([data.samples[sample] for sample in samples], 'mc')
    mc=data.load('mc')
    tr=data.load('track')
    mc2tr=data.load('mc2tr')
    #tr=lcpq.concat_load([data.samples[sample] for sample in samples], 'tr')
    #mc2tr=mcpq.concat_load([data.samples[sample] for sample in samples], 'mc2tr')
    # the single muon
    mu=mc[mc.colidx==0]
    # need at least two good hits
    mc2tr=mc2tr[mc2tr.weight>0.5]
    # merge to get all info in one dataframe
    tracks=mu.merge(
        mc2tr,left_on=['evt','colidx'],right_on=['evt','from']).merge(
            tr,left_on=['evt','to'],right_on=['evt','colidx'])

    eff = len(tracks.index)/len(mu.index)
    # number between 0 and 1 
    return eff

    #delete data from previous tracking, shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash, setup.sh,
    #Marlin ${MYBUILD}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=/path/to/events.slcio,source myenv/bin/activate, eff_calc
    

    #calculates eff for a given z
    # number between 0 and 1 

#Generate z values
z_values = []
for z in range(5):
    z_values.append(random.uniform(0,10))

#Generations 
for i in range(3):

    #Ranks z values with value for efficiency as a function of z
    rankedsolutions = []
    for z in z_values:
    #z is an element of z_values which was some # z values generated prior in a for loop
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
