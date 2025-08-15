# -*- coding:utf-8 -*-
import sys

from abaqus import *
from abaqusConstants import *
import math
import numpy as np
# Preprocessing
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=158.338531494141,
    height=92.4791641235352)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
Mdb()
# User-defined parameters
pix_width = 256.
pix_height = 256.
step_time = 0.72
meshSize = 6.0
pattern = [2,2]
block = [25.6,25.6]
layers = 4
depth = 10.
radio = 1.*block[0]/pix_width
displacement = 7.2
# Create model
# N = 12


# N = int(sys.argv[-1])
# baseName = str(sys.argv[-2])

# baseName = "221"
# N = int(sys.argv[-1])
# baseName = str(sys.argv[-2])

N = 65
baseName = "1"
N = int(sys.argv[-1])
baseName = str(sys.argv[-2])

block = np.asarray(block) + np.asarray([.15,.15])
mat_data = {
    'e':32.14,  # 2400.69
    'u':0.47,
    'density':1.08e-09,
    'plastic':[(0.0052, 0.0000),
               (1.6164, 0.0501),
               (2.5323, 0.0833),
               (3.3145, 0.1131),
               (3.4525, 0.1201),
               (3.6132, 0.1297),
               (3.8275, 0.1445),
               (4.0865, 0.1638),
               (4.3914, 0.1889),
               (4.7421, 0.2212),
               (5.0385, 0.2515),
               (6.8678, 0.4755),
               (7.7982, 0.5989),
               (8.6309, 0.7094),
               (9.3134, 0.8069)]
}
for i in range(N):

    try:
        data = np.loadtxt('data/{}_{}.txt'.format(baseName,i+1))*(radio+0.001)
        approx = data.tolist()
        approx.append(data[0])

        s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
            sheetSize=200.0)
        g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
        s.setPrimaryObject(option=STANDALONE)

        # s.Spline(points=approx)
        for j in range(len(approx)-1):
            pt1,pt2 = approx[j],approx[j+1]
            s.Line(point1=pt1, point2=pt2)

        session.viewports['Viewport: 1'].view.setValues(width=135.349, height=74.4681,
            cameraPosition=(0.406673, 1.59753, 188.562), cameraTarget=(0.406673,
            1.59753, 0))
        p = mdb.models['Model-1'].Part(name='Part-{}'.format(i+1), dimensionality=THREE_D,
                                       type=DEFORMABLE_BODY)
        p = mdb.models['Model-1'].parts['Part-{}'.format(i+1)]
        p.BaseShell(sketch=s)
        s.unsetPrimaryObject()
        p = mdb.models['Model-1'].parts['Part-{}'.format(i+1)]
        #print('part-{}'.format(i+1))
        session.viewports['Viewport: 1'].setValues(displayedObject=p)
        del mdb.models['Model-1'].sketches['__profile__']
    except:
        pass

#plate
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
    sheetSize=200.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.rectangle(point1=(0.0, 0.0), point2=block)
session.viewports['Viewport: 1'].view.setValues(nearPlane=179.688,
    farPlane=197.436, width=36.0144, height=19.8149, cameraPosition=(1.1164,
    -3.68278, 188.562), cameraTarget=(1.1164, -3.68278, 0))
p = mdb.models['Model-1'].Part(name='Part-plate', dimensionality=THREE_D,
                               type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-plate']
p.BaseShell(sketch=s1)
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-plate']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']


#part top
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
    sheetSize=200.0)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(-20., block[0]*pattern[0]), point2=(block[0]*pattern[0]+20., block[0]*pattern[1]))  # Adjust the length of the rigid plate
s1.HorizontalConstraint(entity=g[2], addUndoState=False)
session.viewports['Viewport: 1'].view.setValues(width=136.493, height=74.4681,
    cameraPosition=(-1.86127, 0.950254, 188.562), cameraTarget=(-1.86127,
    0.950254, 0))
p = mdb.models['Model-1'].Part(name='Part-top', dimensionality=THREE_D,
    type=DISCRETE_RIGID_SURFACE)
p = mdb.models['Model-1'].parts['Part-top']
p.AnalyticRigidSurfExtrude(sketch=s1, depth=depth+16.)  # Adjust the width of the rigid plate
s1.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-top']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']
session.viewports['Viewport: 1'].view.setValues(nearPlane=251.709,
    farPlane=565.13, width=353.359, height=192.786, cameraPosition=(259.714,
    254.543, 221.271), cameraTarget=(23.913, 18.7418, -14.5298))
p = mdb.models['Model-1'].parts['Part-top']
v1, e, d1, n = p.vertices, p.edges, p.datums, p.nodes
p.ReferencePoint(point=p.InterestingPoint(edge=e[0], rule=MIDDLE))

#######


# Assembly
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-plate']
a.Instance(name='Part-plate-1', part=p, dependent=ON)

