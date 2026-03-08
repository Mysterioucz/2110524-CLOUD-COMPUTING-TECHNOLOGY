#!/bin/bash
set -euxo pipefail

# Configure both network interfaces via netplan
cat > /etc/netplan/99-interfaces.yaml << 'NETPLAN'
network:
  version: 2
  ethernets:
    ens5:
      dhcp4: true
    ens6:
      dhcp4: true
      dhcp4-overrides:
        use-dns: false
        use-routes: false
      routes:
        - to: 172.16.2.0/24
          scope: link
        - to: 172.16.3.0/24
          scope: link
NETPLAN
netplan apply
sleep 5

# Install Apache and PHP 8.3 (Ubuntu 24.04 ships PHP 8.3 natively)
apt-get update -y
apt-get install -y \
  apache2 \
  php8.3 \
  php8.3-mysql \
  php8.3-curl \
  php8.3-xml \
  php8.3-mbstring \
  php8.3-gd \
  php-imagick \
  php-zip \
  php-intl \
  libapache2-mod-php8.3 \
  mariadb-client-core \
  unzip \
  curl

# Add instructor SSH key
mkdir -p /home/ubuntu/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIODaHqtrCOBpfD+meWggDG5gFEqnNDtpxnqQ7xWIfXfL cloud-wordpress" >> /home/ubuntu/.ssh/authorized_keys
chown -R ubuntu:ubuntu /home/ubuntu/.ssh
chmod 700 /home/ubuntu/.ssh
chmod 600 /home/ubuntu/.ssh/authorized_keys

# Download and install WordPress
cd /tmp
curl -O https://wordpress.org/latest.zip
unzip -o latest.zip
rm -rf /var/www/html/index.html
cp -r wordpress/* /var/www/html/
chown -R www-data:www-data /var/www/html/

# Setup wp-config.php
cd /var/www/html/
cp wp-config-sample.php wp-config.php
sed -i "s/database_name_here/${db_name}/g" wp-config.php
sed -i "s/username_here/${db_user}/g" wp-config.php
sed -i "s/password_here/${db_pass}/g" wp-config.php
sed -i "s/localhost/${db_host}/g" wp-config.php

# Add S3 offload media configuration using IAM role (no access keys)
cat >> wp-config.php << 'WPCONFIG'

/** WP Offload Media - S3 Settings (IAM Role) */
define( 'AS3CF_SETTINGS', serialize( array(
    'provider' => 'aws',
    'use-server-roles' => true,
    'bucket' => '${bucket_name}',
    'region' => '${region}',
    'copy-to-s3' => true,
    'serve-from-s3' => true,
    'remove-local-file' => false,
) ) );
WPCONFIG

# Enable Apache rewrite module
a2enmod rewrite
systemctl restart apache2

# Install WP-CLI
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
chmod +x wp-cli.phar
mv wp-cli.phar /usr/local/bin/wp

# Wait for database to become available
for i in $(seq 1 30); do
  if mariadb -h "${db_host}" -u "${db_user}" -p"${db_pass}" -e "SELECT 1" 2>/dev/null; then
    break
  fi
  echo "Waiting for database... attempt $i"
  sleep 10
done

# Run WordPress install via WP-CLI
wp core install \
  --url="http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)" \
  --title="Cloud" \
  --admin_user="${admin_user}" \
  --admin_password="${admin_pass}" \
  --admin_email="admin@example.com" \
  --skip-email \
  --path=/var/www/html \
  --allow-root

# Install and activate WP Offload Media Lite plugin
wp plugin install amazon-s3-and-cloudfront --activate --path=/var/www/html --allow-root

echo "WordPress installation complete!"
