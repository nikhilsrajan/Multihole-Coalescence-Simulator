import math

class hole:
	def __init__(self, xINI, yINI, radius, timestep = 0, status = 1, uid = -1, velX = 0, velY = 0):
		self.__x = xINI
		self.__y = yINI
		self.__r = radius
		self.__birthtime = timestep
		self.__status = status  # hole is still physically present in the sheet ?
		self.__id = uid
		self.__isInteracting = 0  # is the hole part of an interacting pair ?
		self.__interactingWith = []  # list of tuples of (holeUID, interactingPairUID) "this" hole is interacting with

		self.__velX = velX  # distance moved in x per unit timestep
		self.__velY = velY  # distance moved in y per unit timestep

	def getPosXY(self): 								return self.__x, self.__y
	def getRadius(self): 								return self.__r
	def computeArea(self): 								return self.__r*self.__r*math.pi
	def getID(self): 									return self.__id
	def getStatus(self): 								return self.__status
	def getBirthtime(self): 							return self.__birthtime
	def getVelXY(self): 								return self.__velX, self.__velY
	def getIsInteracting(self): 						return self.__isInteracting
	def getInteractingWith(self): 						return self.__interactingWith
	def getLenInteractingWith(self): 					return len(self.__interactingWith)
	def placeAt(self, xNew, yNew): 						self.__y, self.__y = xNew, yNew
	def setVelXY(self, velX, velY): 					self.__velX, self.__velY = velX, velY
	def computeRimRad(self, liqSheetThickness = 1):		return math.sqrt(self.__r / 2 * liqSheetThickness / math.pi)

	def moveBy(self, dx, dy):
		self.__x += dx
		self.__y += dy

	def move(self, dt):
		self.__x += self.__velX*dt
		self.__y += self.__velY*dt

	def incrementRadiusBy(self, dr): 		self.__r += dr	
	def changeID(self, uid): 				self.__id = uid
	def setStatus(self, status): 			self.__status = status
	def setIsInteracting0(self): 			self.__isInteracting = 0
	def setIsInteracting1(self):			self.__isInteracting = 1
	
	def addInteractingWith(self, item):
		if self.getIsInteracting() == 0:
			self.setIsInteracting1()
		self.__interactingWith.append(item)
	
	def popInteractingWith(self, item): 		
		self.__interactingWith.remove(item)
		if len(self.__interactingWith) == 0:
			self.setIsInteracting0()

	def getUIDInteractingWithByIndex(self, index):	
		if index < 0 or index > len(self.__interactingWith):
			print('Index out of bound.')
			return -1
		else:
			return self.__interactingWith[index]