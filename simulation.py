from hole import hole
from interactingPair import interactingPair

import math as math
import graphics as gfx
import parameterData as param
import copy

class simulation:
	def __init__(self, nozzleName = 'Teejet8002', fluidName = 'emulsion', sheetSettings = 'default'):
		# Data Members
		self.__holes 						= []
		self.__dictHoles 					= {}	# uid: index
		self.__lenHoles						= 0
		self.__cumCountHoles 				= 0
		self.__interactingPairs 			= []
		self.__dictInteractingPairs 		= {}	# uid: index
		self.__lenInteractingPairs 			= 0
		self.__cumCountInteractingPairs 	= 0
		self.__defaultNozzle				= 'Teejet8002'
		self.__defaultFluid					= 'emulsion'
		self.__defaultSheetSettings			= 'default'
		self.__dropDiaCount					= []
		self.__dropDiaDict					= {}
		self.__lenDropDiaCount 				= 0
		self.__dropType0Count				= 0
		self.__isCumulative					= 0
		
		self.__renderShapelist 				= []
		self.__renderDictHoles 				= {}	# uid: index
		self.__renderDictInteractingPairs 	= {}	# uid: index
		
		self.__timestep						= 0
		self.__time 						= 0
		self.__timePertimestep 				= 1e-6

		self.__nozzle 						= param.nozzle[self.__defaultNozzle]
		self.__fluid 						= param.fluid[self.__defaultFluid]
		self.__SheetSettings 				= param.sheetSettings[self.__defaultSheetSettings]

		self.setNozzle(nozzleName)
		self.setFluid(fluidName)
		self.setSheetSettings(sheetSettings)

		# Physics Parameters
		self.__collapseThreshold 			= 100 								# unit: timesteps
		self.__distanceRadiusRatioThreshold	= 0.1								
		self.__largeHoleMul					= 0.75
		self.__sheetBreakupLength 			= self.computeSheetBreakupLength() 	# unit: mm
		self.__pivotX						= 0
		self.__pivotY 						= 0

		# Render Parameters
		self.__renderYes 					= 0 								# canvas is ready ? (renderInit)
		self.__renderAutoflush 				= 0
		self.__renderX 						= 720
		self.__renderY 						= 720
		self.__renderColourWater 			= gfx.color_rgb(0,168,230)
		self.__renderColourHole 			= gfx.color_rgb(0,0,0)
		self.__renderLigamentWidth 			= 1
		self.__renderMarginPercentage		= 5
		self.__renderTransformX 			= self.computeRenderTransformX()  	# (m, c) : (slope, constant)
		self.__renderTransformY 			= self.computeRenderTransformY()  	# (m, c) : (slope, constant)
		self.__renderLenShapelist		 	= 0
		self.__renderWaterCircle			= self.makeRenderWaterCircle()
		self.__renderSectorMask				= self.makeRenderSectorMask()
		self.__renderFrameRefreshRate		= 25								# unit: timesteps
		self.__renderFrameRefreshMul		= 0



	def getLenHoles(self): 					return self.__lenHoles
	def getCumCountHoles(self): 			return self.__cumCountHoles
	def getLenInteractingPairs(self): 		return self.__lenInteractingPairs
	def getCumCountInteractingPairs(self): 	return self.__cumCountInteractingPairs
	def getTimestep(self): 					return self.__timestep
	def getTime(self):						return self.__time
	def getNozzle(self): 					return self.__nozzle
	def getNozzleName(self): 				return self.__nozzle['name']
	def getFluid(self): 					return self.__fluid
	def getFluidName(self): 				return self.__fluid['name']
	def getSheetSettings(self): 			return self.__sheetSettings
	def getSheetSettingsName(self): 		return self.__sheetSettings['name']
	def computeSheetBreakupLength(self):	return self.__sheetSettings['section1'] + self.__sheetSettings['section2'] + self.__sheetSettings['section3'] 
	def getPivotXY(self):					return self.__pivotX, self.__pivotY
	def getDropType0Count(self):			return self.__dropType0Count
	def getIsCumulative(self):				return self.__isCumulative

	def setNozzle(self, nozzleName):
		try:
			self.__nozzle = param.nozzle[nozzleName]
		except:
			print('WARNING --', nozzleName, 'not found, setting default nozzle:', self.__defaultNozzle)
			self.__nozzle = param.nozzle[self.__defaultNozzle]

	def setFluid(self, fluidName):
		try:
			self.__fluid = param.fluid[fluidName]
		except:
			print('WARNING --', fluidName, 'not found, setting default fluid:', self.__defaultFluid)
			self.__fluid = param.fluid[self.__defaultFluid]

	def setSheetSettings(self, sheetSettingsName):
		try:
			self.__sheetSettings = param.sheetSettings[sheetSettingsName]
		except:
			print('WARNING --', sheetSettingsName, 'not found, setting default sheetSettings:', self.__defaultSheetSettings)
			self.__sheetSettings = param.sheetSettings[self.__defaultSheetSettings]

	def setIsCumulative0(self): self.__isCumulative = 0
	def setIsCumulative1(self): self.__isCumulative = 1

	def computeSheetThicknessAt(self, x, y):
		sprayParameter = self.__nozzle['sprayParameter'] * 1e6 # unit: m sq -> mm sq
		distanceFromNozzle = math.sqrt((x - self.__pivotX)*(x - self.__pivotX) + (y - self.__pivotY)*(y - self.__pivotY))
		sheetThickness = sprayParameter / distanceFromNozzle
		return sheetThickness 	# unit: mm

	def computeRenderTransformX(self):
		def deg2rad(theta):
			return theta*math.pi/180

		R = self.__sheetBreakupLength
		theta = deg2rad(self.__nozzle['sprayAngle']/2)

		renderMin = min(self.__renderX, self.__renderY)
		lengthMax = max(R, 2*R*math.sin(theta))
		margin = renderMin*self.__renderMarginPercentage/100

		def computeSlopeIntercept(x0, y0, x1, y1):
			m = (y0 - y1)/(x0 - x1)
			c = (y1*x0 - y0*x1)/(x0 - x1)

			return (m, c)

		x0 = self.__pivotX
		y0 = self.__renderX/2
		x1 = -lengthMax/2 + self.__pivotX
		y1 = self.__renderX/2 - (renderMin/2 - margin)

		return computeSlopeIntercept(x0, y0, x1, y1)

	def computeRenderTransformY(self):
		def deg2rad(theta):
			return theta*math.pi/180

		R = self.__sheetBreakupLength
		theta = deg2rad(self.__nozzle['sprayAngle']/2)

		renderMin = min(self.__renderX, self.__renderY)
		lengthMax = max(R, 2*R*math.sin(theta))
		margin = renderMin*self.__renderMarginPercentage/100

		def computeSlopeIntercept(x0, y0, x1, y1):
			m = (y0 - y1)/(x0 - x1)
			c = (y1*x0 - y0*x1)/(x0 - x1)

			return (m, c)

		x0 = self.__pivotY
		y0 = self.__renderY/2 - (renderMin/2 - margin)
		x1 = lengthMax/2 + self.__pivotY
		y1 = self.__renderY/2

		return computeSlopeIntercept(x0, y0, x1, y1)

	def setCollapseThresholdTo(self, threshold): self.__collapseThreshold = threshold

	def sim2renderCS(self, x, y):
		(mX, cX) = self.__renderTransformX
		(mY, cY) = self.__renderTransformY

		renderX = mX*x + cX
		renderY = mY*y + cY

		return renderX, renderY

	def sim2renderNorm(self, norm):
		oX, oY = self.sim2renderCS(0, 0)
		rX, rY = self.sim2renderCS(0, norm)
		pX, pY = rX - oX, rY - oY
		renderNorm = math.sqrt(pX*pX + pY*pY)
		return renderNorm

	def setRenderAutoflush1(self): 
		self.__renderAutoflush = 1
		if self.__renderYes == 0:
			print('warning: render not initialised')

	def setRenderAutoflush0(self): self.__renderAutoflush = 0

	def updateDictPostPop(self, dictionary, index):
		for key in dictionary.keys():
			if dictionary[key] > index:
				dictionary[key] -= 1

	def addHole(self, x_ini, y_ini, radius, velx = 0, vely = 0):
		holeUID = self.__cumCountHoles
		holeIndex = self.__lenHoles

		self.__holes.append(hole(x_ini, y_ini, radius, self.__timestep, 1, holeUID, velx, vely))
		self.__dictHoles[holeUID] = holeIndex
		self.addInteractingPairsForHoleIndex(holeIndex)

		if self.__renderAutoflush == 1:
			shapelistIndex = self.__renderLenShapelist
			self.__renderShapelist.append(gfx.Circle(gfx.Point(x_ini, y_ini), radius))
			self.__renderShapelist[shapelistIndex].setFill(self.__renderColourHole)
			self.__renderDictHoles[holeUID] = shapelistIndex
			self.__renderLenShapelist += 1
			if self.__renderYes == 0:
				print('render not initialised')
			else:
				self.__renderShapelist[shapelistIndex].draw(self.__renderCanvas)

		self.__cumCountHoles += 1
		self.__lenHoles += 1

		return holeUID

	def popHoleByIndex(self, holeIndex):
		if  holeIndex >= self.__lenHoles or holeIndex < 0:
			print('invalid holeIndex')
			return 0

		holeUID = self.__holes[holeIndex].getID()
		
		if self.__renderAutoflush == 1:
			shapelistIndex = self.__renderDictHoles[holeUID]
			if self.__renderYes == 0:
				print('render not initialised')
			else:
				self.__renderShapelist[shapelistIndex].undraw()
			self.__renderDictHoles.pop(holeUID)
			self.updateDictPostPop(self.__renderDictHoles, shapelistIndex)
			self.__renderShapelist.pop(shapelistIndex)
			self.__renderLenShapelist -= 1

		self.popInteractingPairsForHoleIndex(holeIndex)

		self.__dictHoles.pop(holeUID)
		self.updateDictPostPop(self.__dictHoles, holeIndex)
		self.__holes.pop(holeIndex)
		self.__lenHoles -= 1

		# print('hole', holeUID, 'POPPED --', 'holes len :', len(self.__holes))  ## DEBUG

		return 1

	def isHolesInteracting(self, hole_A, hole_B):
		xA, yA = hole_A.getPosXY()
		rA = hole_A.getRadius()
		xB, yB = hole_B.getPosXY()
		rB = hole_B.getRadius()
		
		d = math.sqrt((xA - xB)*(xA - xB) + (yA - yB)*(yA - yB))

		DRR = d / (rA + rB)

		if DRR <= self.__distanceRadiusRatioThreshold:
			return -3

		if rA + rB > d:  # if the holes overlap more than just a single point, then YES they are interacting, else NO
			if rA + d <= rB:  # if hole_A is completely sucked in by hole_B, then POP smaller hole_A
				return -1
			
			if rB + d <= rA: # if hole_B is completely sucked in by hole_A, then POP smaller hole_B
				return -2

			return 1
		else:
			return 0

	def addDropDiaCount(self, dropDia, count, dropType):
		if dropDia in self.__dropDiaDict:
			dropDiaIndex = self.__dropDiaDict[dropDia]
			self.__dropDiaCount[dropDiaIndex] += count
		else:
			self.__dropDiaDict[dropDia] = self.__lenDropDiaCount
			self.__dropDiaCount.append(count)
			self.__lenDropDiaCount += 1

		if dropType == 0:
			self.__dropType0Count += 1

	def exportDropDiaCountCSV(self, filename = 'dropDiaCount'):
		newfilename = filename
		fileAlreadyPresent = 1
		tried = 0

		while fileAlreadyPresent == 1:
			try:
				testOpen = open(newfilename + '.csv', 'r')
				tried += 1
				testOpen.close()
				newfilename = filename + ' (' + str(tried) + ')'
			except:
				fileAlreadyPresent = 0

		with open(newfilename + '.csv', 'w') as writeFile:
			for dropDia, index in self.__dropDiaDict.items():
				count = self.__dropDiaCount[index]
				string = str(dropDia) + ',' + str(count) + '\n'

				try:
					writeFile.writelines(string)
				except:
					return 0

		return 1

	def addInteractingPair(self, hole_A, hole_B):
		for (holeUID, interactingPairUID) in hole_A.getInteractingWith():
			if hole_B.getID() == holeUID:
				return -1

		interactingPairUID = self.__cumCountInteractingPairs
		interactingPairIndex = self.__lenInteractingPairs

		hole_A.addInteractingWith((hole_B.getID(), interactingPairUID))
		hole_B.addInteractingWith((hole_A.getID(), interactingPairUID))

		self.__interactingPairs.append(interactingPair(hole_A, hole_B, self.__timestep, interactingPairUID))
		self.__dictInteractingPairs[interactingPairUID] = interactingPairIndex
		
		if self.__renderAutoflush == 1:
			shapelistIndex = self.__renderLenShapelist
			x1, y1, x2, y2 = self.__interactingPairs[interactingPairIndex].computeLigamentXYXY()
			self.__renderShapelist.append(gfx.Line(gfx.Point(x1, y1), gfx.Point(x2, y2)))
			self.__renderLenShapelist += 1
			self.__renderShapelist[shapelistIndex].setOutline(self.__renderColourWater)
			self.__renderShapelist[shapelistIndex].setWidth(self.__renderLigamentWidth)
			self.__renderDictInteractingPairs[interactingPairUID] = shapelistIndex
			if self.__renderYes == 0:
				print('render not initialised')
			else:
				self.__renderShapelist[shapelistIndex].draw(self.__renderCanvas)

		self.__cumCountInteractingPairs += 1
		self.__lenInteractingPairs += 1

		return interactingPairUID

	def popInteractingPairIndex(self, interactingPairIndex):
		if interactingPairIndex >= self.__lenInteractingPairs or interactingPairIndex < 0:
			print('invalid interactingPairIndex')
			return 0

		#self.__interactingPairs[interactingPairIndex].setPairStatus(0)
		interactingPairUID = self.__interactingPairs[interactingPairIndex].getID()
		
		A = self.__interactingPairs[interactingPairIndex].getHoleA()
		B = self.__interactingPairs[interactingPairIndex].getHoleB()
		
		self.__holes[self.__dictHoles[A.getID()]].popInteractingWith((B.getID(), interactingPairUID))
		self.__holes[self.__dictHoles[B.getID()]].popInteractingWith((A.getID(), interactingPairUID))

		if self.__renderAutoflush == 1:
			shapelistIndex = self.__renderDictInteractingPairs[interactingPairUID]
			if self.__renderYes == 0:
				print('render not initialised')
			else:
				self.__renderShapelist[shapelistIndex].undraw()

			self.__renderShapelist.pop(shapelistIndex)
			self.updateDictPostPop(self.__renderDictInteractingPairs, shapelistIndex)
			self.__renderLenShapelist -= 1

		self.__dictInteractingPairs.pop(interactingPairUID)
		self.updateDictPostPop(self.__dictInteractingPairs, interactingPairIndex)
		self.__interactingPairs.pop(interactingPairIndex)
		self.__lenInteractingPairs -= 1

		# print('interacting pair', interactingPairUID, 'POPPED --', 'interactingPairs len :', len(self.__interactingPairs))  ## DEBUG

		return 1

	def updateInteractingPairsInteraction(self):
		interactingPairIndex = 0
		while interactingPairIndex < self.__lenInteractingPairs:
			A = self.__interactingPairs[interactingPairIndex].getHoleA()
			B = self.__interactingPairs[interactingPairIndex].getHoleB()
			
			if self.isHolesInteracting(A, B) == 0:
				# print('interacting pair POP case: no more interaction')  ## DEBUG
				self.popInteractingPairIndex(interactingPairIndex)
			else:
				interactingPairIndex += 1

		for holeAIndex in range(self.__lenHoles - 1):
			if self.__holes[holeAIndex].getStatus() == 1:
				for holeBIndex in range(holeAIndex + 1, self.__lenHoles):
					if self.__holes[holeBIndex].getStatus() == 1:
						A = self.__holes[holeAIndex]
						B = self.__holes[holeBIndex]

						if self.isHolesInteracting(A, B) == 1:
							''' Hole A and hole B are intersecting forming an interacting pair '''
							self.addInteractingPair(A, B)

						if self.isHolesInteracting(A, B) == -1:
							''' Hole A is completely inside hole B, thus assumed to be absorbed by hole B '''
							self.__holes[holeAIndex].setStatus(0)

						if self.isHolesInteracting(A, B) == -2:
							''' Hole B is completely inside hole A, thus assumed to be absorbed by hole A '''
							self.__holes[holeBIndex].setStatus(0)

						if self.isHolesInteracting(A, B) == -3:
							''' DDR of hole A is too below threshold, thus it is assumed to be absorbed by hole B '''
							self.__holes[holeAIndex].setStatus(0)

	def updateInteractingPairsStatus(self):
		for interactingPairIndex in range(self.__lenInteractingPairs):
			if self.__interactingPairs[interactingPairIndex].getStatus() == 1:  # if the interacting pair's ligament still intact, then continue
				t_init_i = self.__interactingPairs[interactingPairIndex].getBirthtime()				
				distanceRadiusRatio = self.__interactingPairs[interactingPairIndex].computeDistanceRadiusRatio()

				if self.__timestep - t_init_i >= self.__collapseThreshold or distanceRadiusRatio <= self.__distanceRadiusRatioThreshold:
					self.__interactingPairs[interactingPairIndex].setStatus(0)
					
					if self.__interactingPairs[interactingPairIndex].getHoleAStatus() == 1 and self.__interactingPairs[interactingPairIndex].getHoleBStatus() == 1:
						self.__interactingPairs[interactingPairIndex].setPairStatus(-4)
					
					elif self.__interactingPairs[interactingPairIndex].getHoleAStatus() == -4:
						self.__interactingPairs[interactingPairIndex].setHoleBStatus(1)
					
					elif self.__interactingPairs[interactingPairIndex].getHoleBStatus() == -4:
						self.__interactingPairs[interactingPairIndex].setHoleAStatus(1)
			
	def addInteractingPairsForHoleIndex(self, holeAIndex):
		for holeBIndex in range(self.__lenHoles):
			if self.__holes[holeBIndex].getStatus() == 1:
				if holeBIndex != holeAIndex:
					A = self.__holes[holeAIndex]
					B = self.__holes[holeBIndex]

					if self.isHolesInteracting(A, B) == 1:
						self.addInteractingPair(A, B)

					if self.isHolesInteracting(A, B) == -1:
						self.__holes[holeAIndex].setStatus(0)

					if self.isHolesInteracting(A, B) == -2:
						self.__holes[holeBIndex].setStatus(0)

					if self.isHolesInteracting(A, B) == -3:
						self.__holes[holeAIndex].setStatus(0)

	def popInteractingPairsForHoleIndex(self, holeIndex):
		interactingWithList = copy.deepcopy(self.__holes[holeIndex].getInteractingWith())
		for (holeUID, interactingPairUID) in interactingWithList:
			interactingPairIndex = self.__dictInteractingPairs[interactingPairUID]
			self.popInteractingPairIndex(interactingPairIndex)

	def popCollapsedInteractingPairs(self):
		interactingPairIndex = 0
		while(interactingPairIndex < self.__lenInteractingPairs):
			if self.__interactingPairs[interactingPairIndex].getHoleAStatus() == -4 and self.__interactingPairs[interactingPairIndex].getHoleBStatus() == -4:
				x_ini, y_ini, radius, velx, vely = self.__interactingPairs[interactingPairIndex].computeResHole()
				res_holeUID = self.addHole(x_ini, y_ini, radius, velx, vely)
				res_holeIndex = self.__dictHoles[res_holeUID]
				dropDia, count, dropType = self.__interactingPairs[interactingPairIndex].computeDropDiaAndCount(self.computeSheetThicknessAt(x_ini, y_ini))

				self.popInteractingPairIndex(interactingPairIndex)
				self.addDropDiaCount(dropDia, count, dropType)
				
			elif self.__interactingPairs[interactingPairIndex].getHoleAStatus() != 1 or self.__interactingPairs[interactingPairIndex].getHoleBStatus() != 1:
				self.popInteractingPairIndex(interactingPairIndex)
			
			else:
				interactingPairIndex += 1

	def popInactiveHoles(self):
		holeIndex = 0
		while holeIndex < self.__lenHoles:
			if self.__holes[holeIndex].getStatus() != 1:
				self.popHoleByIndex(holeIndex)
			else:
				holeIndex += 1

	def updateHolesStatusForLargeHoles(self):
		for holeIndex in range(self.__lenHoles):
			if self.__holes[holeIndex].getStatus() == 1:
				if self.__holes[holeIndex].getRadius() >= self.__largeHoleMul * self.__sheetBreakupLength:
					self.__holes[holeIndex].setStatus(0)

	def actionHoles(self):
		'''
		Action Holes -- Sheet Breakup ver 1
		-----------------------------------
		Only the interaction between holes are considered for droplet formation.
		Interaction with the hole and the sheet boundary is ignored.

		...

		Step 1: Remove all set the holes lying outside the sheet to status 0.

		'''
		def getHoleStatusByLocationOnSheet(holeX, holeY, holeR):
			nozzleX = self.__pivotX
			nozzleY = self.__pivotY
			nozzleR = self.__sheetBreakupLength
			nozzleTheta = self.__nozzle['sprayAngle']

			cX, cY = holeX - nozzleX, holeY - nozzleY
			pX, pY = 0, nozzleR

			def norm2(x, y):
				return math.sqrt(x*x + y*y)

			D = norm2(cX, cY)
			R = norm2(pX, pY)

			if D >= R + holeR:
				return 0

			def rad2deg(angle): return 180 / math.pi * angle

			phi = rad2deg(math.asin(holeR / D))
			alpha = rad2deg(math.acos((cX*pX + cY*pY) / (D * R)))

			if alpha >= nozzleTheta / 2 + phi:
				return 0

			return 1

		for holeIndex in range(self.__lenHoles):
			if self.__holes[holeIndex].getStatus() == 1:
				holeX, holeY = self.__holes[holeIndex].getPosXY()
				holeR = self.__holes[holeIndex].getRadius()

				status = getHoleStatusByLocationOnSheet(holeX, holeY, holeR)

				if status == 0:
					self.__holes[holeIndex].setStatus(0)

		'''
		Step 2: Move and increase the hole radius

		'''
		nozzleArea 			= self.__nozzle['orificeWidth'] * self.__nozzle['orificeHeight']  	# unit: mm sq
		nozzleFlowrate 		= self.__nozzle['flowrate'] * 1e9 / (264.172 * 60)					# unit: gpm -> mm cb per s
		fluidDensity 		= self.__fluid['density'] * 1e-6									# unit: kg per m cb -> g per mm cb
		fluidVelocity 		= nozzleFlowrate / (nozzleArea)										# unit: mm per s
		fluidSurfaceTension = self.__fluid['surfaceTension']									# unit: mN per m -> N (mm-g-s) per mm

		for holeIndex in range(self.__lenHoles):
			if self.__holes[holeIndex].getStatus() == 1:
				holeX, holeY = self.__holes[holeIndex].getPosXY()
				nozzleX, nozzleY = self.__pivotX, self.__pivotY
				
				cX, cY = holeX - nozzleX, holeY - nozzleY

				def norm2(x, y):
					return math.sqrt(x*x + y*y)

				D = norm2(cX, cY)

				velX = cX/D * fluidVelocity
				velY = cY/D * fluidVelocity

				self.__holes[holeIndex].setVelXY(velX, velY)

				self.__holes[holeIndex].move(self.__timePertimestep)

				sheetThickness = self.computeSheetThicknessAt(holeX, holeY) 	# unit: mm	

				taylorCulickVelocity = math.sqrt((2 * fluidSurfaceTension) / (fluidDensity * sheetThickness)) 	# unit: mm per s
				
				dr = taylorCulickVelocity * self.__timePertimestep

				self.__holes[holeIndex].incrementRadiusBy(dr)


	def runInit(self):
		self.__renderAutoflush = 0

	def runNext(self):
		self.__timestep += 1
		self.__time += self.__timePertimestep
		self.actionHoles()
		self.updateInteractingPairsInteraction()
		self.updateInteractingPairsStatus()
		self.popCollapsedInteractingPairs()
		self.updateHolesStatusForLargeHoles()
		self.popInactiveHoles()

		if(self.__renderYes == 1):
			self.renderDrawAll()

	def renderInit(self):
		self.__renderYes = 1
		self.__renderCanvas = gfx.GraphWin("screen", self.__renderX, self.__renderY)
		self.__renderCanvas.setBackground(self.__renderColourHole)
		self.renderDrawSheet()

	def viewHoles(self):
		print("")
		print("----------------------holes-------------------------")
		print("  index       id   status     velx     vely   radius")
		print("----------------------------------------------------")
		for i in range(self.__lenHoles):
			h_i = self.__holes[i]
			velx, vely = h_i.getVelXY()
			print("%7d  %7d  %7d  %1.7f  %1.7f  %2.5f" % (i, h_i.getID(), h_i.getStatus(), velx, vely, h_i.getRadius()))

	def viewInteractingPairs(self):
		print("")
		print("----------------------interacting pairs------------------------")
		print("  index       id   status     A_id   status     B_id   status")
		print("---------------------------------------------------------------")
		for i in range(self.__lenInteractingPairs):
			ip_i = self.__interactingPairs[i]
			A_i = ip_i.getHoleA()
			B_i = ip_i.getHoleB()
			print("%7d  %7d  %7d  %7d  %7d  %7d  %7d" % (i, ip_i.getID(), ip_i.getStatus(), A_i.getID(), A_i.getStatus(), B_i.getID(), B_i.getStatus()))


	def makeRenderWaterCircle(self):
		oX, oY = self.__pivotX, self.__pivotX
		R = self.__sheetBreakupLength

		renderNozzleX, renderNozzleY = self.sim2renderCS(oX, oY)
		renderSheetRadius = self.sim2renderNorm(R)
		renderWaterCircle = gfx.Circle(gfx.Point(renderNozzleX, renderNozzleY), renderSheetRadius)
		renderWaterCircle.setFill(self.__renderColourWater)

		return renderWaterCircle

	def makeRenderSectorMask(self):
		oX, oY = self.__pivotX, self.__pivotX
		R = self.__sheetBreakupLength

		def deg2rad(angle): return math.pi / 180 * angle

		theta = deg2rad(self.__nozzle['sprayAngle'])
		
		p1X, p1Y = -R*math.sin(theta/2) + oX, R*math.cos(theta/2) + oY
		p2X, p2Y = -R + oX, p1Y
		p3X, p3Y = p2X, -R + oY
		p4X, p4Y = R + oX, p3Y
		p5X, p5Y = p4X, p1Y
		p6X, p6Y = R*math.sin(theta/2) + oX, p5Y

		renderOX, renderOY 	 = self.sim2renderCS(oX, oY)
		renderP1X, renderP1Y = self.sim2renderCS(p1X, p1Y)
		renderP2X, renderP2Y = self.sim2renderCS(p2X, p2Y)
		renderP3X, renderP3Y = self.sim2renderCS(p3X, p3Y)
		renderP4X, renderP4Y = self.sim2renderCS(p4X, p4Y)
		renderP5X, renderP5Y = self.sim2renderCS(p5X, p5Y)
		renderP6X, renderP6Y = self.sim2renderCS(p6X, p6Y)

		p0 = gfx.Point(renderOX, renderOY)
		p1 = gfx.Point(renderP1X, renderP1Y)
		p2 = gfx.Point(renderP2X, renderP2Y)
		p3 = gfx.Point(renderP3X, renderP3Y)
		p4 = gfx.Point(renderP4X, renderP4Y)
		p5 = gfx.Point(renderP5X, renderP5Y)
		p6 = gfx.Point(renderP6X, renderP6Y)

		renderSectorMask = gfx.Polygon(p0, p1, p2, p3, p4, p5, p6)
		renderSectorMask.setFill(self.__renderColourHole)

		return renderSectorMask

	def renderDrawSheet(self):
		if self.__renderYes == 0:
			print('render not initialised')
			return 0

		self.__renderWaterCircle.draw(self.__renderCanvas)
		self.__renderSectorMask.draw(self.__renderCanvas)

		return 1

	def renderDrawAll(self):
		if self.__renderYes == 0:
			print('render not initialised')
			return 0

		if self.__timestep - 1 == self.__renderFrameRefreshMul*self.__renderFrameRefreshRate:
			
			self.renderClearAll()
			
			for holeIndex in range(self.__lenHoles):
				if self.__holes[holeIndex].getStatus() == 1:
					holeUID = self.__holes[holeIndex].getID()
					xi, yi = self.__holes[holeIndex].getPosXY()
					xi, yi = self.sim2renderCS(xi, yi)
					radiusi = self.__holes[holeIndex].getRadius()
					radiusi = self.sim2renderNorm(radiusi)
					shapelistIndex = self.__renderLenShapelist
					self.__renderShapelist.append(gfx.Circle(gfx.Point(xi, yi), radiusi))
					self.__renderLenShapelist += 1
					self.__renderShapelist[shapelistIndex].setFill(self.__renderColourHole)
					self.__renderDictHoles[holeUID] = shapelistIndex
					self.__renderShapelist[shapelistIndex].draw(self.__renderCanvas)

			for interactingPairIndex in range(self.__lenInteractingPairs):
				if self.__interactingPairs[interactingPairIndex].getStatus() == 1:
					interactingPairUID = self.__interactingPairs[interactingPairIndex].getID()
					x1, y1, x2, y2 = self.__interactingPairs[interactingPairIndex].computeLigamentXYXY()
					x1, y1 = self.sim2renderCS(x1, y1)
					x2, y2 = self.sim2renderCS(x2, y2)
					shapelistIndex = self.__renderLenShapelist
					self.__renderShapelist.append(gfx.Line(gfx.Point(x1, y1), gfx.Point(x2, y2)))
					self.__renderLenShapelist += 1
					self.__renderShapelist[shapelistIndex].setOutline(self.__renderColourWater)
					self.__renderShapelist[shapelistIndex].setWidth(self.__renderLigamentWidth)
					self.__renderDictInteractingPairs[interactingPairUID] = shapelistIndex
					self.__renderShapelist[shapelistIndex].draw(self.__renderCanvas)

			self.__renderFrameRefreshMul += 1
			return 1			

	def renderClearAll(self):
		if self.__renderYes == 0:
			print('render not initialised')
			return 0

		for i in range(self.__renderLenShapelist):
			self.__renderShapelist[i].undraw()

		self.__renderDictHoles.clear()
		self.__renderDictInteractingPairs.clear()
		self.__renderShapelist.clear()
		self.__renderLenShapelist = 0

	def renderStop(self):
		self.__renderCanvas.close()
		self.renderClearAll()
		self.__renderYes = 0
		self.__renderFrameRefreshMul = 0

	def reset(self):
		if self.__renderYes == 1:
			self.renderStop()

		self.__holes.clear()
		self.__dictHoles.clear()
		self.__lenHoles = 0
		self.__cumCountHoles = 0
		self.__interactingPairs.clear()
		self.__dictInteractingPairs.clear()
		self.__lenInteractingPairs = 0
		self.__cumCountInteractingPairs = 0

		if self.__isCumulative == 0:
			self.__dropDiaCount.clear()
			self.__dropDiaDict.clear()
			self.__lenDropDiaCount = 0
			self.__dropType0Count = 0
		
		self.__timestep = 0
		self.__time = 0

	def getInteractingPairs(self): return self.__interactingPairs
	def getHoles(self): return self.__holes
