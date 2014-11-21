"""
A sample Python code for the Termine Web Service.
This code requires Python 2.2 or later and ZSI 2.0.

Before running this code, run the following command to generate wrapper
classes for the service:
$ wsdl2py -u http://www.nactem.ac.uk/software/termine/webservice_key/termine.wsdl
"""

from termine_server import *

port = termineLocator().gettermine_porttype()
req = analyze_request()

# Call the service with default options.
print "--- Default ---"
req._src = 'Technical terms are important for knowledge mining, especially in the bio-medical area where vast amount of documents are available.'
req._key = "Your key here"
res = port.analyze(req)
print res._result
print

# Analyze the same text and obtain the result in XML.
print "--- XML output ---"
req._output_format = 'xml'
res = port.analyze(req)
print res._result
print
req._output_format = None

# Register words 'area' and 'amount' to the stoplist.
print "--- Apply stoplist, ['area', 'amount'] ---"
req._stoplist = 'area amount'
res = port.analyze(req)
print res._result
print
req._stoplist = None

# Modify the linguistic filter to extract prepositional phrases.
print "--- Modify the linguistic filter to '{IN}{DT}*{JJ}*{NN}+' ---"
req._filter = '{IN}{DT}*{JJ}*{NN}+'
res = port.analyze(req)
print res._result
print
req._filter = None

# Analyze the sentence with part-of-speech annotation.
print "--- Analyze a part-of-speech tagged (POST) sentence ---"
req._input_format = 'post.genia'
req._src="""
Technical	Technical	JJ
terms	term	NNS
are	be	VBP
important	important	JJ
for	for	IN
knowledge	knowledge	NN
mining	mining	NN
,	,	,
especially	especially	RB
in	in	IN
the	the	DT
bio-medical	bio-medical	JJ
area	area	NN
where	where	WRB
vast	vast	JJ
amount	amount	NN
of	of	IN
documents	document	NNS
are	be	VBP
available	available	JJ
.	.	.
EOS
"""
res = port.analyze(req)
print res._result
print
