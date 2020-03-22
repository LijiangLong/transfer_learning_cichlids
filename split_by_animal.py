import os
import numpy as np
import pandas as pd
import sys
from subprocess import call
import json
import pdb

from training_size_test import convert_csv_to_dict

def create_random_spliting_train_test(annotation_file,master_dir,data_folder,n_training=3,split_ratio = 0.8):
    animals_list = ['MC16_2', 'MC6_5', 'MCxCVF1_12a_1', 'MCxCVF1_12b_1', 'TI2_4', 'TI3_3', 'CV10_3']
    training = np.random.choice(animals_list, n_training, replace=False)
    result_dir = os.path.join(master_dir,'_'.join(training))
    if os.path.isdir(result_dir):
        return
    else:
        call(['mkdir',result_dir])
        call(['ln','-s',data_folder,result_dir+'/'])
    train_list_csv = os.path.join(result_dir,'train_list.csv')
    val_list_csv = os.path.join(result_dir,'val_list.csv')
    test_list_csv = os.path.join(result_dir,'test_list.csv')
    dst_json_path = os.path.join(result_dir,'cichlids.json')
    
    
    annotateData = pd.read_csv(annotation_file, sep = ',', header = 0)

    i = 0
    with open(train_list_csv,'w') as train_output, open(val_list_csv,'w') as val_output,open(test_list_csv,'w') as test_output:
        for index,row in annotateData.iterrows():
            output_string = row['Label']+'/'+row['Location']+'\n'
            animal = row['MeanID'].split(':')[0]
            #first determine if this is train/validation or test
            if animal not in training:
                test_output.write(output_string)
                continue
            #if train/validation, determine if this go to train or validation
            if np.random.uniform() < split_ratio:
                train_output.write(output_string)
            else:
                val_output.write(output_string)
    train_database = convert_csv_to_dict(train_list_csv, 'training')
    val_database = convert_csv_to_dict(val_list_csv, 'validation')
    test_database = convert_csv_to_dict(test_list_csv, 'test')
    dst_data = {}
    dst_data['labels'] = ['c', 'f', 'p', 't', 'b', 'm', 's', 'x', 'o', 'd']
    dst_data['database'] = {}
    dst_data['database'].update(train_database)
    dst_data['database'].update(val_database)
    dst_data['database'].update(test_database)
    with open(dst_json_path, 'w') as dst_file:
        json.dump(dst_data, dst_file)
            
def prepare_animal_subset_directories(excel_file,master_directory,data_folder):
    # for each training, create a new folder for training results watching
    
        # create a new directory
        directory = os.path.join(master_directory,'{}-{}-{}'.format(train_ratio,val_ratio,test_ratio))
        call(['mkdir',directory])
        
        split_train_validation_test(directory,data_folder,train_ratio,val_ratio)
        
def main():
    annotation_file = '/data/home/llong35/patrick_code_test/modelAll_34/AnnotationFile.csv'
    master_dir = '/data/home/llong35/data/transfer_test/animal_split'
    data_folder = '/data/home/llong35/data/annotated_videos'
    create_random_spliting_train_test(annotation_file,master_dir,data_folder,5,split_ratio = 0.8)
if __name__ == '__main__':
    main()