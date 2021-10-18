import subprocess
from multiprocessing import Pool
import random
import matplotlib.pyplot as plt
import pandas as pd
import os.path
random.seed(7)
#Run tracking algorithm n times with different values of z max/min

#Population size n 

#Function to calculate efficiency

def marlin_eff(z):

    z_change = '--MyCKFTracking.SeedFinding_CollisionRegion=' + str(z)
    track_name = '--MyLCParquet.OutputDir=LBLMuCWorkspace/output/data_seedckf_Zmax{}'.format(z) 
    track_name_FakeRate = '--MyLCParquet.OutputDir=LBLMuCWorkspace/output/data_seedckf_BIB{}'.format(z) 

    Marlin = 'shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash -c \'source LBLMuCWorkspace/setup.sh LBLMuCWorkspace/build && Marlin {} {} ${{MYBUILD}}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=LBLMuCWorkspace/muonGun_sim_MuColl_v1.slcio\''.format(z_change, track_name)
    Marlin_FakeRate = 'shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash -c \'source LBLMuCWorkspace/setup.sh LBLMuCWorkspace/build && Marlin {} {} ${{MYBUILD}}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=LBLMuCWorkspace/BIB_010.slcio --global.MaxRecordNumber=2\''.format(z_change, track_name_FakeRate)


    datafile = 'LBLMuCWorkspace/output/data_seedckf_Zmax' + str(z)
    if not os.path.exists(datafile):
        subprocess.run(Marlin, shell = True)

    datafile_FakeRate = 'LBLMuCWorkspace/output/data_seedckf_BIB' + str(z)
    if not os.path.exists(datafile_FakeRate):
        subprocess.run(Marlin_FakeRate, shell = True)

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


    dataBIB = mcpq.LCParquet('LBLMuCWorkspace/output/data_seedckf_BIB'+str(z))
    trBIB = dataBIB.load('track')

    k = 1/1000
    #matching each montecarlo particle to a track and subtracting a weighted value corresponding to the amount of fakes from the BIB
    score = len(tracks.index)/len(mu.index) - k*len(trBIB.index)
    eff = len(tracks.index)/len(mu.index)
    fakes = len(trBIB.index)

    # number between 0 and 1 
    return ((score,eff,fakes), z)

    #delete data from previous tracking, shifter --image gitlab-registry.cern.ch/berkeleylab/muoncollider/muoncollider-docker/mucoll-ilc-framework:1.5.1-centos8 /bin/bash, setup.sh,
    #Marlin ${MYBUILD}/packages/ACTSTracking/example/actsseed_steer.xml --global.LCIOInputFiles=/path/to/events.slcio,source myenv/bin/activate, eff_calc
    
    #calculates eff for a given coll region
    # number between 0 and 1 

#Generate coll region values
z_values = []
for z in range(5):
    z_values.append(random.uniform(0,10))

#print(z_values)

#Plot data sets
#score as a function of the generation
plot_maxeff= []
plot_mineff= []


plot_effcollregx= []
plot_effcollreg_eff= []
plot_effcollreg_fakes= []
plot_effcollreg_score= []

plot_collreg = []
plot_collregset = []


#Generations 
for i in range(9):

    #Map the function marlin_eff to the collision region values

    workers = Pool(10)
    rankedsolutions = workers.map(marlin_eff, z_values)
    rankedsolutions = sorted(rankedsolutions, key = lambda score: score[0][0], reverse = True) 
    #At this point there's an ordered list of score, eff, and fakes along with the collision region value

    print(f'=== gen {i} best solutions ===')

    #Prints generation number corresponding to ranked solutions and z values
    print(rankedsolutions)
    #Prints first efficiency z value pair

    ################plot#########################
    for y in rankedsolutions:
        plot_effcollreg_score.append(y[0][0])

    for b in rankedsolutions:
        plot_effcollreg_eff.append(b[0][1])
    
    for a in rankedsolutions:
        plot_effcollreg_fakes.append(a[0][2])

    for x in rankedsolutions:
        plot_effcollregx.append(x[1])

    for g in rankedsolutions:
        plot_collreg.append(g[1])
    
    plot_collregset.append(plot_collreg)
    plot_collreg = []
    #makes list of best/worst eff for the generation
    plot_maxeff.append(rankedsolutions[0][0][0])
    plot_mineff.append(rankedsolutions[4][0][0])
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
#print(plot_effcollregx)
#print(plot_effcollreg_score)
#print(plot_collregset)

#Plots

# #Max eff

# plt.scatter(list(range(len(plot_maxeff))), plot_maxeff)
# plt.ylabel('Max Eff')
# plt.xlabel('Generation')
# plt.savefig('maxeff_gen.png')
# plt.tight_layout()
# plt.clf()

# #Min eff
# plt.scatter(list(range(len(plot_mineff))), plot_mineff)
# plt.ylabel('Min Eff')
# plt.xlabel('Generation')
# plt.savefig('mineff_gen.png')
#plt.tight_layout()
# plt.clf()

# #Collreg vs gen
# n = 0
# for e in plot_collregset:
#     n += 1 
#     for h in e:
#         plt.scatter(n, h)
#         plt.ylabel('Collision Region')
#         plt.xlabel('Generation')
# plt.savefig('collreg_gen.png')
#plt.tight_layout()
# plt.clf()

#score vs collision region
plt.plot(plot_effcollregx, plot_effcollreg_score,'o')
plt.ylabel('Score')
plt.xlabel('Collision Region (mm)')
plt.savefig('effcollregscore.png')
plt.tight_layout()
#plt.clf()

#eff vs collision region
# plt.plot(plot_effcollregx, plot_effcollreg_eff,'o')
# plt.ylabel('Eff')
# plt.xlabel('Collision Region (mm)')
# plt.savefig('effcollregeff.png')
# plt.tight_layout()
# plt.clf()

# #fakes vs collision region
# plt.plot(plot_effcollregx, plot_effcollreg_fakes,'o')
# plt.ylabel('fakes')
# plt.xlabel('Collision Region (mm)')
# plt.savefig('effcollregfakes.png')
# plt.tight_layout()
# plt.clf()

#Save data as excel
dict1 = {'CollRegion_Val': plot_effcollregx, 'Eff_Val': plot_effcollreg_score}
df1 = pd.DataFrame(dict1)
df1.to_csv('Eff_CollRegionVal.csv') 

dict2 = {'generation': list(range(len(plot_maxeff))), 'MaxEff_Val': plot_maxeff}
df2 = pd.DataFrame(dict2)
df2.to_csv('MaxEff_Gen.csv') 

dict3 = {'generation': list(range(len(plot_mineff))), 'MinEff_Val': plot_mineff}
df3 = pd.DataFrame(dict3)
df3.to_csv('MinEff_Gen.csv') 
