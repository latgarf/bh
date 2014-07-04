### Dedicated OS user

Optionally, create an OS user dedicated to running the software (as root):

    pacman -S sudo
    groupadd -r sudo
    useradd -m -s /bin/bash -G sudo bh

Edit `/etc/sudoers` to enable _sudo_ group to use `sudo`.

### Install Bitcoin client

Install Bitcoin Daemon software and make it run at system startup (as root):
    
    pacman -S bitcoin-daemon
    cat >/etc/systemd/system/bitcoind.service <<EOF
    [Unit]
    Description=Bitcoin daemon

    [Service]
    User=bh
    Type=forking
    PIDFile=/home/bh/.bitcoin/bitcoind.pid
    ExecStart=/usr/bin/bitcoind -daemon
    ExecStop=/usr/bin/bitcoind stop

    [Install]
    WantedBy=multi-user.target
    EOF

As _bh_ user, create bitcoin config, start the service, and check it is running:

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

### Install BHSDK

    cd bhsdk
    workon bhpy
    pip install . # note trailing dot

`~/bhsdk-config/` will be created.
Also install [bitcoind](https://bitcoin.org/en/download). 

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

    cd trunk
    workon bhpy
    ./manage.py syncdb
    uwsgi --ini uwsgi.ini

The website is ready at [/future/](http://localhost/future/).
