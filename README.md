### Setup Python environment

Install Python 3, `python-virtualenv`, and `virtualenvwrapper`. Then,

    mkvirtualenv -p /usr/bin/python3 bh
    workon bh
    pip install numpy scipy django uwsgi

You may need to install `libblas-dev`, `liblapack-dev`, `gfortran` packages for SciPy to compile.
Alternatively, install SciPy and NumPy from distribution provided packages (for Python 3!) and supply `--system-site-packages` to mkvirtualenv.

### Install BHSDK

    cd bhsdk
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
Edit `trunk/uwsgi.ini` and set `home=` to the path to _bh_ virtualenv. Then,

    workon bh
    cd trunk
    uwsgi --ini uwsgi.ini

The website is ready at http://localhost/future/
