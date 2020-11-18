# Setup POC VoIP with Debian 10, Asterisk 18

## 1. Setup Debian 10 server


### Base setup configuration
--------------- 

Connect as root
```bash
su -
```

Install sudo 
```bash
apt update
apt updgrade
apt install sudo
```

Install ssh
```bash
apt install openssh-server
```

Check IP address
```bash
ip a
```

If you need to connect with ssh (replace user by the username and ip by the ip machine)
```bash
ssh user@ip
```
> if you need to generate a new ssh key : `ssh-keygen -R ip`

Install linux-headers
```bash
apt install linux-headers-$(uname -r)
```

Install some required tools to compile from sources
```bash
apt install build-essential autoconf net-tools
```

Install some required Asterisk's packages
```bash
sudo apt install openssl libjansson-dev uuid-dev sqlite3 libsqlite3-dev libxml2-dev libxslt1-dev libncurses5-dev pkg-config unixodbc-dev libtool make libasound2-dev
```

Install python 2.7 (Debian 10 comes with python 3.X)
```bash
apt install python-pip python-dev
```

### Install Asterisk
---------------

#### From sources (best way to install it)

> Asterisk will be installed in folder `/usr/local/src`

First download the Asterisk current archive
```bash
wget https://downloads.asterisk.org/pub/telephony/asterisk/asterisk-18-current.tar.gz
```

Extract tarball and go to folder (replace .X.X by your version number)
```bash
tar -zxvf asterisk-18-current.tar.gz
cd asterisk-18.X.X
```

Install all Asterisk's prereq
```bash
./contrib/scripts/install_prereq install
```

> During installation, Asterisk will ask for your international phone extension (eg. **1** for North America, **33** for France, **34** for Spain, **44** for UK, ...)

Compile source
```bash
./configure --with-jansson-bundled --with-pjproject-bundled
make menuselect
make
make install
make config
make install-logrotate
```

Run Asterisk at startup
```bash
systemctl enable asterik
```

Start/Stop/Restart/Status Asterisk
```bash
service asterisk start|stop|restart|status
```

> If you need to get rid of radius error. There is 2 options :
> * Install free radius (create symlink if the folder isn't correct)
```bash
apt install freeradius-utils libpam-radius-auth
ln -s /etc/radcli /etc/radiusclient-ng
```
> * Unload radius modules
```bash
nano /etc/asterisk/modules.conf
```
Add the following line
```vim
noload => cdr_radius.so
```
> Restart asterisk `service asterisk restart`

To access all Asterisk's conf files
```bash
cd /etc/asterisk/
```

#### Other dependencies
> If you need to install DAHDI
```bash
apt install libusb-dev libglib2.0-dev autogen libtool shtool 
wget https://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-current.tar.gz
tar -zxvf dahdi-linux-complete-current.tar.gz
cd dahdi-linux-complete-3.1.0+3.1.0/
make 
make install
make config
```

> If you need to install libpri
```bash
wget https://downloads.asterisk.org/pub/telephony/libpri/libpri-current.tar.gz
cd libpri-1.6.0/
make
make install
```

#### Basic Asterisk configuration

```bash
cd /etc/asterisk/
```

First check your asterisk installation 
```bash
asterisk -rvvv

> show sip peers
```

If the following error appears `No such command 'sip show peers'` run the following command (it will load chan_sip module)
```bash
> module load chan_sip.so
```

Then run `netstat -anup` and check if port :5060 is present

First save original conf files
```bash
mv sip.conf sip.conf.origin
mv extensions.conf extensions.conf.origin
```

Restart Asterisk and then run again `netstat -anup`, port :5060 shouldn't be present

#### Setup basic SIP configuration

```bash
nano sip.conf
```

> Add the following configuration

```vim
[general]
language=fr
disallow=all
allow=ulaw
allow=alaw
hassip=yes
hasvoicemail=no
notifyhold=yes
callcounter=yes
context=local

[john]
type=friend
secret=test
callerid= 'John' <100>
host=dynamic

[bob]
type=friend
secret=test
callerid= 'Bob' <301>
host=dynamic

[alice]
type=friend
secret=test
callerid= 'Alice' <302>
host=dynamic
```

```bash
nano extensions.conf
```

> Add the following configuration
```vim
[general]


[local]
exten => 100,1,Answer
exten => 100,2,Dial(SIP/john)
exten => 100,3,Hangup

exten => 301,1,Set(VOLUME(RX)=10)
exten => 301,2,Set(VOLUME(TX)=10)
exten => 301,3,Answer
exten => 301,4,Dial(SIP/alice)
exten => 301,5,Hangup

exten => 302,1,Set(VOLUME(RX)=10)
exten => 302,2,Set(VOLUME(TX)=10)
exten => 302,3,Answer
exten => 302,4,Dial(SIP/bob)
exten => 302,5,Hangup
```

Restart Asterisk and check your peers
```bash
asterisk -rvvv

> sip show peers
```

#### Test your configuration
At this point, you should be able to use your asterisk to make calls

* Download a SoftPhone (like Zoiper5, MicroSIP)
* Connect to the asterisk server
* Try to call 100, 301 or 302

## 2. Setup client 

First install some tools

```bash
apt install build-essential git libasound2-dev pulseaudio-module-jack jackd2 python python-dev alsa-tools alsa-utils
```

Install pjsip project
```bash
cd /usr/local/src
wget https://github.com/pjsip/pjproject/archive/2.10.tar.gz
tar -zxvf 2.10.tar.gz
```

To avoid a compile error, comment this code could help

```bash
cd /usr/local/src/pjproject-2.10/pjmedia/src/pjmedia
nano conference.c
```

```c
    /* Check that correct size is specified.
    pj_assert(frame->size == conf->samples_per_frame *
    conf->bits_per_sample / 8);
    */
    
    /* Check for correct size.
    PJ_ASSERT_RETURN( frame->size == conf->samples_per_frame *
    conf->bits_per_sample / 8,
    PJMEDIA_ENCSAMPLESPFRAME);
    */
```

Compile PJSIP project
```bash
cd /usr/local/src/pjproject-2.10/
sudo su
./configure CFLAGS='-fPIC'
make dep
make
make install
cd pjsip-apps/src/python/
sudo python setup.py install
```

If you need to kill pulse audo and start jack_control
```bash
pulseaudio --kill
jack_control  start
qjackctl
```

> if there is problem with jack server https://askubuntu.com/questions/224151/jack-server-could-not-be-started-when-using-qjackctl/935564

## 3. Try to call from client

Firstly, clone this repository. This project is based on [most-voip](https://github.com/crs4/most-voip) library
```bash
cd ~/Documents/
git clone https://github.com/Azunyth/poc-asterisk client-test
cd client-test
python app\call.py -e 100 -c bob
```
