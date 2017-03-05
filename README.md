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

Enabling the Changes in Nginx

    $ sudo nginx -t

If no errors are found, restart Nginx with this command:

    $ sudo systemctl restart nginx
