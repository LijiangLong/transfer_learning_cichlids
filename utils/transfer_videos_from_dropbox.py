import pandas as pd
import os
import pdb
from subprocess import call

#transfer videos to a single folder for downstream processing
fish_folder = '/Users/lijiang/Dropbox (GaTech)/McGrath/Apps/CichlidPiData/MC6_5/VideoAnalysis'
target_folder = '/Users/lijiang/Desktop/Zach_new_annotations_HMM_videos'
for folder in os.listdir(fish_folder):
    folder_path = fish_folder+'/'+folder
    if not os.path.isdir(folder_path):
        continue
    annotation_csv = '/'.join([folder_path,'ClusterData','LabeledClusters.csv'])
    clips_folder = '/'.join([folder_path,'ClusterData','MLClips'])
    if folder == '0010_vid':
        tab = ','
    else:
        tab = '\t'
    #read the csv file
    df = pd.read_csv(annotation_csv,sep = tab)
    df = df.dropna(subset=['ManualLabel'])
    for index, row in df.iterrows():
        label = row['ManualLabel']
        #check if directory exists
        des_folder = target_folder +'/'+label
        if not os.path.isdir(des_folder):
            os.mkdir(des_folder)
        video_file = clips_folder + '/'
        temp = [row['LID'],row['N'],row['X'],row['Y']]
        video_file += '_'.join([str(x) for x in temp])
        video_file += '_HMM.mp4'
        command = ['cp',video_file,des_folder+'/']
        call(command)
        print(' '.join(command))
        
        
        
        







