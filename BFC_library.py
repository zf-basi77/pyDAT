import pandas as pd
import matplotlib.pylab as plt
import numpy as np
import os
from scipy.stats import linregress
from tqdm import tqdm


def check_invert(arr):                 # a function that checks if an AP is 'inverted', defined as the functions outline. 

    #  a spike waveform array          # this is optional, but will make APs all look the 'same' direction which can be useful for finding spike-width
    global min_diff, max_diff
    mean = np.mean(arr) #get mean
    mini = np.min(arr) #get min
    maxi = np.max(arr) #get max
    min_diff = abs(mini-mean) # get diffs between min and max against mean
    max_diff = abs(maxi-mean)
    if min_diff > max_diff:  #if min-mean > max-mean, then signal is considered inverted
        inversion=-1  #set inversion to -1 to multiply the waveform and flip it
    else:
        inversion=1

    return inversion


#read and organize all cluster txt files from a kilosort folder
# put all in a single df


def read_clustersTimes(spath):  #reads cluster time information
    #input: patrh to folder with cluster.txt files
    import re  #import library to parse numbers from text
    files = []
    for i in os.listdir(spath):  #check folder for correct files, when found store its name
        if 'cluster' in i and '.txt' in i:
            files.append(i)

    dfs = []

    for i in range(len(files)): #loop through each found file
        tmp = pd.read_csv(os.path.join(spath, files[i]), header=None) #read it as csv
        tmp = tmp.rename(columns={0:'spike_times'}) 
        tmp['ID_long'] = files[i]
        tmp['cluster'] = int(re.findall(r'\d+',files[i])[0])  #add cluster name as clolumn
        dfs.append(tmp) #append df rto list

    return pd.concat(dfs).reset_index(drop=True) #return a master df with all of the cluster's spiketimes

#BELOW, HOW TO EXECUTE CODE
#spath = r'D:\phyRedone_practice\kilosort4'
#stimes_df = read_clustersTimes(spath)

import numpy as np
import bisect


def searchNextract_spikeWaveforms(data, stimes_df, tarr, cluster):  # searches and extracts spike waveforms from a .dat file

    #inputs:

        #data: this is the import .dat file with all analog channels 
        #stimes_df: a df with cluster and spike-times info (the output of 'read_clustersTime' function)
        #tarr this is an array of "true-bin time", essentially each cell's values are a mulitple of the resolution (1/30000) 
        


    def get_closest_index(time, large_array):  #function to get the closest index of the spike onset

        # Convert the time to the corresponding index in the large array
        target_index = time
        insert_pos = bisect.bisect_left(large_array, target_index) #do a binary-based search for the spike (VERY FAST)
        
        
        if insert_pos == 0:# If the insertion point is at the start of the array
            return 0
       
        if insert_pos == len(large_array): # If the insertion point is at the end of the array
            return len(large_array) - 1
        
        
        before = large_array[insert_pos - 1]# Check the two closest positions: before and after the insertion point
        after = large_array[insert_pos]
        
        
        if abs(before - target_index) <= abs(after - target_index): # Return the closest index based on absolute distance
            return insert_pos - 1
        else:
            return insert_pos

    def get_sample_indices(event_times, large_array): #get sample indices by looping can calling above fiunction to fo the heavy lifting
        indices = []
        for event_time in event_times:
            index = get_closest_index(event_time, large_array)
            indices.append(index)
        return np.array(indices)
    


    sr = 30000
    resolution = 1/sr


    targets = np.array(stimes_df[stimes_df.cluster==cluster].reset_index(drop=True).spike_times)       #get cluster specific spike-times
    #chan =    #get channel from cluster_info.tsv for comprehensive tracking of data


    indices = get_sample_indices(targets, tarr)
    #print(indices)  # Indices that correspond to event times in the large array

    waveforms = []
    for i in tqdm(range(len(indices)), desc='extarcting spike waveforms'): #loop and get windowed spike waveforms
        waveforms.append(data[indices[i]-15:indices[i]+25])


    return waveforms



def make_timeBinArray(sr, length):   #make the time array of equal time-bins based on samplig rate for crossreference
    resolution = 1/sr
    return [resolution*i for i in range(length)]

## how to run above functions
#tarr = make_timeBinArray(sr=30000, length = len(data_array[:][:,1] )) # for a given channel (all should be equal in same recording), get length of data

#avg_waves = []
#std_waves = []
#cluster_id = []
#chani = []


#for cluster in stimes_df.cluster.unique():
#    chan = int(clus_info[clus_info.cluster_id==58].ch)
#    waveforms = searchNextract_spikeWaveforms(data_array[:][:,chan], stimes_df, tarr, cluster=cluster)
#    avg_waves.append(np.mean(waveforms, axis=0))
#    std_waves.append(np.std(waveforms, axis=0))
#    cluster_id.append(cluster)
#    chani.append(chan)


#read and organize all cluster txt files from a kilosort folder
# put all in a single df


