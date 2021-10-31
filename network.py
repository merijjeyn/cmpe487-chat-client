import threading
import socket
import nmap
import json
import time

PORT = 12345
DEBUG = True

class Network:

    def constructMessage(self, type, body=''):
        if type == 3:
            res = '{"type":' + str(type) + ', "name":"' + self.name + '", "body":"' + body + '"}'
        else:
            res = '{"type":' + str(type) + ', "name":"' + self.name + '", "IP":"' + self.ip + '"}'
        
        if len(res) > 2560: res = res[:2560]
        return bytes(res, 'utf-8')

    def addToActiveUsers(self, name, ip):
        with open('active_users.json', 'w+') as f:
            try:
                active_users = json.loads(f.read())
            except:
                active_users = {}
            if name not in active_users:
                active_users[name] = ip
                
                f.write(json.dumps(active_users))
                if DEBUG: print('Added', name, 'with ip', ip, 'to active users')

    def getNamefromIP(self, ip):
        with open('active_users.json', 'r') as f:
            try:
                active_users = json.loads(f.read())
            except:
                active_users = {}
            for user in active_users:
                if active_users[user] == ip:
                    return user

    def getIpFromName(self, name):
        with open('active_users.json', 'r') as f:
            try:
                active_users = json.loads(f.read())
            except:
                active_users = {}
            return active_users[name]


    def addMessageToDatabase(self, conv, name, body):
        with open('conversations.json', 'w+') as f:
            try:
                conversations = json.loads(f.read())
            except Exception as e:
                conversations = {}

            storedMsg = name + '::' + body
            if conv in conversations:
                convArray = conversations[conv]
                convArray.append(storedMsg)
                conversations[conv] = convArray
            else:
                conversations[conv] = [storedMsg]
            
            f.write(json.dumps(conversations))

    def sendDiscover(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(0.2)
                s.connect((ip, PORT))
                message = self.constructMessage(1)

                if DEBUG: print('Sending discover message:', message)
                s.sendall(message)
            except Exception as e:
                if DEBUG: print('Inactive ip:', ip)

    def sendDiscoverResponse(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                if DEBUG: print('Sending discover response to', ip)
                s.connect((ip, PORT))
                message = self.constructMessage(2)
                s.sendall(message)
            except Exception as e:
                if DEBUG: print('Could not send discover response with error:', e)

    def sendMessage(self, ip, body):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                if DEBUG: print('Sending message to ip', ip, 'with body', body)
                s.connect((ip, PORT))
                message = self.constructMessage(3, body)
                s.sendall(message)
                self.addMessageToDatabase(self.getNamefromIP(ip), self.name, body)
            except:
                if DEBUG: print('Message could not be sent')
                with open('active_users.json', 'w+') as f:
                    try:
                        active_users = json.loads(f.read())
                    except:
                        active_users = {}
                    for user in active_users:
                        if active_users[user] == ip:
                            active_users.pop(user)
                    
                    f.write(json.dumps(active_users))

    def listener(self):
        # TODO: Check if self here causes any problems because of the thread
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', PORT))
            s.listen()
            while True:
                dataDict = {}
                conn, addr = s.accept()
                if DEBUG: print('Connected with', addr)
                with conn:
                    while True:
                        data = conn.recv(10240)
                        if DEBUG: print('Received message:', data)
                        if not data:
                            break

                        dataDict = json.loads(data.decode('utf-8'))

                if dataDict['type'] == 1:
                    # Received discover, reply with discover response and add it the active_users
                    time.sleep(0.05)
                    self.sendDiscoverResponse(dataDict['IP'])
                    self.addToActiveUsers(dataDict['name'], dataDict['IP'])

                elif dataDict['type'] == 2:
                    # Should not receive a discover response out of nowhere
                    self.addToActiveUsers(dataDict['name'], dataDict['IP'])
                elif dataDict['type'] == 3:
                    # Received normal message, update the messages
                    self.addMessageToDatabase(dataDict['name'], dataDict['name'], dataDict['body'])
                else:
                    if DEBUG: print('Received unknown message type')



    def __init__(self):
        # Initialize self ip
        sckt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sckt.connect(('192.168.1.1', 81))
        self.ip = sckt.getsockname()[0]
        sckt.close()

        # Get the name from terminal
        print('What should your username be?')
        self.name = input()

        # Scan ips
        nm = nmap.PortScanner()
        nm.scan('192.168.1.0/24', str(PORT))
        hosts = nm.all_hosts()

        # initialize listener
        listener = threading.Thread(target=self.listener, name='listener')
        listener.start()

        for host in hosts:
            # Send discover messages to ips
            if host != self.ip:
                self.sendDiscover(host)