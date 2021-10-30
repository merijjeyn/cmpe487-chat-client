import nmap

nm = nmap.PortScanner()
nm.scan('192.168.1.0/24', '12345')
hosts = nm.all_hosts()
for host in hosts:
    print(nm[host]['tcp'][12345])