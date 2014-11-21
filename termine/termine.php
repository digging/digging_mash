<?php
// A key is required to use this service. See: http://www.nactem.ac.uk/register_service.php
$key = "a63653030d56a1ab4a436be3fa2cb172914d60d2492250064a6a7e1";

// Create an object to access the Termine Web Service.
$client = new SoapClient("http://www.nactem.ac.uk/software/termine/webservice/termine.wsdl");

$l1 = mysql_connect('127.0.0.1', 'root', '');
$l2 = mysql_connect('127.0.0.1', 'root', '');

mysql_select_db('did', $l1);
mysql_select_db('did', $l2);

$res = mysql_query("select d.libid, d.rid, type, value from digging_master d, samples s
where d.rid = s.rid
and type in ('title', 'description')
order by libid, rid, type desc", $l1);
// and d.pid = 'humbul15954'

while($row = mysql_fetch_row($res)) {
	$libid = $row[0];
	$rid = $row[1];
	$type = $row[2];
	$txt = $row[3];

	print "* ID: ". $rid. "\n";
	print "* TYPE: ". $type. "\n";

	$sents = explode('.', $txt);
	foreach ($sents as $sent) {
		$sent = iconv('UTF-8', 'ASCII//TRANSLIT', $sent);
		$tres = $client->analyze($sent, $key);

		///
		$tres = trim($tres);
		$lines = split("\n", $tres);

		foreach($lines as $l) {
			$r = split(" ", $l, 2);

			$score = $r[0];
			$np = $r[1];
			$q = "insert into phrases values ('".$libid."', '".$rid."', '".$type."', '".$score."', '".$np."')";
			mysql_query($q, $l2);
		}

	}

}

?>
