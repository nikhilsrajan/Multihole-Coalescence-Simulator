import random
import math
import time
import parameterData as param
from simulation import simulation
  
'''
simulator parameters:
---------------------
Nozzle, Fluid, and sheet-settings are selected from the options available in parameterData.py
One may add new nozzle, fluid, sheet-settings as needed by manually adding them to the parameterData.py
as stated in parameterData.py	

'''
nozzleName			= 'Teejet8002'
fluidName			= 'emulsion'
sheetSettingsName	= 'default'

sheetSettings 		= param.sheetSettings[sheetSettingsName] 
nozzle 				= param.nozzle[nozzleName]


'''
simulation parameters:
----------------------
This dicatates how the simulation is to run.

STEPS 			   			: total number of steps in each run
seed_ini, seed_fin 			: range of the seed values given to the randon number generator. It also decides how many epochs of STEPS steps are run
sleep 			   			: how long to pause before the next step is run
initialHoleCount   			: how many holes are present at timestep = 0
holeNucleationRate         	: after how many timesteps should a new holes be nucleated
minHoleCount, maxHoleCount 	: range of the number of holes that are nucleated after every holeNucleationRate timesteps. uniform distribution is assumed for the range
printRate					: after how many timesteps should the details of the simulation be printed on the terminal
graphicsON					: 1 if the simulation should be displayed visually, 0 if not.
isCumulative 				: should the .csv file generated every epoch be cumulative or independent. 1 if cumulative, 0 if independent.

'''
STEPS 				= 100000

seed_ini			= 0
seed_fin			= 19

sleep 				= 0			# unit: seconds

initialHoleCount	= 0		

holeNucleationRate	= 25		# unit: timesteps
minHoleCount		= 1
maxHoleCount		= 2


printRate			= 1000		# unit: timesteps

graphicsON 			= 1

isCumulative		= 1


'''
hole nucleation settings:
-------------------------
This is to set the area where the holes are nucleated, and range between which the nucleated holes radii should lie

'''
distanceMin			= (sheetSettings['section1'] + sheetSettings['section2']) * 2/3		# unit: mm
distanceMax 		= (sheetSettings['section1'] + sheetSettings['section2'])			# unit: mm

angleMin 			= -nozzle['sprayAngle']/2	# unit: deg
angleMax 			= nozzle['sprayAngle']/2	# unit: deg

nucleRadMin			= 0			# unit: mm
nucleRadMax			= 0.5e-3	# unit: mm


'''
simulation
----------

'''

sim = simulation(nozzleName, fluidName, sheetSettingsName)

if isCumulative == 1:
	sim.setIsCumulative1()
else:
	sim.setIsCumulative0()

ru = random.uniform
ri = random.randint
s = math.sin
c = math.cos

def deg2rad(theta): return theta * math.pi / 180

def addRandomHole():
	pivotX, pivotY = sim.getPivotXY()
	r = ru(distanceMin, distanceMax)
	theta = deg2rad(ru(angleMin, angleMax))
	xpos = r*s(theta) + pivotX
	ypos = r*c(theta) + pivotY
	radi = ru(0, 0.5e-3)
	sim.addHole(xpos, ypos, radi)

for seed in range(seed_ini, seed_fin + 1):

	random.seed(seed)

	if graphicsON == 1:
		sim.renderInit()
		sim.setRenderAutoflush1()

		if seed == 0:	
			print('\nPress <ENTER> to start')
			input()

	print('\nSEED: %6d\n------------' % (seed))

	for i in range(initialHoleCount):
		addRandomHole()	

	sim.runInit()

	mul = 1
	dispMul = 0

	for step in range(STEPS):
		if step == mul*holeNucleationRate:
			for i in range(int(ru(minHoleCount,maxHoleCount))):
				addRandomHole()
				mul += 1

		if step == printRate*dispMul:
			print('step: %6d | hCount: %6d | hCCount: %6d | ipCount: %6d | ipCCount: %6d | dropType0Count: %6d' % (step, sim.getLenHoles(), sim.getCumCountHoles(), sim.getLenInteractingPairs(), sim.getCumCountInteractingPairs(), sim.getDropType0Count()))
			dispMul += 1

		sim.runNext()

		if sleep > 0:
			time.sleep(sleep)

	sim.exportDropDiaCountCSV('sim_seed' + str(seed) + '_STEPS' + str(STEPS))
	sim.reset()

print('\nPress <ENTER> to close')
input()
sim.renderStop()