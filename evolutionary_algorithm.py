import subprocess
from multiprocessing import Pool
import random
import matplotlib.pyplot as plt
import pandas as pd
import os.path
random.seed(1)
#Run tracking algorithm n times with different values of z max/min

#Population size n 

#Function to calculate efficiency

def marlin_eff(z):

    z_change = '--MyCKFTracking.SeedFinding_CollisionRegion=' + str(z)
    track_name = '--MyLCParquet.OutputDir=LBLMuCWorkspace/output/data_seedckf_Zmax{}'.format(z) 
    Marlin = 'shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash -c \'source LBLMuCWorkspace/setup.sh LBLMuCWorkspace/build && Marlin {} {} ${{MYBUILD}}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=LBLMuCWorkspace/muonGun_sim_MuColl_v1.slcio\''.format(z_change, track_name)

    datafile = 'LBLMuCWorkspace/output/data_seedckf_Zmax' + str(z)
    if not os.path.exists(datafile):
        subprocess.run(Marlin, shell = True)

    #source myvenv/bin/activate (activates virtual environment)

    
    #cmd = arg + marlin
    #print(Marlin)
    #print(str(setup) + str(arg) + str(Marlin))

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
    return (eff, z)

    #delete data from previous tracking, shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash, setup.sh,
    #Marlin ${MYBUILD}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=/path/to/events.slcio,source myenv/bin/activate, eff_calc
    
    #calculates eff for a given coll region
    # number between 0 and 1 

#Generate coll region values
z_values = []
for z in range(5):
    z_values.append(random.uniform(0,3))

#print(z_values)

plot_maxeff= []
plot_mineff= []
plot_effcollregy= []
plot_effcollregx= []

#Generations 
for i in range(10):

    #Ranks z values with value for efficiency as a function of z
    #z is an element of z_values which was some # z values generated prior in a for loop

    workers = Pool(10)
    rankedsolutions = workers.map(marlin_eff, z_values)
    rankedsolutions = sorted(rankedsolutions, key = lambda eff: eff[0], reverse = True)
    #At this point there's an ordered list of pairs of values each with an efficiency and a z value for that efficiency from highest to lowest

    print(f'=== gen {i} best solutions ===')

    #Prints generation number corresponding to ranked solutions and z values
    print(rankedsolutions)
    #Prints first efficiency z value pair

    ################plot#########################
    for y in rankedsolutions:
        plot_effcollregy.append(y[0])

    for x in rankedsolutions:
        plot_effcollregx.append(x[1])
    
    #makes list of best/worst eff for the generation
    plot_maxeff.append(rankedsolutions[0][0])
    plot_mineff.append(rankedsolutions[4][0])
    #############################################

    del rankedsolutions[3:5]

    elements = []
    prob = .1
    for s in rankedsolutions:
        if random.random() < prob:
                elements.append(s[1]*(1+random.gauss(0, .01)))
        else:
            elements.append(s[1])
   
    elements.append(random.uniform(0,10))
    elements.append(random.uniform(0,10))

    z_values = elements
    #newGen becomes the new input for the next iteration i + 1

#print(plot_maxeff)
#print(plot_mineff)
#print(list(range(len(plot_maxeff))))
print(plot_effcollregx)
print(plot_effcollregy)


#Plots
#Max eff
plt.plot(list(range(len(plot_maxeff))), plot_maxeff)
plt.ylabel('Max Eff')
plt.xlabel('Generation')
plt.savefig('maxeff_gen.png')
plt.clf()
#Min eff
plt.plot(list(range(len(plot_mineff))), plot_mineff)
plt.ylabel('Min Eff')
plt.xlabel('Generation')
plt.savefig('mineff_gen.png')
plt.clf()
#eff vs collision region
plt.plot(plot_effcollregx, plot_effcollregy,'o')
plt.ylabel('Eff')
plt.xlabel('Collision Region (mm)')
plt.savefig('effcollreg.png')
plt.clf()

#Save data as excel
dict1 = {'CollRegion_Val': plot_effcollregx, 'Eff_Val': plot_effcollregy}
df1 = pd.DataFrame(dict1)
df1.to_csv('Eff_CollRegionVal.csv') 

dict2 = {'generation': list(range(len(plot_maxeff))), 'MaxEff_Val': plot_maxeff}
df2 = pd.DataFrame(dict2)
df2.to_csv('MaxEff_Gen.csv') 

dict3 = {'generation': list(range(len(plot_mineff))), 'MinEff_Val': plot_mineff}
df3 = pd.DataFrame(dict3)
df3.to_csv('MinEff_Gen.csv') 
