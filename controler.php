<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr" lang="fr">
<head>
	<title>Le redoutable questionnaire</title>
	<meta charset="utf-8" />
	<link href="style.css" rel="stylesheet" type="text/css"/>
</head>
<body>
	<div id="haut">
		<h1>Le questionnaire sur les technos Web</h1>
	</div>
	<?php
		$lesR�ponses[0]=$_GET["rep1"];
		$lesR�ponses[1]=$_GET["rep2"];
		$lesR�ponses[2]=$_GET["rep3"];
		$lesR�ponses[3]=$_GET["rep4"];
		$lesR�ponses[4]=$_GET["rep5"];
		$lesR�ponses[5]=$_GET["rep6"];
		$leFichier=fopen("./reponses.txt","r");
		$trouve=false;
		for ($i=0;$i<6;$i++)
		{	$ligne=fgets($leFichier,250);
			$tableau = explode (";",$ligne);
			$lesBonnesR�ponses[$i]=$tableau[0];
		}
		fclose ($leFichier);
		$tot=0;
		for ($i=0;$i<6;$i++)
		{	if (strToUpper($lesR�ponses[$i])==strToUpper($lesBonnesR�ponses[$i]))
				$tot=$tot + 1;
		}
		if (isset($_GET["ssfaute"]))
			if($tot != 6)
				echo '<h3 class="�chec">Vous avez perdu votre pari ; votre score est de ' . $tot . ' /6 </h3>';
			else
				echo '<h3 class="r�ussite">Vous avez gagn� votre pari ; c\'est un tr�s beau sans faute</h3>';
		else
			if($tot != 6)
				echo '<h3 class="�chec">Vous avez bien fait de ne pas parier; votre score est de ' . $tot . ' /6 </h3>';
			else
				echo '<h3>Vous auriez du parier ; c\'est un tr�s beau sans faute</h3>';
		
?>
</html>