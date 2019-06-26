'''
Information of different nozzles are stored in a dictionary called 'nozzle'.
An item in this dictionary is also a dictionary which stores the information
of a particular nozzle.

The template of a dictionary of a particular nozzle is as follows:
	- name (string)
	- orificeWidth (unit: mm)
	- orificeHeight (unit: mm)
	- sprayAngle (unit: degrees)
	- flowRate (unit: 0.2 gpm)
	- sprayPressure (unit: psig)
	- sprayParameter (unit: m sq)

'''
nozzle = {
	'Teejet8002' : { 
		'name' : 'Teejet8002',
		'orificeWidth' : 0.6, 
		'orificeHeight' : 1.3, 
		'sprayAngle' : 95, 
		'flowrate' : 0.2, 
		'sprayParameter' : 1e-7
	}
}


'''
Information of different fluids are stored in a dictionary called 'fluid'.
An item in this dictionary is also a dictionary which stores the information
of a particular fluid.

The template of a dictionary of a particular fluid is as follows:
	- name (string)
	- density (unit: kg per m cb)
	- viscosity (unit: cp)
	- surfaceTension (unit: mN per m)

'''
fluid = {
	'water' : {
		'name' : 'water',
		'density' : 1000,
		'viscosity' : 1,
		'surfaceTension' : 72
	},

	'emulsion' : {
		'name' : 'emulsion',
		'density' : 1000,
		'viscosity' : 1,
		'surfaceTension' : 70
	}
}

'''
Different sheet settings are stored in a dictionary called 'sheetSettings'.
An item in this dictionary is also a dictionary which stores the information
of a sheet setting.

The template of a dictionary of a particular sheet setting is as follows:
	- name (string)
	- section1 (unit: mm)
	- section2 (unit: mm)
	- section3 (unit: mm)

'''
sheetSettings = {
	'default' : {
		'name' : 'default',
		'section1' : 5,
		'section2' : 10,
		'section3' : 15
	}
}