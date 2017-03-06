# Initial test

- Host machine for VirtualBox based on Ubuntu 16.10 with SSD storage.
- Virtual machines called node1 and node2 based on Debian Jessie.

### VirtualBox installation on Ubuntu 16.10

Open a terminal and execute:

    $ sudo apt update
    $ sudo apt install virtualbox -y

## node1

### Configure virtual machine "node1"

This command creates a new XML virtual machine definition file.

$ VBoxManage createvm --name "node1" --register

This command changes the properties of a registered virtual machine which is not running. Creates two nic interface - bridged and internal.

    $ VBoxManage modifyvm "node1" \
    --ostype Debian_64 \
    --memory 4096 \
    --nic1 bridged \
    --bridgeadapter1 enp6s0 \
    --cableconnected1 on \
    --nic2 intnet \
    --intnet2 localnet \
    --cableconnected2 on \
    --acpi on \
    --ioapic on \
    --boot1 dvd

Create a 16GB “dynamic” disk.
 
    $ VBoxManage createhd --filename /home/$USER/VirtualBox\ VMs/node1/node1.vdi --size 16000

Add a SATA controller with the dynamic disk attached and mark it as SSD.

    $ VBoxManage storageattach node1 \
    --storagectl SATA \
    --port 0 \
    --type hdd \
    --nonrotational on \
    --medium /home/$USER/VirtualBox\ VMs/node1/node1.vdi

Download minimal Debian Jessy ISO image.

    $ wget http://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-8.7.1-amd64-netinst.iso

Add an IDE controller with a DVD drive attached, and the install ISO inserted into the drive:

    $ VBoxManage storagectl node1 --name IDE --add ide
    $ VBoxManage storageattach node1 \
    --storagectl IDE \
    --port 1 \
    --device 0 \
    --type dvddrive \
    --medium /home/$USER/debian-8.7.1-amd64-netinst.iso

Configuration is all done and we can start node1.

    $ VBoxManage startvm node1

Once you have configured the operating system, you can connect from host machine terminal to a server by using SSH.

    $ ssh krelion@192.168.99.219

Configure network interfaces

    $ sudo nano /etc/network/interfaces

    ...
    auto eth0
    ...
    
    # The secondary network interface for internal network
    auto eth1
    iface eth1 inet static
            address 192.168.55.1
            netmask 255.255.255.0

Restart network service
    
    service networking restart
    

### Install Oracle JRE 8 on Debian Linux

To install Oracle’s Java Runtime with apt, we first need to entend the list of apt-get’s sources. Once that is done, an java-installer will actually install the Java SE Runtime Environment. Here are the steps to follow:

    $ sudo su
    # echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" > /etc/apt/sources.list.d/webupd8team-java.list
    # echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >> /etc/apt/sources.list.d/webupd8team-java.list
    # apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EEA14886
    # apt update
    # apt install oracle-java8-installer -y
    # java -version
    # exit

With Java now installed we move on, installing Tomcat. However, it may be beneficial to have an dedicated user for Tomcat.
BTW, Java got installed into this location: /usr/lib/jvm/java-8-oracle

    $ sudo adduser \
    --system \
    --shell /bin/bash \
    --gecos 'Tomcat Java Servlet and JSP engine' \
    --group \
    --disabled-password \
    --home /home/tomcat \
    tomcat

### Installing Tomcat 8.5.11

    $ mkdir -p ~/tmp
    $ cd ~/tmp
    $ wget http://apache-mirror.rbc.ru/pub/apache/tomcat/tomcat-8/v8.5.11/bin/apache-tomcat-8.5.11.tar.gz
    $ tar xvzf ./apache-tomcat-8.5.11.tar.gz
    $ rm ./apache-tomcat-8.5.11.tar.gz
    $ sudo mv ./apache-tomcat-8.5.11 /usr/share

