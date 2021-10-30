import threading
import socket
import nmap
import json

HOST = '127.0.0.1'
PORT = 12345
DEBUG = True

class Network:

    def constructMessage(self, type, body=''):
        if type == 3:
            # TODO: make sure message is shorter than 10KB
            return b'{type:' + str(type) + ', name:' + self.name + ', body:' + body + '}'
        else:
            return b'{type:' + str(type) + ', name:' + self.name + ', IP:' + self.ip + '}'


    def sendDiscover(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip, PORT))
                message = self.constructMessage(1)
                s.sendall(message)
                
                # message sent, now listen for discover response messages
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
                    try:
                        ss.settimeout(0.2)
                        ss.bind((ip, PORT))
                        ss.listen()
                        conn, addr = ss.accept()
                        with conn:
                            while True:
                                data = conn.recv(10240)
                                if not data:
                                    break

                                # TODO: Handle discover response
                        ss.settimeout(None)

                    except:
                        # TODO: didn't receive a discover response
                        if DEBUG: print('Didnt receive a discover response from', ip)
            except:
                # TODO: useless ip
                if DEBUG: print('Inactive ip:', ip)

    def sendDiscoverResponse(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip, PORT))
                message = self.constructMessage(2)
                s.sendall(message)
            except:
                if DEBUG: print('Discover response could not be sent')

    def sendMessage(self, ip, body):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((ip, PORT))
                message = self.constructMessage(3, body)
                s.sendall(message)
            except:
                # TODO: Remove the user from active_users
                if DEBUG: print('Message could not be sent')


    def listener(self):
        # TODO: Check if self here causes any problems because of the thread
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', PORT))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    while True:
                        data = conn.recv(10240)
                        if not data:
                            break
                        # TODO: handle different messages
                        dataDict = json.loads(data)
                        if dataDict['type'] == '1':
                            # Received discover, reply with discover response and add it the active_users
                            ip = dataDict['IP']
                            self.sendDiscoverResponse(ip)
                        elif dataDict['type'] == '2':
                            # Should not receive a discover response out of nowhere
                            pass
                        elif dataDict['type'] == '3':
                            # Received normal message, update the messages
                            pass
                        else:
                            if DEBUG: print('Received unknown message type')



    def __init__(self):
        # Initialize self ip
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self.ip = local_ip

        # Get the name from terminal
        print('What should your username be?')
        self.name = input()


        # Scan ips
        nm = nmap.PortScanner()
        nm.scan('192.168.1.0/24', str(PORT))
        hosts = nm.all_hosts()

        for host in hosts:
            # Send discover messages to ips
            self.sendDiscover(host)

        # initialize listener
        listener = threading.Thread(target=self.listener, name='listener')
        listener.start()



# if __name__ == '__main__':
    # nw = Network()
