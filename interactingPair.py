from hole import hole
import math

class interactingPair:
	def __init__(self, holeA, holeB, timestep, uid = -1):
		self.__A = holeA
		self.__A.setIsInteracting1()
		self.__B = holeB
		self.__B.setIsInteracting1()
		self.__id = uid
		self.__birthtime = timestep
		self.__status = 1 # is the ligament in the interacting pair still intact ?

	def getID(self): 					return self.__id
	def changeID(self, uid): 			self.__id = uid
	def getBirthtime(self): 			return self.__birthtime
	def setStatus(self, status): 		self.__status = status
	def getStatus(self): 				return self.__status
	def getHoleA(self): 				return self.__A
	def getHoleB(self): 				return self.__B
	def getHoleAStatus(self): 			return self.__A.getStatus()
	def getHoleBStatus(self):			return self.__B.getStatus()
	def setHoleAStatus(self, status): 	self.__A.setStatus(status)
	def setHoleBStatus(self, status):	self.__B.setStatus(status)

	def setPairStatus(self, status):
		self.__A.setStatus(status)
		self.__B.setStatus(status)

	def setPairIsInteracting0(self):
		self.__A.setIsInteracting0()
		self.__B.setIsInteracting0()

	def computeLigamentXYXY(self):
		xA, yA 	= self.__A.getPosXY()
		rA 		= self.__A.getRadius()
		xB, yB 	= self.__B.getPosXY()
		rB 		= self.__B.getRadius()

		D2 		= (xA - xB)*(xA - xB) + (yA - yB)*(yA - yB)
		D 		= math.sqrt(D2)

		pB 		= (-rA*rA + rB*rB + D2)/(2.0*D)
		pA 		= D - pB

		h 		= math.sqrt(rA*rA - pA*pA)

		theta 	= math.atan2(yB-yA, xB-xA)

		xl1 	= xA + pA*math.cos(theta) - h*math.sin(theta)
		yl1 	= yA + pA*math.sin(theta) + h*math.cos(theta)
		xl2 	= xA + pA*math.cos(theta) + h*math.sin(theta)
		yl2 	= yA + pA*math.sin(theta) - h*math.cos(theta)

		return xl1, yl1, xl2, yl2

	def computePairDistance(self):
		xA, yA = self.__A.getPosXY()
		xB, yB = self.__B.getPosXY()

		return math.sqrt((xA-xB)*(xA-xB) + (yA-yB)*(yA-yB))

	def computeDistanceRadiusRatio(self):
		d = self.computePairDistance()
		rA = self.__A.getRadius()
		rB = self.__B.getRadius()

		return d / (rA + rB)

	def computeLigamentLength(self):
		xl1, yl1,xl2, yl2 = self.computeLigamentXYXY()
		return ((xl1 - xl2)*(xl1 - xl2) + (yl1 - yl2)*(yl1 - yl2))

	def computeResHole(self):
		xA, yA = self.__A.getPosXY()
		rA = self.__A.getRadius()
		xB, yB = self.__B.getPosXY()
		rB = self.__B.getRadius()


		d = math.sqrt((xA - xB)*(xA - xB) + (yA - yB)*(yA - yB))

		if rA + rB > d:  # if the holes overlap more than just a single point, then YES they are interacting, else NO
			if rA + d <= rB:  # if hole_A is completely sucked in by hole_B, then xCOM = xB, yCOM = yB, rCOM = rB
				xCOM = xB
				yCOM = yB
				rCOM = rB
				velx, vely = self.__B.getVelXY()
			
			elif rB + d <= rA: # if hole_B is completely sucked in by hole_A, then xCOM = xA, yCOM = yA, rCOM = rA
				xCOM = xA
				yCOM = yA
				rCOM = rA
				velx, vely = self.__A.getVelXY()

			else:
				D2 = (xA - xB)*(xA - xB) + (yA - yB)*(yA - yB)
				D = math.sqrt(D2)

				pB = (-rA*rA + rB*rB + D2)/(2.0*D)
				pA = D - pB

				if pA >= 0:
					areaA1 = rA*rA/2 * math.pi/2
					xmA1 = rA*rA*rA / (3*areaA1)
					areaA2 = rA*rA/2 * (math.asin(pA/rA) + 0.5*math.sin(2*math.asin(pA/rA)))
					xmA2 = rA*rA*rA/3 * (1- math.pow((1-(pA/rA)*(pA/rA)), 1.5))/areaA2

					xmA = (-xmA1*areaA1 + xmA2*areaA2)/(areaA1 + areaA2)
					areaA = 2*(areaA1 + areaA2)
				else:
					areaA1 = rA*rA/2*math.pi/2
					xmA1 = rA*rA*rA/(3*areaA1)

					## DEBUG
					try:
						asin_pA_rA = math.asin(-pA/rA)
					except:
						print('interacting_pair_uid = ', self.__id)
						print('hole A -- (x,y,r) :', (xA,yA,rA))
						print('hole B -- (x,y,r) :', (xB,yB,rB))
						print('pA = ', pA)
						print('rA = ', rA)
						print('-pA/rA = ', -pA/rA)
						asin_pA_rA = 0.5

					areaA2 = rA*rA/2*(asin_pA_rA + 0.5*math.sin(2*asin_pA_rA))

					xmA2 = rA*rA*rA/3*(1-  math.pow((1-(-pA/rA)*(-pA/rA)), 1.5))/areaA2

					xmA = -(xmA1*areaA1 - xmA2*areaA2)/(areaA1 - areaA2)
					areaA = 2*(areaA1 - areaA2)

				if pB >= 0:
					areaB1 = rB*rB/2*math.pi/2
					xmB1 = rB*rB*rB/(3*areaB1)
					areaB2 = rB*rB/2*(math.asin(pB/rB) + 0.5*math.sin(2*math.asin(pB/rB)))
					xmB2 = rB*rB*rB/3*(1-  math.pow((1-(pB/rB)*(pB/rB)), 1.5))/areaB2

					xmB = (-xmB1*areaB1 + xmB2*areaB2)/(areaB1 + areaB2)
					areaB = 2*(areaB1 + areaB2)
				else:
					areaB1 = rB*rB/2*math.pi/2
					xmB1 = rB*rB*rB/(3*areaB1)
					areaB2 = rB*rB/2*(math.asin(-pB/rB) + 0.5*math.sin(2*math.asin(-pB/rB)))
					xmB2 = rB*rB*rB/3*(1-  math.pow((1-(-pB/rB)*(-pB/rB)), 1.5))/areaB2

					xmB = -(xmB1*areaB1 - xmB2*areaB2)/(areaB1 - areaB2)
					areaB = 2*(areaB1 - areaB2)

				xm = (-xmA*areaA + (D + xmB)*areaB)/(areaA + areaB)
				theta = math.atan2(yB-yA, xB-xA)

				xCOM = xm*math.cos(theta) + xA
				yCOM = xm*math.sin(theta) + yA
				rCOM = math.sqrt((areaA + areaB)/math.pi)

				Avelx, Avely = self.__A.getVelXY()
				Bvelx, Bvely = self.__B.getVelXY()

				# Conservation of momentum
				velx = (Avelx*areaA + Bvelx*areaB) / (areaA + areaB)
				vely = (Avely*areaA + Bvely*areaB) / (areaA + areaB)
		else:
			print("error: holes not interacting")
			return -1, -1, -1, -1, -1				

		return xCOM, yCOM, rCOM, velx, vely

	def computeDropDiaAndCount(self, liqSheetThickness = 1):
		xA, yA 		= self.__A.getPosXY()
		rA 			= self.__A.getRadius()
		rimRadA 	= self.__A.computeRimRad(liqSheetThickness)
		
		xB, yB 		= self.__B.getPosXY()
		rB 			= self.__B.getRadius()
		rimRadB 	= self.__B.computeRimRad(liqSheetThickness)

		d = math.sqrt((xA - xB)*(xA - xB) + (yA - yB)*(yA - yB))

		if rA + rB > d:  # if the holes overlap more than just a single point, then YES they are interacting, else NO
			if rA + d <= rB:  # if hole_A is completely sucked in by hole_B, then 0 holes are formed of 0 diameter
				return 0, 0
			
			elif rB + d <= rA: # if hole_B is completely sucked in by hole_A, 0 holes are formed of 0 diameter
				return 0, 0

			else:
				ligament_rad 	= math.sqrt(rimRadA*rimRadA + rimRadB*rimRadB)
				dropDia 	 	= 3.78 * ligament_rad # Plateau-Rayleigh Instability
				ligament_vol 	= self.computeLigamentLength() * math.pi * ligament_rad*ligament_rad
				dropVol 		= 4 / 3 * math.pi * dropDia/2 *dropDia/2 * dropDia /2
				dropCount 		= round(ligament_vol / dropVol)
				dropType		= 1

				if dropCount == 0:
					# print('\npredicted drop vol > ligament vol\n')
					dropDia = 2*math.pow(3/4 * ligament_vol / math.pi, 1/3)
					dropCount = 1
					dropType = 0

				## DEBUG
				# print('ip_id = ', self.__id, ', dropDia = ', dropDia, ', dropCount = ', dropCount)


				if dropDia > 1 :
					print('\ndropDia, dropCount, dropType = %2.5f, %6d, %1d' % (dropDia, dropCount, dropType))

					xA, yA = self.__A.getPosXY()
					rA = self.__A.getRadius()
					print('A : (x %2.5f, y %2.5f, rh %2.5f, rt %2.5f)' % (xA, yA, rA, rimRadA))

					xB, yB = self.__B.getPosXY()
					rB = self.__B.getRadius()
					print('B : (x %2.5f, y %2.5f, rh %2.5f, rt %2.5f)\n' % (xB, yB, rB, rimRadB))



				return dropDia, dropCount, dropType

		else:
			print("error: holes not interacting")
			return -1, -1