cuts = []
for i in range(N):
    p = mdb.models['Model-1'].parts['Part-{}'.format(i+1)]
    a.Instance(name='Part-{}-1'.format(i+1), part=p, dependent=ON)
    cuts.append(a.instances['Part-{}-1'.format(i+1)])


# bool
a = mdb.models['Model-1'].rootAssembly
a = mdb.models['Model-1'].rootAssembly
a.InstanceFromBooleanCut(name='Part-model',
    instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-plate-1'],
    cuttingInstances=cuts, originalInstances=DELETE)

# Array
a = mdb.models['Model-1'].rootAssembly
a.LinearInstancePattern(instanceList=('Part-model-1', ), direction1=(1.0, 0.0,
    0.0), direction2=(0.0, 1.0, 0.0), number1=pattern[0], number2=pattern[1], spacing1=block[0],
    spacing2=block[1])

ins = []
a = mdb.models['Model-1'].rootAssembly
for i in range(int(pattern[0])):
    for j in range(int(pattern[1])):
        if(i==0 and j == 0):
            name = "Part-model-1"
        else:
            name = 'Part-model-1-lin-{}-{}'.format(i+1,j+1)
        ins.append(a.instances[name])
a.InstanceFromBooleanMerge(name='Part-final', instances=ins, originalInstances=DELETE, domain=GEOMETRY)

