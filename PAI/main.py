#-*- coding:utf-8 -*-
import shutil
import sys
import os
import worker
#
sys.path.append('scripts')
# Utility class
import utils

#

# Parameter input
data = {}
data['temp'] = './temp'
data['result'] = os.path.join(data['temp'],'result')
data['data'] = os.path.join(data['temp'],'data')
data['images'] = './images'
data['cpus'] = 2 #CPUs per task
data['gpus'] = 0 #GPU per task
data['threads'] = 100 #Number of concurrent computations

# Do not modify the following section
data['current'] = os.getcwd()

if(not os.path.exists(data['temp'])):
    os.mkdir(data['temp'])

if(not os.path.exists(data['data'])):
    os.mkdir(data['data'])

if(not os.path.exists(data['result'])):
    os.mkdir(data['result'])

# step 1: Get file image path
images = utils.getAllImages(data['images'])
# step 2: image 2 data
model_data = []
for i,image in enumerate(images):
    job_id,c = utils.image2data(image,data['data'])
    model_data.append((job_id,c))

# step 3:Create all model inputs
shutil.copy("scripts/genModel.py",os.path.join(data['temp'],"genModel.py"))
shutil.copy("scripts/getOdb.py",os.path.join(data['temp'],"getOdb.py"))
os.chdir(data['temp'])

all_jobs = []
for i,md in enumerate(model_data):
    try:
        Job_name = f"Job-{md[0]}.inp"
        # if(os.path.exists(Job_name)):
        #     all_jobs.append(Job_name)
        #     continue
        print(f'Creating model file{i+1}, model name:{Job_name}')
        cmd = 'abaqus cae noGui=genModel.py -- {} {}'.format(md[0],md[1])
        os.system(cmd)
        utils.update(Job_name)
        all_jobs.append(Job_name)
    except BaseException as e:
        pass


# sys.exit(0) ## After commenting out this line, only the INP file will be generated, which can be used to check the model.
print(all_jobs)
# Parallel computation
# Create and start multiple threads
threads = []
count = 1
#//////////////////////////////////
for i in range(data['threads']):
    job_name = all_jobs.pop()
    if(os.path.exists(job_name+'.odb')):
        continue
    thread = worker.Worker(count, job_name, data)
    thread.start()
    threads.append(thread)
    count += 1
    if(len(all_jobs) == 0):
        break

# Monitor thread status
while(True):
    for i,thread in enumerate(threads):
        if(thread.is_alive()):
            continue
        else:
            # Perform post-processing on the extracted results
            thread = threads.pop(i)
            #/////////////////////
            if(len(all_jobs) == 0):
                break
            job_name = all_jobs.pop()
            thread = worker.Worker(count, job_name, data)
            threads.append(thread)
            thread.start()
            count += 1
    if(len(threads) == 0):
        break
print("All Jobs have completed")
#