def rasterizeNmake_diagnosticPlots(self, cluster, rtimes, psth=False, raster_StimLines=True):
    #psth takes a VERY long time, set to False to skip it.. Specially when doing the whole recording (i.e./e.g. not splitting per stimulus)

    #INPUTS
    ## self is a df with clusters and their spike times (output of 'read_clustersTimes(path)')


    global trial, windows
    tmp = self[self.cluster==cluster].reset_index(drop=True)
    windows = []
    trial = []
    for i in tqdm(range(len(rtimes))):
        st = rtimes[i]-1
        end = rtimes[i]+2
        windows.append(np.array(tmp[(tmp.spike_times>st)&(tmp.spike_times<end)].spike_times)-rtimes[i])
        trial.append(i)
    plt.eventplot(windows)
    plt.title('Raster plot for cluster '+str(cluster), fontsize=20)
    plt.ylabel('<-- Trial', fontsize=16)
    plt.xlabel('Time (s)', fontsize=16)
    plt.axvline(0, c='red')
    if raster_StimLines:
        for i in range(10):
            plt.axhline(25+25*i, c='r', alpha=.3)
    plt.gca().invert_yaxis()
    plt.show()



    if psth:
        ras_start = 1 
        ras_end = 2

        bins=[]
        for i in np.arange(-ras_start, ras_end+0.005, 0.005):   #to use arange, which allows decimals
            bins.append(round(i,3))     #to round the float to 2 decimal places  

        plt.hist(windows, bins, stacked=True, width=0.01, label = 'hist') #to plot the PSTH
        plt.ylabel('Spikes/bin')
        plt.title('PSTH')

    return


#for cluster in stimes_df.cluster.unique():
#    rasterizeNmake_diagnosticPlots(stimes_df, cluster, psth=False, raster_StimLines=True)

def binarize_timeArray(stamps):

    # Set the resolution (number of divisions along the x-axis)
    resolution = 30000*3  # set resolution! 

    # Quantize the event data to integer indices
    max_position = -1  # Get the maximum position
    min_position = 2  # Get the minimum position
    scale_factor = resolution / (max_position - min_position)  # Scaling factor for quantization

    # Create an empty binary array
    binary_array = np.zeros(resolution+1)

    # Map the event data to indices based on the resolution
    for event in stamps:
        # Convert the event position to the corresponding index in the binary array
        index = int((event - min_position) * scale_factor)
        binary_array[index] = 1

    
    return binary_array[::-1]



def plot_Cluster(cluster, cluster_id, avg_waves, std_waves, chani, std_fac, soft_check=True, inversion=True):
    global wave_label, diff
    indi = np.where(cluster==np.array(cluster_id))[0][0]
    if inversion:
        check_invert(avg_waves[indi])
        if soft_check:
            diff = abs(max(avg_waves[indi])-min(avg_waves[indi]))
            if diff < 5:
                plt.plot(avg_waves[indi]*check_invert(avg_waves[indi]), c='r', label='likely bad unit')
                plt.fill_between(list(range(len(avg_waves[indi]))), (avg_waves[indi]*check_invert(avg_waves[indi])-std_waves[indi]*std_fac), (avg_waves[indi]*check_invert(avg_waves[indi])+std_waves[indi]*std_fac), color='b', alpha=.3)
                plt.title('Cluster '+str(cluster)+' in chan '+str(chani[indi]))
                wave_label=0
                plt.legend()
                plt.show()
            else:
                plt.plot(avg_waves[indi]*check_invert(avg_waves[indi]), c='b', label='likely good unit')
                plt.fill_between(list(range(len(avg_waves[indi]))), (avg_waves[indi]*check_invert(avg_waves[indi])-std_waves[indi]*std_fac), (avg_waves[indi]*check_invert(avg_waves[indi])+std_waves[indi]*std_fac), color='b', alpha=.3)
                plt.title('Cluster '+str(cluster)+' in chan '+str(chani[indi]))
                wave_label=1
                plt.legend()
                plt.show()
        else:
            plt.plot(avg_waves[indi]*check_invert(avg_waves[indi]), c='b')
            plt.fill_between(list(range(len(avg_waves[indi]*check_invert(avg_waves[indi])))), (avg_waves[indi]*check_invert(avg_waves[indi])-std_waves[indi]*std_fac), (avg_waves[indi]*check_invert(avg_waves[indi])+std_waves[indi]*std_fac), color='b', alpha=.3)
            plt.title('Cluster '+str(cluster)+' in chan '+str(chani[indi]))
            plt.legend()
            plt.show()
    else:
        if soft_check:
            diff = abs(max(avg_waves[indi])-min(avg_waves[indi]))
            if diff < 5:
                plt.plot(avg_waves[indi], c='r', label='likely bad unit')
                plt.fill_between(list(range(len(avg_waves[indi]))), (avg_waves[indi]-std_waves[indi]*std_fac), (avg_waves[indi]+std_waves[indi]*std_fac), color='b', alpha=.3)
                plt.title('Cluster '+str(cluster)+' in chan '+str(chani[indi]))
                wave_label=0
                plt.legend()
                plt.show()
            else:
                plt.plot(avg_waves[indi], c='b', label='likely good unit')
                plt.fill_between(list(range(len(avg_waves[indi]))), (avg_waves[indi]-std_waves[indi]*std_fac), (avg_waves[indi]+std_waves[indi]*std_fac), color='b', alpha=.3)
                plt.title('Cluster '+str(cluster)+' in chan '+str(chani[indi]))
                wave_label=1
                plt.legend()
                plt.show()
        else:
            plt.plot(avg_waves[indi], c='b')
            plt.fill_between(list(range(len(avg_waves[indi]))), (avg_waves[indi]-std_waves[indi]*std_fac), (avg_waves[indi]+std_waves[indi]*std_fac), color='b', alpha=.3)
            plt.title('Cluster '+str(cluster)+' in chan '+str(chani[indi]))
            plt.legend()
            plt.show()
    return wave_label
