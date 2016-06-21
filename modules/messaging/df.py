# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-
import re, os, ConfigParser

class df():
	def __init__(self, confFolder):
		# Dwarf proffesions.
		confFile=os.path.join(confFolder, "df.cfg")
		grepTag='grep'
		profTag='prof'
		config = ConfigParser.RawConfigParser(allow_no_value=True)
		config.read(confFile)
		
		for grep in config.items(grepTag):
			if grep[0] == 'symbol':
				self.symbol = grep[1]
			elif grep[0] == 'file':
				self.file = grep[1]
				if not os.path.isfile(grep[1]):
					with open(grep[1], 'w') as f:
						pass
				
		self.prof=[]
		for prof in config.items(profTag):
			comp = [prof[0].capitalize(), self.symbol + prof[1].decode('utf-8')]
			self.prof.append(comp)
			
	def writeToFile(self, message):
		with open(self.file, 'r') as f:
			for line in f.readlines():
				if message['user'] == line.split(',')[0]:
					return 
			text = "%s,%s\n" %(message['user'], message['text'])
		with open(self.file, 'a') as f:
			f.write(text)
	
	def getMessage(self, message):
		for regexp in self.prof:
			if re.search(regexp[1], message['text']):
				# print "Got Hit %s" % regexp[0]
				comp = {'user': message['user'], 'text': regexp[0]}
				self.writeToFile(comp)
				break
				
		return message