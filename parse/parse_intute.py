#!/opt/local/bin/python2.7

import MySQLdb
import re

con = MySQLdb.connect('127.0.0.1', 'root', '', 'intute')
cur = con.cursor()

coni = MySQLdb.connect('127.0.0.1', 'root', '', 'did')
curi = coni.cursor()

curi.execute("delete from digging_master where libid = 'intute'")
curi.execute("commit")

curc = con.cursor()

cur.execute("select handle, title, alternative_title1, alternative_title2, description, keywords_uncontrolled, keywords_controlled, classification, url1, url2, url3 from record4")

def insert_row(handle, field, ftype, value, cursor, check_empty=False):
	
	if check_empty and (value is None or value.strip() == ""):
		return
	
	if value is None:
		value = ""
	
	# if field == "alternative_title1" or field == "alternative_title2":
	# 	if value == 0:
	# 		value = ""
	
	try:
		value = value.decode('utf-8').encode("ascii", "replace")
	except:
		value = value

	value = MySQLdb.escape_string(value)
	
	if field == 'classification' or field == 'classification_free':
		value = value.split("/")[-1].strip()
	
	if field == "keywords_uncontrolled" or field == "keywords_controlled":
		for k in re.split("[;/]", value):
			k = k.strip()
			
			if len(k) == 0:
				continue
			
			q = "insert into digging_master values ('intute', '%s', " % handle
			q += "'%s', '%s', '%s', '')" % (field, ftype, k)

			cursor.execute(q)
			cursor.execute("commit")	
		
	
	
	else:
		q = "insert into digging_master values ('intute', '%s', " % handle
		q += "'%s', '%s', '%s', '')" % (field, ftype, value)
	
		cursor.execute(q)
		cursor.execute("commit")	


def get_classification(c):

	global not_found, total

	if c == "NULL" or c == None:
		return (0, c)

	if not re.match('[0-9 ;]', c): # cond: contains only classification codes
		return (1, c)

	codes = re.findall('([a-zA-Z0-9]+)', c)

	clstring = ""
	for code in codes:
		q = "select label from classification where id = '%s'" % code
		n = curc.execute(q)
		# total += 1
		if n > 0:
			clabel = curc.fetchone()[0]
			clstring += clabel + "\t"
		else:
			pass
			# not_found += 1

	return (2, clstring)

# not_found = 0
# total = 0


for row in cur:
	handle, title, alternative_title1, alternative_title2, description, keywords_uncontrolled, keywords_controlled, classification, url1, url2, url3 = row
	
	handle = handle.strip()
	
	insert_row(handle, 'title', 'title', title, curi)
	insert_row(handle, 'alternative_title1', 'title', alternative_title1, curi, True)
	insert_row(handle, 'alternative_title2', 'title', alternative_title2, curi, True)
	insert_row(handle, 'description', 'description', description, curi)
	
	insert_row(handle, 'keywords_controlled', 'subject', keywords_controlled, curi, True)
	insert_row(handle, 'keywords_uncontrolled', 'subject', keywords_uncontrolled, curi, True)

	#TODO: keywords_uncontrolled, keywords_controlled, classification

	insert_row(handle, 'url1', 'url', url1, curi, True)
	insert_row(handle, 'url2', 'url', url2, curi, True)
	insert_row(handle, 'url3', 'url', url3, curi, True)

	ctype, clstr_list = get_classification(classification)

	if ctype != 0:
		if ctype == 1:
			insert_row(handle, 'classification_free', 'subject', clstr_list, curi, True)
		else:
			for clstr in clstr_list.split("\t"):
				insert_row(handle, 'classification', 'subject', clstr, curi, True)




# print not_found, total
