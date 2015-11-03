#!/bin/bash
 
MYSQL=`which mysql`

make_db="CREATE DATABASE IF NOT EXISTS homeless_net;"
use_db="use homeless_net;"
make_table="CREATE TABLE IF NOT EXISTS users (
	id int(10) NOT NULL AUTO_INCREMENT,
	username varchar(100) DEFAULT NULL,
	password varchar(100) DEFAULT NULL,
	PRIMARY KEY (id)
);"
create_user="INSERT INTO users VALUES(null,'holmes@stbart.com','7f7d47f1ff6bf26a221b21ae3bde1074');"

SQL="${make_db}${use_db}${make_table}${create_user}"

$MYSQL -uroot -p -e "$SQL"