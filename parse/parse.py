#!/opt/local/bin/python2.7

import os
import xml.parsers.expat
import MySQLdb

pid = ""
xmldata = ""
tag = ""
xmldata_all = {}
inDC = False
inIPL = False

target_fields = ["dc:title", "dc:description", "dc:subject", "ipl:url"]
avoid_fields = ["ipl:record", "ipl:header", "ipl:contact", "ipl:status"]

field_types = {}
field_types["dc:title"] = "title"
field_types["dc:description"] = "description"
field_types["dc:subject"] = "subject"
field_types["ipl:url"] = "url"

temp_data = []

con = MySQLdb.connect('127.0.0.1', 'root', '', 'did')
cur = con.cursor()
cur.execute("delete from digging_master where libid = 'ipl'")

# 3 handler functions
def start_element(name, attrs):

	global xmldata, pid, temp_data, inIPL, inDC
	
	if name == "foxml:digitalObject":
		pid = attrs['PID']
		temp_data = []
		
	if name == "foxml:datastream" and attrs['ID'] == "IPL":
		inIPL = True
		
	if name == "foxml:datastream" and attrs['ID'] == "DC":
		inDC = True
		
	xmldata = ""	
	
def end_element(name):
	global xmldata, pid, temp_data, inIPL, inDC

	if name in avoid_fields:
		return

	if name in target_fields:
		temp_data.append(name + "\t" + xmldata)
	else:
		if xmldata.strip() != "":
			if inDC and name[:3] == "dc:":
				temp_data.append(name + "\t" + xmldata)

			if inIPL and name[:4] == "ipl:":
				temp_data.append(name + "\t" + xmldata)
		
	if name == "foxml:datastream" and inIPL:
		inIPL = False
		
	if name == "foxml:datastream" and inDC:
		inDC = False
		
		
	if name == "foxml:digitalObject":
		print "***: " + pid

		for fld in temp_data:
			fname, fvalue = fld.split("\t", 1)
			
			fvalue = fvalue.encode("ascii", "replace")
			fvalue = MySQLdb.escape_string(fvalue)
			
			if field_types.has_key(fname):
				ftype = field_types[fname]
			else:
				ftype = ""
				
			q = "insert into digging_master values ('ipl', '%s', '%s', '%s', '%s')" % (pid, fname, ftype, fvalue)
			cur.execute(q)
			cur.execute("commit")

		
			
def char_data(data):
	global xmldata
	xmldata += data

def parse(path):

	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data
	
	
	f = open(path)
	doc = f.read()
	f.close()
	
	p.Parse(doc)
	
##########################################################################

rootdir = "/Users/codex/data/IPL/MetaDataSamples/objects/"

for root, dirs, files in os.walk(rootdir):
	if files == []:
		continue
	
	for fn in files:
		
		if fn[0] == "." or fn[:4] != "res_":
			continue
			
		path = "%s/%s" % (root, fn)
		parse(path)