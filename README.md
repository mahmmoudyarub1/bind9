/install BIND9 

sudo apt update    
sudo apt install bind9    
sudo systemctl start bind9    
sudo systemctl enable bind9    
sudo systemctl status bind9    


/config named.conf

options {    
    directory "/var/cache/bind";    
    forwarders {    
        8.8.8.8;    
    };    
    listen-on { any; };    
    allow-query { any; };    
    dnssec-validation auto;    
    auth-nxdomain no;    
    listen-on-v6 { any; };    
};    


