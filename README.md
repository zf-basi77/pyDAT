# pyDAT
this is a set of libraries intended to be used when dealing with OpenEphys ".dat" files, in addition to spike-time outputs from the Kilosort/Phy pipeline. 


Required:
1) .dat OpenEphys electrophysiology file
2) run .dat through Kilosort then curate the extracted waveforms using Phy
      a) Phy-processing leads to clusters_info.tsv, which contains relevant information

Running Script:
1) BFC_library contains all necessary functions, though the OpenEphyDtype_SpikeExtractor&Sorter_clean.ipynb shows you how to run the functions
2) Load dat file and clusters_info.tsv
3) Based on spike-timing data and the dat file, a bisect function is used to find and extract every single detected unit in the file; these are stored in arrays
       a) bisect algorithm is VERY fast compared to a normal or brute-force search
5) These waveforms can be averaged and then compare to assess for phenotype (e.g. narrow vs broad)

TO DO: add links to sample data and input files. (these can be rather large; e.g. 30min of recording 128 data channels at 30kHz is rouhgly 25-30GB)
