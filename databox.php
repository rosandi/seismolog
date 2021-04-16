<?php

echo "Message received\n";
$fname=$_POST["name"];
if(file_exists("data/$fname")) die ("File $fname exists");

$fl=fopen("data/$fname", "w") or die("Unable to open file!");
fwrite($fl, $_POST["json"]."\n");
fclose($fl);

echo "File saved:".$_POST["name"];

?>
