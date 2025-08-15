
#-*- coding:utf-8 -*-
import numpy as np
import sys
from odbAccess import *
import os

odbName = sys.argv[-1]
# odbName = 'Job-12'
odb = session.openOdb(name=odbName + ".odb")
rgs = odb.steps['Step-1'].historyRegions
F_data = odb.steps['Step-1'].historyRegions[rgs.keys()[-1]].historyOutputs['RF2'].data
U_data = odb.steps['Step-1'].historyRegions[rgs.keys()[-1]].historyOutputs['U2'].data

data = []
for f,u in zip(F_data,U_data):
	data.append([abs(u[1]),abs(f[1]),0,0])
# out = sys.argv[-1] + ".txt"

#
ns_left = odb.rootAssembly.instances['PART-FINAL-1'].nodeSets['SET-NODE-LEFT']
ns_right = odb.rootAssembly.instances['PART-FINAL-1'].nodeSets['SET-NODE-RIGHT']
fieldU = odb.steps['Step-1'].frames[-1].fieldOutputs['U']
ndFieldU_left = fieldU.getSubset(region=ns_left, position=NODAL).values
ndFieldU_right = fieldU.getSubset(region=ns_right, position=NODAL).values
left = sum([ndFieldU_left[i].data[0] for i in range(len(ndFieldU_left))])/len(ndFieldU_left)
right = sum([ndFieldU_right[i].data[0] for i in range(len(ndFieldU_right))])/len(ndFieldU_right)
#
data[0][2] = left
data[0][3] = right
np.savetxt(os.path.join("result",odbName + ".txt"),data,fmt='%f')