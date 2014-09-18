## ISSUES

### Past expiry error handling
Error handling needs to be implemented for the cases when the user specifies expiry earlier than now.

### Check & fix ['Order Status' page](https://178.79.185.250/future/query/)
It must show correct info at all stages of the order life cycle: Submitted-Cancelled/Paid-Expired.

##	ArchLinux Install

### Disable ping responses
(instructions need completion)

[systemd only applies settings from /etc/sysctl.d/* and /usr/lib/sysctl.d/*.](https://wiki.archlinux.org/index.php/sysctl)
If you customized /etc/sysctl.conf, you must rename it as /etc/sysctl.d/99-sysctl.conf.


	# echo "1" > /proc/sys/net/ipv4/icmp_echo_ignore_all
	
	To re-enable ping request:
	# echo "0" > /proc/sys/net/ipv4/icmp_echo_ignore_all
	Or:
	"net.ipv4.icmp_echo_ignore_all = 1" >> /etc/sysctl.conf

### Change ssh port (from default 22)

    Edit /etc/ssh/sshd_config
	#Port 22122

    # systemctl restart sshd


##	Users & Groups: Create & Configure

    # groupadd -r sudo
    # EDITOR=nano visudo
	# visudo /etc/sudoers   # to enable members of group sudo to use sudo.

	# useradd -m -g users -G sudo wheel -s /bin/bash tobin
	# passwd tobin
	
	ssh tobin@server.tld
	
	Test that user tobin can do anything with sudo, e.g. touch /root/somefile

###	Enable key-based authentication

    On local machine:
	$ ssh-keygen -t ecdsa -b 521
	$ ssh-copy-id -i ~/.ssh/id_ecdsa.pub bh@178.79.185.250

	
    Or copy pubkey to remote server:
	$ scp -P 22122 ~/.ssh/id_ecdsa.pub root@212.71.235.160:

	Then, on remote server, append your pubkey to file  ~/.ssh/authorized_keys
	$ ssh username@remote-server.org
	$ mkdir ~/.ssh
	$ cat ~/id_ecdsa.pub >> ~/.ssh/authorized_keys
	$ rm ~/id_ecdsa.pub
	$ chmod 600 ~/.ssh/authorized_keys

### Disable remote root login

	Edit /etc/ssh/sshd_config
	#PermitRootLogin no
	
	# systemctl restart sshd

	# gpasswd -d root wheel

### Disable password-based authentication
    ...
    
###	Dedicated user bh for running bh software:

	# groupadd bh
	# useradd -m -g bh -G sudo -s /bin/bash bh


## Install Bitcoin client

Install [bitcoind](https://bitcoin.org/en/download) and make it run at system startup (as root):
    
    pacman -S bitcoin-daemon
    
    https://wiki.archlinux.org/index.php/bitcoin#Installation
    Systemd service file:
    
    cat >/etc/systemd/system/bitcoind.service <<EOF
    [Unit]
    Description=Bitcoin daemon service
	After=network.target
	
    [Service]
    User=bh
    Type=forking
    PIDFile=/home/bh/.bitcoin/bitcoind.pid
    ExecStart=/usr/bin/bitcoind -daemon
    ExecStop=/usr/bin/bitcoind stop
	Restart=always
	KillSignal=SIGQUIT

    [Install]
    WantedBy=multi-user.target
    EOF

As _bh_ user, create bitcoin config, start the service, and check it is running:

    mkdir ~/.bitcoin/
    cat >~/.bitcoin/bitcoin.conf <<EOF
    rpcuser=bitcoinrpc
    rpcpassword=AR3pgfhfggfhhgfh54ydaeRHgj89sq4wsfdd
    EOF
    chmod 600 ~/.bitcoin/bitcoin.conf
    sudo systemctl start bitcoind
    sudo systemctl status bitcoind
    bitcoind listaccounts # give it up to 1min to start


## Setup Python environment

    pacman -S python python-virtualenvwrapper

Add to `~/.bashrc`:

    . /usr/bin/virtualenvwrapper.sh

Then,

    mkvirtualenv -p /usr/bin/python3 bhpy
    workon bhpy
    pip install numpy scipy django uwsgi

You may need to install `blas`, `lapack`, `gcc-fortran` packages for SciPy to compile on ArchLinux.
Alternatively, install SciPy and NumPy from distribution provided packages (for python3) 
and then use option
    mkvirtualenv --system-site-packages


## Clone Git repo

    git clone git@github.com:latgarf/bh.git ~/bh

    .gitignore should be configured properly.

## Install BHSDK

    cd ~/bh/bhsdk
    workon bhpy
    pip uninstall bhsdk
    pip install .       # note the trailing dot

`~/bhsdk-config/` will be created.


## Setup Nginx

Create `/etc/nginx/uwsgi_params` if absent:

    uwsgi_param  QUERY_STRING       $query_string;
    uwsgi_param  REQUEST_METHOD     $request_method;
    uwsgi_param  CONTENT_TYPE       $content_type;
    uwsgi_param  CONTENT_LENGTH     $content_length;

    uwsgi_param  REQUEST_URI        $request_uri;
    uwsgi_param  PATH_INFO          $document_uri;
    uwsgi_param  DOCUMENT_ROOT      $document_root;
    uwsgi_param  SERVER_PROTOCOL    $server_protocol;
    uwsgi_param  HTTPS              $https if_not_empty;

    uwsgi_param  REMOTE_ADDR        $remote_addr;
    uwsgi_param  REMOTE_PORT        $remote_port;
    uwsgi_param  SERVER_PORT        $server_port;
    uwsgi_param  SERVER_NAME        $server_name;

Add to `server{}` block of `nginx.conf`:

    location /future {
        include     uwsgi_params;
        uwsgi_pass  127.0.0.1:8011;
    }
    location /static {
        root  /home/bh/bh/trunk/bhsite;
    }

Adjust `root` appropriately.


## Configure uwsgi

Edit `trunk/uwsgi.ini`:

	[uwsgi]
	master=true
	socket=127.0.0.1:8011
	daemonize=%d/../uwsgi.log
	pidfile=%d/../uwsgi.pid
	home=/home/bh/.virtualenvs/bhpy
	chdir=%d
	module=btchedge.wsgi:application
	processes=1
	threads=1
	#buffer-size=32768
	plugin=python


## Start uwsgi, Django

    cd ~/bh/trunk
    workon bhpy
    ./manage.py syncdb
    uwsgi --ini uwsgi.ini
    
    /home/bh/.virtualenvs/bhpy/bin/uwsgi --ini uwsgi.ini --py-autoreload=3

## ?! Manually create DB table transaction_ids ?

	sqlite> CREATE TABLE "transaction_ids" (
    "order_id" varchar(32) NOT NULL PRIMARY KEY,
    "transaction_id" varchar(64) NOT NULL
	);

There's probably a better way to do it - update this section if you know how to!
    bitcoind/bhdb_schema.sql

## Website is ready at  [/future/](http://localhost/future/)


## Payment processing

Setup periodic execution of payment processing scripts:

    crontab - <<EOF
    MAILTO=your@email.tld
    */1 * * * * cd $HOME/bh/bitcoind && . /usr/bin/virtualenvwrapper.sh && workon bhpy && ./paymentchecker.py && ./autopay.py --pay
    # */2 * * * * cd $HOME/bh/bitcoind && . /usr/bin/virtualenvwrapper.sh && workon bhpy && ./fetch_bitstamp_history.py
    EOF

----------------------------------------------------------------------------
