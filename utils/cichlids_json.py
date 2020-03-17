from __future__ import print_function, division
import os
import sys
import json
import pandas as pd
import pdb, argparse

def convert_csv_to_dict(csv_path, subset):
    try:
        data = pd.read_csv(csv_path, delimiter=' ', header=None)
    except:
        print('Warning: no {}, check data'.format(csv_path))
        return {}
    keys = []
    key_labels = []
    for i in range(data.shape[0]):
        row = data.ix[i, :]
        slash_rows = data.ix[i, 0].split('/')
        class_name = slash_rows[0]
        basename = slash_rows[1]
        
        keys.append(basename)
        key_labels.append(class_name)
    database = {}
    for i in range(len(keys)):
        key = keys[i]
        database[key] = {}
        database[key]['subset'] = subset
        label = key_labels[i]
        database[key]['annotations'] = {'label': label}
    
    return database

def load_labels(label_csv_path):
    data = pd.read_csv(label_csv_path, delimiter=' ', header=None)
    labels = []
    for i in range(data.shape[0]):
        labels.append(data.ix[i, 1])
    return labels

def convert_cichlids_csv_to_activitynet_json(label_csv_path, train_csv_path, 
                                           val_csv_path, dst_json_path):
    labels = load_labels(label_csv_path)
    train_database = convert_csv_to_dict(train_csv_path, 'training')
    val_database = convert_csv_to_dict(val_csv_path, 'validation')
    
    dst_data = {}
    
    dst_data['labels'] = labels
    
    dst_data['database'] = {}
    dst_data['database'].update(train_database)
    dst_data['database'].update(val_database)

    with open(dst_json_path, 'w') as dst_file:
        json.dump(dst_data, dst_file)


parser = argparse.ArgumentParser()
parser.add_argument('classFile', type = str, help = 'File containing the possible labels')
parser.add_argument('trainFile', type = str, help = 'File containing the train videos')
parser.add_argument('testFile', type = str, help = 'File containing the test videos')
parser.add_argument('outFile', type = str, help = 'Location of output file')

args = parser.parse_args()

label_csv_path = args.classFile
train_csv_path = args.trainFile
val_csv_path = args.testFile

dst_json_path = args.outFile

convert_cichlids_csv_to_activitynet_json(label_csv_path, train_csv_path,
                                               val_csv_path, dst_json_path)
