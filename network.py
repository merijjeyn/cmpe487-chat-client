import threading
import socket
import nmap
import json
import time

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

    def addToActiveUsers(name, ip):
        with open('active_users.json', 'w+') as f:
            active_users = json.loads(f.read())
            if name not in active_users:
                active_users[name] = ip
                f.write(json.dumps(active_users))
                if DEBUG: print('Wrote', name, 'with ip', ip, 'to active users')

    def getNamefromIP(ip):
        with open('active_users.json', 'r') as f:
            active_users = json.loads(f.read())
            for user in active_users:
                if active_users[user] == ip:
                    return user

    def getIpFromName(name):
        with open('active_users.json', 'r') as f:
            active_users = json.loads(f.read())
            return active_users[name]


    def addMessageToDatabase(conv, name, body):
        with open('conversations.json', 'w+') as f:
            conversations = json.loads(f.read())
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
                if DEBUG: print('sending discover to', ip)
                s.connect((ip, PORT))
                message = self.constructMessage(1)
                s.sendall(message)
                time.sleep(0.1)

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

                                dataDict = json.loads(data)
                                if dataDict['type'] == 2:
                                    # write the new user to the active_users.json
                                    if DEBUG: print('Received a discover response from', dataDict['name'], 'with ip', dataDict['IP'])
                                    self.addToActiveUsers(dataDict['name'], dataDict['IP'])
                                    
                        ss.settimeout(None)

                    except:
                        # TODO: didn't receive a discover response
                        if DEBUG: print('Did not receive a discover response from', ip)
            except:
                # TODO: useless ip
                if DEBUG: print('Inactive ip:', ip)

    def sendDiscoverResponse(self, ip):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                if DEBUG: print('Sending discover response to', ip)
                s.connect((ip, PORT))
                message = self.constructMessage(2)
                s.sendall(message)
            except:
                if DEBUG: print('Discover response could not be sent')

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
                    active_users = json.loads(f.read())
                    for user in active_users:
                        if active_users[user] == ip:
                            active_users.pop(user)
                    f.write(json.dumps(active_users))

    def listener(self):
        # TODO: Check if self here causes any problems because of the thread
        while True:
            dataDict = {}
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', PORT))
                s.listen()
                conn, addr = s.accept()
                if DEBUG: print('Connected with', addr)
                with conn:
                    while True:
                        data = conn.recv(10240)
                        if not data:
                            break

                        dataDict = json.loads(data)
                        if DEBUG: print('Received data:', data)

            if dataDict['type'] == '1':
                # Received discover, reply with discover response and add it the active_users
                self.sendDiscoverResponse(dataDict['IP'])
                self.addToActiveUsers(dataDict['name'], dataDict['IP'])

            elif dataDict['type'] == '2':
                # Should not receive a discover response out of nowhere
                pass
            elif dataDict['type'] == '3':
                # Received normal message, update the messages
                self.addMessageToDatabase(dataDict['name'], dataDict['name'], dataDict['body'])
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
