import sys

myFile = open("namesandnetids.csv", "r");
sys.stdout.write('{')
line = myFile.readline()
while (line != None):
	line = line[:-2]
	split = line.split(',')
	sys.stdout.write('"%s": "%s",\n' %(split[1], split[0]))
	line = myFile.readline()
	if line == None:
		break