#/ mesh
p = mdb.models['Model-1'].parts['Part-final']
p.seedPart(size=0.59, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-final']
p.seedPart(size=meshSize, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-final']
f = p.faces
pickedRegions = f.getSequenceFromMask(mask=('[#1 ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=TRI)
p = mdb.models['Model-1'].parts['Part-final']
p.generateMesh()
#
p = mdb.models['Model-1'].parts['Part-top']
p.seedPart(size=meshSize, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-top']
p.seedPart(size=4.0, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Part-top']
p.generateMesh()

# # 2D TO 3D
p = mdb.models['Model-1'].parts['Part-final']
s = p.elements
p.generateMeshByOffset(region=regionToolset.Region(
    side1Elements=p.elements), meshType=SOLID, totalThickness=float(depth*1.),  # 1./layers
    numLayers=layers, offsetDirection=OUTWARD)

# p = mdb.models['Model-1'].parts['Part-final']
# e = p.elementFaces
# pickedElemFacesSourceSide = e.getSequenceFromMask(mask=('[#1010101:6763 ]', ),
#     )
# vector =((0.0, 0.0, 0.0), (0.0, 0.0, 1.0*depth))
# p.generateBottomUpExtrudedMesh(elemFacesSourceSide=pickedElemFacesSourceSide,
#     extrudeVector=vector, numberOfLayers=layers, biasRatio=.0)
# p = mdb.models['Model-1'].parts['Part-final']
# p.Set(elements=p.elements, name='BottomUpElements-1')


#

a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-top']
a.Instance(name='Part-top-1', part=p, dependent=ON)
a.translate(instanceList=('Part-top-1', ), vector=(0.0, 0.0, 4.0))
a.translate(instanceList=('Part-top-1', ), vector=(0.0, 0.01, 0))  # Distance between the upper rigid plate and the structure

a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-top']
a.Instance(name='Part-top-2', part=p, dependent=ON)
a.translate(instanceList=('Part-top-2', ), vector=(0.0, -pattern[1]*block[1] - 0.01, 0))
a.translate(instanceList=('Part-top-2', ), vector=(0.0, 0.0, 4.0))
#material
mdb.models['Model-1'].Material(name='Material-1')
mdb.models['Model-1'].materials['Material-1'].Density(table=((mat_data['density'], ), ))
mdb.models['Model-1'].materials['Material-1'].Elastic(table=((mat_data['e'], mat_data['u']), ))
mdb.models['Model-1'].materials['Material-1'].Plastic(table=mat_data['plastic'])

# section
mdb.models['Model-1'].HomogeneousSolidSection(name='Section-1',
    material='Material-1', thickness=None)

# assign material
p = mdb.models['Model-1'].parts['Part-final']
region = regionToolset.Region(elements=p.elements)
p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0,
    offsetType=MIDDLE_SURFACE, offsetField='',
    thicknessAssignment=FROM_SECTION)

# Interaction
mdb.models['Model-1'].ContactProperty('IntProp-1')
mdb.models['Model-1'].interactionProperties['IntProp-1'].TangentialBehavior(
    formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF,
    pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((
    0.2, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION,
    fraction=0.005, elasticSlipStiffness=None)
mdb.models['Model-1'].interactionProperties['IntProp-1'].NormalBehavior(
    pressureOverclosure=HARD, allowSeparation=ON,
    constraintEnforcementMethod=DEFAULT)

# Establish contact
mdb.models['Model-1'].ContactExp(name='Int-1', createStepName='Initial')
mdb.models['Model-1'].interactions['Int-1'].includedPairs.setValuesInStep(
    stepName='Initial', useAllstar=ON)
mdb.models['Model-1'].interactions['Int-1'].contactPropertyAssignments.appendInStep(
    stepName='Initial', assignments=((GLOBAL, SELF, 'IntProp-1'), ))
#
#

#
a = mdb.models['Model-1'].rootAssembly
p = mdb.models['Model-1'].parts['Part-final']
nodes = p.nodes
bottom_nodes = None
left_nodes = None
right_nodes = None

for i,node in enumerate(nodes):
    if(node.coordinates[1] == 0):
        if(bottom_nodes == None):
            bottom_nodes = nodes[i:i+1]
        else:
            bottom_nodes += nodes[i:i+1]

    if(abs(node.coordinates[0])<=1e-3 and node.coordinates[2] == depth):
        if(left_nodes == None):
            left_nodes = nodes[i:i+1]
        else:
            left_nodes += nodes[i:i+1]

    if(abs(node.coordinates[0] - sum(block))<= 1e-3 and node.coordinates[2] == depth):
        if(right_nodes == None):
            right_nodes = nodes[i:i+1]
        else:
            right_nodes += nodes[i:i+1]
p.Set(nodes=bottom_nodes, name='Set-node-bottom')
p.Set(nodes=left_nodes, name='Set-node-left')
p.Set(nodes=right_nodes, name='Set-node-right')
#


# step

a = mdb.models['Model-1'].rootAssembly
r1 = a.instances['Part-top-1'].referencePoints
refPoints1=(r1[r1.keys()[-1]], )
a.Set(referencePoints=refPoints1, name='Set-res')


mdb.models['Model-1'].ExplicitDynamicsStep(name='Step-1', previous='Initial',
    timePeriod=step_time, massScaling=((SEMI_AUTOMATIC, MODEL, THROUGHOUT_STEP, 0.0,
    7.8e-05, BELOW_MIN, 1, 0, 0.0, 0.0, 0, None), ))

# session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
# regionDef=mdb.models['Model-1'].rootAssembly.sets['Set-res']
# mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2',
#     createStepName='Step-1', variables=('U', 'UT', 'RF', 'RT'),
#     region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)

regionDef=mdb.models['Model-1'].rootAssembly.sets['Set-res']
mdb.models['Model-1'].historyOutputRequests['H-Output-1'].setValues(variables=(
    'U1', 'U2', 'U3', 'UR1', 'UR2', 'UR3', 'UT', 'UR', 'RF1', 'RF2', 'RF3',
    'RM1', 'RM2', 'RM3', 'RT', 'ALLAE', 'ALLCD', 'ALLDMD', 'ALLFD', 'ALLIE',
    'ALLKE', 'ALLPD', 'ALLSE', 'ALLVD', 'ALLWK', 'ETOTAL'), region=regionDef,
    sectionPoints=DEFAULT, rebar=EXCLUDE)
# left output
regionDef=mdb.models['Model-1'].rootAssembly.allInstances['Part-final-1'].sets['Set-node-left']
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2',
    createStepName='Step-1', variables=('U', ), region=regionDef,
    sectionPoints=DEFAULT, rebar=EXCLUDE)
#right output
regionDef=mdb.models['Model-1'].rootAssembly.allInstances['Part-final-1'].sets['Set-node-right']
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-3',
    createStepName='Step-1', variables=('U', ), region=regionDef,
    sectionPoints=DEFAULT, rebar=EXCLUDE)
# BC condition
a = mdb.models['Model-1'].rootAssembly
region = a.instances['Part-final-1'].sets['Set-node-bottom']
mdb.models['Model-1'].EncastreBC(name='BC-bottom-nodes', createStepName='Initial',
    region=region, localCsys=None)


a = mdb.models['Model-1'].rootAssembly
r1 = a.instances['Part-top-2'].referencePoints
refPoints1=(r1[r1.keys()[-1]], )
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].EncastreBC(name='BC-bottom', createStepName='Initial',
    region=region, localCsys=None)


mdb.models['Model-1'].TabularAmplitude(name='Amp-1', timeSpan=STEP,
    smooth=SOLVER_DEFAULT, data=((0.0, 0.0), (step_time, 1.0)))

a = mdb.models['Model-1'].rootAssembly
r1 = a.instances['Part-top-1'].referencePoints
refPoints1=(r1[r1.keys()[-1]], )
region = regionToolset.Region(referencePoints=refPoints1)
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='Step-1',
    region=region, u1=0.0, u2=-displacement, u3=0.0, ur1=0.0, ur2=0.0, ur3=0.0,
    amplitude='Amp-1', fixed=OFF, distributionType=UNIFORM, fieldName='',
    localCsys=None)
# create job
jobName = "Job-" + baseName
mdb.Job(name=jobName, model='Model-1', description='', type=ANALYSIS,
    atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
    memoryUnits=PERCENTAGE, explicitPrecision=SINGLE,
    nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF,
    contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='',
    resultsFormat=ODB, parallelizationMethodExplicit=DOMAIN, numDomains=1,
    activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1)

mdb.jobs[jobName].writeInput(consistencyChecking=OFF)