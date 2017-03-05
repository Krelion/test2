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

    $sudo nano /etc/network/interfaces

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

