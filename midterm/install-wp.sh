#!/bin/bash
# Basic setup script for WordPress
apt-get update -y
apt-get install -y apache2 php php-mysql mysql-client libapache2-mod-php unzip

# Get WordPress
cd /tmp
wget https://wordpress.org/latest.zip
unzip latest.zip
mv wordpress/* /var/www/html/
chown -R www-data:www-data /var/www/html/
rm -rf /var/www/html/index.html

# Setup wp-config.php
cd /var/www/html/
cp wp-config-sample.php wp-config.php
sed -i "s/database_name_here/${db_name}/g" wp-config.php
sed -i "s/username_here/${db_user}/g" wp-config.php
sed -i "s/password_here/${db_pass}/g" wp-config.php
sed -i "s/localhost/${db_host}/g" wp-config.php

systemctl restart apache2
