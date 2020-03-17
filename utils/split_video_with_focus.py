# split video with focus

import subprocess
annotation_file = '/Users/lijiang/Dropbox (GaTech)/research/cichlids_behavior_annotation/MC9_1_Day8_coordinates_timepoints_102418_corrected.csv'
video_file = '/Users/lijiang/Video_8_10800_15800.mp4'
spit_folder = '/Users/lijiang/Desktop/MC9_1_day_8/Video/spit/'
scoop_folder = '/Users/lijiang/Desktop/MC9_1_day_8/Video/scoop/'
offset = 10800

with open(annotation_file,'r') as input:
    input.readline()
    times = []
    xs = []
    ys = []
    events = []
    for line in input:
        time, event, x, y = line.split(',')[0:4]
        time = round(float(time),2)
        times.append(time)
        x = float(x)
        xs.append(x)
        y = float(y)
        ys.append(y)
        events.append(event)
    total_events = len(times)
    for i in range(total_events):
        if i == 0:
            if times[1]-times[0] < 1:
                continue
        elif i == total_events-1:
            if times[total_events-1]-times[total_events-2] < 1:
                continue
        else:
            if times[i+1]-times[i] < 1 or times[i]-times[i-1] < 1:
                continue
        if events[i] == 'Spit':
            output_file_name = spit_folder
            
        else:
            output_file_name = scoop_folder
        output_file_name += 'MC9_1_Day_8_'+str(times[i])+'.mp4'
        cmd = ['ffmpeg','-ss']
        cmd += [str(round(times[i]-offset-1.1,2))]
        cmd += ['-i',video_file,'-t','2','-c', 'copy', '-vcodec', 'h264','-vf', "pad=1616:1212:160:120:color=black,crop=320:240:"+str(xs[i])+":"+str(ys[i])]
        cmd += ['-y',output_file_name]
        
        print(' '.join(cmd))
        subprocess.check_output(cmd)

        