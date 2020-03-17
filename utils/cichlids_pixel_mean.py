#cichlids_video_mean_variance_calculation

from skimage import io, img_as_float
import numpy as np
import os

images_directory = '/data/home/llong35/0004_vid/jpgs'
categories  = os.listdir(images_directory)
count = 0
pixels = np.zeros(0)

for category in categories:
    if category.startswith('.'):
        continue
    else:
        folders  = os.listdir(images_directory+'/'+category)
        for folder in folders:
            if folder.startswith('.'):
                continue
            else:
                files = os.listdir(images_directory+'/'+category+'/'+folder)
                for file in files:
                    #print(file)
                    if not file.endswith('.jpg'):
                        continue
                    else:
                        file_path = '/'.join([images_directory,category,folder,file])
                        image = io.imread(file_path)
                        if count == 0:
                            
                            images = [image]
                        else:
                            #this part is bad, has to be updated
                            images.append(image)
                            
                        count += 1
                        if count %1000 == 0:
                            pixels = np.concatenate(images,axis=0)
                            r_mean = np.mean(pixels[:,:,0])
                            g_mean = np.mean(pixels[:,:,1])
                            b_mean = np.mean(pixels[:,:,2])
                            r_std = np.std(pixels[:,:,0])
                            g_std = np.std(pixels[:,:,1])
                            b_std = np.std(pixels[:,:,2])
                            rgb_mean = [r_mean,g_mean,b_mean]
                            rgb_std = [r_std,g_std,b_std]
                            print(rgb_mean)
                            print(rgb_std)
                            pixels = image
                        #print(file_path)

r_mean = np.mean(pixels[:,:,0])
g_mean = np.mean(pixels[:,:,1])
b_mean = np.mean(pixels[:,:,2])
r_std = np.std(pixels[:,:,0])
g_std = np.std(pixels[:,:,1])
b_std = np.std(pixels[:,:,2])
rgb_mean = [r_mean,g_mean,b_mean]
rgb_std = [r_std,g_std,b_std]
print(rgb_mean)
print(rgb_std)