To make it easy to replace this release with future releases, we are going to create a symbolic link that we are going to use when referring to Tomcat (after removing the old link, you might have from installing a previous version):

    $ sudo rm -f /usr/share/tomcat
    $ sudo ln -s /usr/share/apache-tomcat-8.5.11 /usr/share/tomcat

Since we created a tomcat user, he should also own all these files in

    $ sudo chown -R tomcat:tomcat /usr/share/tomcat/*
    $ sudo chmod +x /usr/share/tomcat/bin/*.sh

Edit tomcat/conf/server.xml

    $ sudo nano /usr/share/tomcat/conf/server.xml

Specify a bind address and port for that connector:

    port="9999"
    protocol="HTTP/1.1"
    address="127.0.0.1"

To start Tomcat automatically, every time the server re-boots, save this script in /etc/init.d/tomcat

    $ nano /etc/init.d/tomcat
    
    #!/bin/bash
    
    ### BEGIN INIT INFO
    # Provides:        tomcat
    # Required-Start:  $network
    # Required-Stop:   $network
    # Default-Start:   2 3 4 5
    # Default-Stop:    0 1 6
    # Short-Description: Start/Stop Tomcat server
    ### END INIT INFO
    
    PATH=/sbin:/bin:/usr/sbin:/usr/bin

    start() {
     /bin/su - tomcat -c /usr/share/tomcat/bin/startup.sh
    }
    
    stop() {
     /bin/su - tomcat -c /usr/share/tomcat/bin/shutdown.sh
    }

    case $1 in
      start|stop) $1;;
      restart) stop; start;;
      *) echo "Run as $0 <start|stop|restart>"; exit 1;;
    esac

Now change the permissions of the newly created file and add the correct symlinks automatically:

    $ sudo chmod 755 /etc/init.d/tomcat
    $ sudo update-rc.d tomcat defaults

### Installing Nginx

    $sudo apt install nginx

### Install Certbot, the Let's Encrypt Client

    $ sudo su
    # echo 'deb http://ftp.debian.org/debian jessie-backports main' | sudo tee /etc/apt/sources.list.d/backports.list
    # exit
    $ sudo apt update
    $ sudo apt install certbot -t jessie-backports

### Configure Nginx

sudo nano /etc/nginx/sites-available/default

Inside the server block, add this location block:

        location ~ /.well-known {
                allow all;
        }
        
        
Check your configuration for syntax errors:

    $ sudo nginx -t


If no errors are found, restart Nginx with this command:

    $ sudo systemctl restart nginx

### Obtain an SSL Certificate for domain test.devops.su

We can use the Webroot plugin to request an SSL certificate with these commands.

    $ sudo certbot certonly -a webroot --webroot-path=/var/www/html -d test.devops.su -d www.test.devops.su

After certbot initializes, you will be prompted for some information. The exact prompts may vary depending on if you've used Let's Encrypt before.

### Generate Strong Diffie-Hellman Group

To further increase security, you should also generate a strong Diffie-Hellman group. To generate a 2048-bit group, use this command:

    $ sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

### Create a Configuration Snippet Pointing to the SSL Key and Certificate

    $ sudo nano /etc/nginx/snippets/ssl-test.devops.su.conf

    ssl_certificate /etc/letsencrypt/live/test.devops.su/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/test.devops.su/privkey.pem;

### Create a Configuration Snippet with Strong Encryption Settings

    $ sudo nano /etc/nginx/snippets/ssl-params.conf

    ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers on;
    ssl_ciphers "EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH";
    ssl_ecdh_curve secp384r1;
    ssl_session_cache shared:SSL:10m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    add_header Strict-Transport-Security "max-age=63072000; includeSubdomains";
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    ssl_dhparam /etc/ssl/certs/dhparam.pem;

### Adjust the Nginx Configuration to Use SSL

Before we go any further, let's back up our current server block file:

    $ sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak

Now, open the server block file to make adjustments:

    $ sudo nano /etc/nginx/sites-available/default

    ...
    # Default server configuration
    #
    server {
            listen 80 default_server;
            listen [::]:80 default_server;
            server_name test.devops.su www.test.devops.su;
            return 301 https://$server_name$request_uri;
    }

    server {
            # SSL configuration
    
            listen 443 ssl default_server;
            listen [::]:443 ssl default_server;
            include snippets/ssl-test.devops.su.conf;
            include snippets/ssl-params.conf;
    
            #
            # listen 443 ssl default_server;
            # listen [::]:443 ssl default_server;
            #
            # Self signed certs generated by the ssl-cert package
            # Don't use them in a production server!
            #
            # include snippets/snakeoil.conf;

            root /var/www/html;

            # Add index.php to the list if you are using PHP
            index index.html index.htm index.nginx-debian.html;

            server_name test.devops.su www.test.devops.su;
        ...

### Configure nginx as reverse proxy

    $ sudo nano /etc/nginx/sites-available/default

    upstream tomcat {
        server 127.0.0.1:9999 fail_timeout=0;
    }

    server {
        . . .
    
        location / {
            #try_files $uri $uri/ =404;
            include proxy_params;
            proxy_pass http://tomcat/;
        }
        
        . . .
    }

Enabling the Changes in Nginx

    $ sudo nginx -t

If no errors are found, restart Nginx with this command:

    $ sudo systemctl restart nginx

### Check SSL security.

You can use the Qualys SSL Labs Report to see how your server configuration scores:

In a web browser:

https://www.ssllabs.com/ssltest/analyze.html?d=test.devops.su

This SSL setup should report an A+ rating.

### Set Up Auto Renewal SSL certs.

    $ sudo crontab -e

    30 2 * * 1 /usr/bin/certbot renew >> /var/log/le-renew.log
    35 2 * * 1 /bin/systemctl reload nginx


### iptables

Iptables provides packet filtering, network address translation (NAT) and other packet mangling.

In security reason we need to block all incoming connections to all ports, except ssh and nginx ports.

    $sudo nano /etc/iptables.test.rules

    *filter
        
    -P INPUT DROP
    -P FORWARD ACCEPT
    -P OUTPUT ACCEPT
    -A INPUT -p tcp -m tcp --dport 443 -j ACCEPT
    -A INPUT -i lo -j ACCEPT
    -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    -A INPUT -p tcp -m tcp --dport 22 -j ACCEPT
    -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT

    COMMIT

Activate these new rules:

    $ sudo iptables-restore < /etc/iptables.test.rules

Save the new rules to the master iptables file:

    $ sudo iptables-save > /etc/iptables.up.rules

To make sure the iptables rules are started on a reboot we'll create a new file:

    $ sudo nano /etc/network/if-pre-up.d/iptables

Add these lines to it:

    #!/bin/sh
    /sbin/iptables-restore < /etc/iptables.up.rules

The file needs to be executable so change the permissions:

    $sudo chmod +x /etc/network/if-pre-up.d/iptables

### Nginx log parser

You can analyze nginx log with python script - countresponse.py

    $ sudo python countresponse.py

Output looks like this:

    200 - 126
    304 - 18
    404 - 8
    301 - 5
    400 - 4
    302 - 2
    401 - 1
    502 - 1
    500 - 1
 
### Set Up MySQL and configure Master Slave Replication

For communication between two servers, we'll use the internal network.

- 192.168.55.1 - Master Database

- 192.168.55.2 - Slave Database

Install MySQL Server and CLI

    $ sudo apt install mysql-server mysql-client

Install addition modules for python

    $ sudo apt install python-mysqldb

Create couple of databases and populate them with data using python scripts randomemailstomysql.py for "CogiaDB1" and randomemailstomysql2.py for "CogiaDB2"

    $ python randomemailstomysql.py
    $ python randomemailstomysql2.py

Open up the mysql configuration file on the master server "node1".

    $sudo nano /etc/mysql/my.cnf

    ...
    bind-address            = 192.168.55.1
    ...

    #uncomment line
    server-id               = 1

    binlog_do_db            = CogiaDB1
    binlog_do_db            = CogiaDB2

Refresh MySQL.

    $ sudo service mysql restart

Open up the MySQL shell.
    
    $ mysql -u root -p

We need to grant privileges to the slave. You can use this line to name your slave and set up their password. The command should be in this format:

    GRANT REPLICATION SLAVE ON *.* TO 'slave_user'@'%' IDENTIFIED BY 'CogiaTest33';

    FLUSH PRIVILEGES;
    
Following that, lock the database to prevent any new changes:

    USE CogiaDB1;

    FLUSH TABLES WITH READ LOCK;

    USE CogiaDB2;

    FLUSH TABLES WITH READ LOCK;

    SHOW MASTER STATUS;

You will see a table that should look something like this:

    +------------------+----------+-------------------+------------------+
    | File             | Position | Binlog_Do_DB      | Binlog_Ignore_DB |
    +------------------+----------+-------------------+------------------+
    | mysql-bin.000003 |      107 | CogiaDB1,CogiaDB2 |                  |
    +------------------+----------+-------------------+------------------+
    1 row in set (0.00 sec)

This is the position from which the slave databases will start replicating. Record these numbers, they will come in useful later.

Proceeding the with the database still locked, export your database using mysqldump in the new window 

    $ mysqldump -u root -p --opt CogiaDB1 > CogiaDB1.sql
    $ mysqldump -u root -p --opt CogiaDB2 > CogiaDB2.sql

Now, returning to your your original window, unlock the databases (making them writeable again). Finish up by exiting the shell.

    UNLOCK TABLES;
    QUIT;

Copy backups to slave server "node2"

    $ scp ./*.sql krelion@192.168.55.2:~

Now you are all done with the configuration of the the master database.

## node2

### Configure virtual machine "node2"

This command creates a new XML virtual machine definition file.

$ VBoxManage createvm --name "node2" --register

This command changes the properties of a registered virtual machine which is not running. Creates two nic interface - bridged and internal.

    $ VBoxManage modifyvm "node2" \
    --ostype Debian_64 \
    --memory 4096 \
    --nic1 bridged \
    --bridgeadapter1 enp6s0 \
    --cableconnected1 on \
    --nic2 intnet \
    --intnet2 localnet \
    --cableconnected2 on \
    --acpi on \
    --ioapic on \
    --boot1 dvd

Create a 16GB “dynamic” disk.
 
    $ VBoxManage createhd --filename /home/$USER/VirtualBox\ VMs/node2/node2.vdi --size 16000

Add a SATA controller with the dynamic disk attached and mark it as SSD.

    $ VBoxManage storageattach node2 \
    --storagectl SATA \
    --port 0 \
    --type hdd \
    --nonrotational on \
    --medium /home/$USER/VirtualBox\ VMs/node2/node2.vdi

Download minimal Debian Jessy ISO image.

    $ wget http://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-8.7.1-amd64-netinst.iso

Add an IDE controller with a DVD drive attached, and the install ISO inserted into the drive:

    $ VBoxManage storagectl node2 --name IDE --add ide
    $ VBoxManage storageattach node2 \
    --storagectl IDE \
    --port 1 \
    --device 0 \
    --type dvddrive \
    --medium /home/$USER/debian-8.7.1-amd64-netinst.iso

Configuration is all done and we can start node2.

    $ VBoxManage startvm node2

Once you have configured the operating system, you can connect from host machine terminal to a server by using SSH.

    $ ssh krelion@192.168.99.218

Configure network interfaces

    $ sudo nano /etc/network/interfaces

    ...
    auto eth0
    ...
    
    # The secondary network interface for internal network
    auto eth1
    iface eth1 inet static
            address 192.168.55.2
            netmask 255.255.255.0

Restart network service
    
    service networking restart
    
