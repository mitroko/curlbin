# curlbin

# Usage examples
ls -1 | curl -i --upload-file - https://l.stremki.net  
curl -i --upload-file ./somefile https://l.stremki.net  
alias curlbin='curl -i --upload-file - https://l.stremki.net'  
ls -1 | curlbin  

# TODO
Docker container

# Installation:
- Add new system user to run curlbin with:  
  Example: useradd -d /var/spool/curlbin -c 'uWSGI user curlbin' -M -r -s /sbin/nologin w3curlbin
- install nginx and configure server using curlbin.conf.nginx template
- install uwsgi and configure vassal using curlbin.ini.uwsgi template
- install curlbin.py to desired path and make it executable
- install dependencies for curlbin.py
- install crontab using curlbin.crontab template
- create /var/spool/curlbin /var/log/uwsgi/curlbin directories and properly assign ACLs and selinux context.
- start nginx and uwsgi
