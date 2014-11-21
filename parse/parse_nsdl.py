#!/opt/local/bin/python2.7

import os
import xml.parsers.expat
import MySQLdb

pid = ""
xmldata = ""
tag = ""
xmldata_all = {}
inHead = False
inMeta = False
inRelation = False
inCollection = False

target_fields = ["dc:title", "dc:description", "dc:subject", "dc:identifier", "title", "description", "text", "subject"]
avoid_fields = ["dc:format"]

field_types = {}
field_types["dc:title"] = "title"
field_types["dc:description"] = "description"
field_types["dc:subject"] = "subject"
field_types["dc:identifier"] = "url"
field_types["title"] = "title"
field_types["description"] = "description"
field_types["text"] = "description"
field_types["subject"] = "subject"

temp_data = []

con = MySQLdb.connect('127.0.0.1', 'root', '', 'did')
cur = con.cursor()
cur.execute("delete from digging_master where libid = 'nsdl'")

pid_count = 0

# 3 handler functions
def start_element(name, attrs):

	global xmldata, pid, temp_data, inHead, inMeta, inRelation, inCollection
	
	if name == "head":
		inHead = True
		
	if name == "metadata":
		inMeta = True
		
	if name == "relations":
		inRelation = True
		
	if name == "collectionMetadata":
		inCollection = True

	xmldata = ""	
		
def end_element(name):
	global xmldata, pid, temp_data, inHead, inMeta, inRelation, inCollection
	global pid_count
	
	if name in avoid_fields:
		return
		
	if inHead and not inCollection and name == "id":# and not inRelation:
		pid = xmldata
		pid_count += 1

	if name in target_fields and inMeta and not inCollection:
		temp_data.append(name + "\t" + xmldata)
	else:
		if inMeta and xmldata.strip() != "":
			if name[:3] == "dc:" or name[:4] == "dct:":
				temp_data.append(name + "\t" + xmldata)
		
	if name == "head":
		inHead = False
		
	if name == "metadata":
		inMeta = False
		
	if name == "collectionMetadata":
		inCollection = False
		
	if name == "relations":
		inRelation = False
		
	if name == "metadata" and not inCollection:
		# print "***: " + pid

		for fld in temp_data:
			fname, fvalue = fld.split("\t", 1)
			
			fvalue = fvalue.encode("ascii", "replace")
			fvalue = MySQLdb.escape_string(fvalue)
			
			if field_types.has_key(fname):
				ftype = field_types[fname]
			else:
				ftype = ""
				
			q = "insert into digging_master values ('nsdl', '%s', '%s', '%s', '%s', '')" % (pid, fname, ftype, fvalue)
			cur.execute(q)
			cur.execute("commit")

		temp_data = []
		
			
def char_data(data):
	global xmldata
	xmldata += data

def parse(path):
	
	global pid_count
	
	p = xml.parsers.expat.ParserCreate()

	p.StartElementHandler = start_element
	p.EndElementHandler = end_element
	p.CharacterDataHandler = char_data
		
	f = open(path)
	doc = f.read()
	f.close()
	
	p.Parse(doc)
	
	print pid_count
	
##########################################################################

rootdir = "/Users/codex/data/nsdl/"

counter = 0
for root, dirs, files in os.walk(rootdir):
	if files == []:
		continue
	
	for fn in files:
		
		# if fn != "nsdl-118101-118200.xml":
		if fn[:5] != "nsdl-":
			continue

		path = "%s/%s" % (root, fn)
		print path
		parse(path)
		counter += 1
	#	if counter == 1:
	#		break
