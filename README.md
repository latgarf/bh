##	ArchLinux Install

### Disable ping responses

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
	# nano /etc/sudoers   # to enable members of group sudo to use sudo.

	# useradd -m -g users -G sudo wheel -s /bin/bash tobin
	# passwd tobin
	
	ssh tobin@server.tld
	
	Test that user tobin can do anything with sudo, e.g. touch /root/somefile

###	Enable key-based authentication

    On local machine:
	$ ssh-keygen -t ecdsa -b 521
	
	Copy pubkey to remote server:
	$ scp -P 22122 ~/.ssh/id_ecdsa.pub root@212.71.235.160:
	
	On remote server, append your pubkey to file  ~/.ssh/authorized_keys
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


##	Dedicated OS user bh for running the software:

	# groupadd bh
	# useradd -m -g bh -G sudo -s /bin/bash bh
	

### Install Bitcoin client

Install [Bitcoin](https://bitcoin.org/en/download) daemon (bitcoind) and make it run at system startup (as root):
    
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

### Setup Python environment

Install Python 3, `python-virtualenv`, and `virtualenvwrapper`:

    pacman -S python python-virtualenvwrapper

On Arch Linux, add to `~/.bashrc`:

    . /usr/bin/virtualenvwrapper.sh

Then,

    mkvirtualenv -p /usr/bin/python3 bhpy
    workon bhpy
    pip install numpy scipy django uwsgi

You may need to install `libblas-dev`, `liblapack-dev`, `gfortran` (Ubuntu); `blas`, `lapack`, `gcc-fortran` (Arch Linux) packages for SciPy to compile.
Alternatively, install SciPy and NumPy from distribution provided packages (for Python 3!) and supply `--system-site-packages` to mkvirtualenv.

### Sources

Clone the repository into `~/bh`:

    git clone git@github.com:latgarf/bh.git ~/bh

### Install BHSDK

    cd ~/bh/bhsdk
    workon bhpy
    pip install . # note trailing dot

`~/bhsdk-config/` will be created.

### Setup Nginx and start Django

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
        root  /home/arkadi/bh/trunk/bhsite;
    }

Adjust `root` appropriately.
Edit `trunk/uwsgi.ini` and set `home=` to the path to _bhpy_ virtualenv. Then,

    cd ~/bh/trunk
    workon bhpy
    ./manage.py syncdb
    uwsgi --ini uwsgi.ini

The website is ready at [/future/](http://localhost/future/).

### Payment processing

Setup periodic execution of payment processing scripts:

    crontab - <<EOF
    MAILTO=your@email.tld
    */2 * * * * cd $HOME/bh/bitcoind && ./fetch_bitstamp_history.py
    */1 * * * * cd $HOME/bh/bitcoind && ./paymentchecker.py && ./autopay.py --pay
    EOF
