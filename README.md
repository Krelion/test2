# Initial test
===========

- Host machine for VirtualBox based on Ubuntu 16.10 with SSD storage.
- Virtual machines called node1 and node2 based on Debian Jessie.

### VirtualBox installation on Ubuntu 16.10

Open a terminal and execute:

    $ sudo apt update
    $ sudo apt install virtualbox -y

### Configure virtual machine "node1"

This command creates a new XML virtual machine definition file.

$ VBoxManage createvm --name "node1" --register

This command changes the properties of a registered virtual machine which is not running.

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

