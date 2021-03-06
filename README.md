# DNS simulation
This project is part of a university curriculum which is *Basic Networking Programming*.  
> Author:  
> [*Dat Thinh*](https://github.com/datthinh1801)  
> [*Xuan Ninh*](https://github.com/xuanninh1412)  
> [*Minh Tien*](https://github.com/mt2651)

# Introduction
This project has 2 main features.  
1. Simulate DNS protocol  
2. Illustrate a Man-In-The-Middle attack to spoof DNS reponses from the **Resolver** to the **User**, this is called **DNS Spoofing**.

## Dependencies
- `scapy` (for python 3.9)
- `dnspython` (for python 3.9)
- `netfilterqeuue` (for python 2.7)

# Instruction
## DNS protocol simulation
### Resolver and Nameserver
In this project, **Resolver** and **Nameserver** are operated on the same machine, which we activate them in the `main.py`. Therefore, to run these components, just run the `main.py` file with the command `python3 main.py`.  
### User
In order for the **User** to make a query, run the `UserScript.py`.  
For more information, execute the script with `-h` option (`python3 UserScript.py -h`).  
```
usage: .\UserScript.py [-h] -d [QNAME] [-t [QTYPE]] [-c [QCLASS]] --ip [IP] --port [PORT] [--protocol [PROTOCOL]]

Parse DNS arguments from CLI

optional arguments:
  -h, --help            show this help message and exit
  -d [QNAME], --domain [QNAME]
                        the domain name to be queried
  -t [QTYPE], --type [QTYPE]
                        the type of the query (A by default)
  -c [QCLASS], --class [QCLASS]
                        the class of the query (IN by default)
  --ip [IP]             IP address of the resolver
  --port [PORT]         port number that the resolver is listening
  --protocol [PROTOCOL]
                        tcp/udp (udp by default)
```

## DNS Spoofing
### Network Scanner
To be the man in the middle, we need to know the IP addresses of our 2 targets. For this reason, run the `network_scanner_manual.py` script with the `-t` option to specify the IP range of the network that we want to scan. The outcome of this script will be the ***IP addresses*** as well as ***MAC addresses*** of **all hosts** in the targeted network.  
Use the `-h` option to see the help message.
```
usage: network_scanner_manual.py [-h] -t [TARGET]

optional arguments:
  -h, --help            show this help message and exit
  -t [TARGET], --target [TARGET]
                        IP address of a target host or an IP range of a target network
```
### ARP Spoofer
After having the IP addresses of our targets, run the `ARP_spoofer.py` script and specify the IP addresses of our 2 targets to start spoofing them. This spoof takes advantages of **ARP** to deceive both targets.  
For more information, use the `-h` option to see the help message.
```
usage: ARP spoofer [-h] -t TARGET_IP -g GATEWAY_IP

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET_IP, --target TARGET_IP
                        the IP address of the target machine
  -g GATEWAY_IP, --gateway GATEWAY_IP
                        the IP address of the default gateway
```  
> Originally, this tool was developed to spoof a host and a default gateway. However, this can be run to spoof 2 arbitrary hosts in the same network. If that is the case, we can use `-t` and `-g` interchangeably to specify our 2 targets.  

### DNS Spoofer
Once we become the man in the middle, we can run `DNS_Spoofer.py` to spoof DNS response from Resolver to User.  
For more information, use the `-h` option to see the help message.
```
usage: DNS Spoofer [-h] -t TARGET DOMAIN [TARGET DOMAIN ...] -d
                   [DESTINATION IP ADDRESS] [-l [TRUE]]

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET DOMAIN [TARGET DOMAIN ...], --target-domains TARGET DOMAIN [TARGET DOMAIN ...]
                        Domain names that we want to spoof
  -d [DESTINATION IP ADDRESS], --destined-domain [DESTINATION IP ADDRESS]
                        Our evil IP address that we want the victim to reach
  -l [TRUE], --local [TRUE]
                        Use this option if this script is run locally
```  
# An example demonstration
We run the `main.py` on a machine whose IP address is `10.0.0.5`.  
Then, we'll receive logs as followed:
```
[SERVER]         Listening for UDP connections at 10.0.0.5:5252...
[SERVER]         Listening for TCP connections at 10.0.0.5:5353...
[RESOLVER]       Listening for clients' requests at 10.0.0.5:9292...
```  
We run the `UserScript.py` to make a query for `facebook.com`. Here, we run this script on a machine whose IP address is `10.0.0.7`.
```
python3 UserScript.py -d facebook.com --ip 10.0.0.5 --port 9292
```
The result in return is `facebook.com.;1;1;205;69.171.250.35`. The last part of the reponse (`69.171.250.35`) is the IP address of `facebook.com`.  
In addition, if we examine the resolver's log, we can see a message specifying that the resolver has received a request from a user. 
```
[RESOLVER]       Receive a request for facebook.com;A;IN from ('10.0.0.7', 49775) using UDP
```
> If we want to specify the Resolver to make a query to the Nameserver via TCP, we need to execute the script with the `--protocol tcp` option.
### Now, let's do some hacking.  
First and foremost, as we already know the IP addresses of the machines that run the `main.py` and `UserScript.py`, it is unnecessary to run the `network_scanner_manual.py`.  
Next, we need to run the `ARP_spoofer.py` to make us become the man in the middle between the Resolver and User.
```
sudo python3 ARP_spoofer.py -t 10.0.0.7 -g 10.0.0.5
# or
sudo python3 ARP_spoofer.py -t 10.0.0.5 -g 10.0.0.7
# either is ok
```
If the script is executed successfully, a successful message will be printed on the console.
```
[+] Spoof ['10.0.0.5'] and ['10.0.0.7'] successfully!
```

Finally, run our `DNS_spoofer.py`.
```
sudo python DNS_spoofer.py -t facebook.com google.com -d 10.0.0.10
```
Here, we specify the domains that we want to spoof. In this example, we will spoof any responses that carry the IP addresses of `facebook.com` and `google.com`.  
These IP addresses will be changed to the one specified by the `-d` option, which is `10.0.0.10` in this example.  
  
Now let's come back to the machine that runs `UserScript.py` and make a query for `facebook.com` again.
```
python3 UserScript.py -d facebook.com --ip 10.0.0.5 --port 9292
```

This time, the response is `facebook.com.;1;1;205;10.0.0.10` which carries the spoofed IP address specified by our `DNS_spoofer`.  
But if we make a query for `youtube.com`, the response is not spoofed (`youtube.com.;1;1;43;172.217.31.238`).
