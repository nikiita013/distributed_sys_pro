# Python TCP Client A
import socket
from os import system
from threading import Thread
from SocketServer import ThreadingMixIn
import sqlite3
import time
from imp import load_source
module = load_source('functions', '../functions.py')

#creating its database sql

tcpParent = -1
tcpFile = -1

def updateD(data):
    data = list(data)
    data[4] = '5'
    return ''.join(data)

# root_ip = raw_input("Enter the IP of root: ")
# port_ip = raw_input("Enter the port no. of root: ")



class QueryThread(Thread):
    def __init__(self, tcpServer):
        Thread.__init__(self)
        self.tcpParent = tcpParent

    def run(self):
        print "starting query run"
        while True:
            input_query = raw_input("Enter the file name to search: ")
            (flag, MESSAGE) = module.queryData(input_query)
            if flag == 0:
                print "MESSGe 6: "
                self.tcpParent.send(MESSAGE)
            else:
                pass
                # print MESSAGE
            #search in its own, if yes display already have it
            #if not request to the parent
            #receive the reply from parent
            #make connection to that node
            #make ftp connection
            #take the file
            #update the parents about this new addition           
            
class ServerThread(Thread):
    def __init__(self, tcpServer):
        Thread.__init__(self)
        self.tcpServer = tcpServer

    def run(self):
        global tcpParent
        threads = []
        while True:
            self.tcpServer.listen(20)
            #print "Root : Waiting for connections from TCP clients..."
            try:
                (conn, (ip,port)) = self.tcpServer.accept()
                newthread = ClientThread(ip,port,conn)
                newthread.start()

            except Exception as e:
                print("something's wrong with %s:%d. Exception is %s" % (ip, port, e))
            threads.append(newthread)
        for t in threads:
            t.join()
        
class ClientThread(Thread):
    def __init__(self,ip,port,conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        #print "[+] New server socket thread started for " + ip + ":" + str(port)
    def run(self):
        global tcpParent
        #global tcpFile
        while True :
            data = self.conn.recv(2048)
            # print data
            if module.decode(data) == 1:
                tcpParent.send(updateD(data))
                if module.selfid.getCount() < 2:
                    module.selfid.incCount();
                    if module.selfid.getCount() == 1:
                        module.selfid.setLchild(self.conn)
                        self.conn.send("msgr:1;child:left;")
                        MESSAGE = "msg:3;" + "wprevIP:" + module.selfid.getIP() + ";wprevPort:" + str(module.selfid.getPort()) + ";wnewIP:" + module.selfid.getIP() + ";wnewPort:" + str(module.selfid.getPort()) + ";"
                    elif module.selfid.getCount() == 2:
                        module.selfid.setRchild(self.conn)
                        self.conn.send("msgr:1;child:right;")
                        MESSAGE = "msg:4;" + "child:" + module.selfid.getSelfChild() +";jumps:1;wprevIP:" + module.selfid.getIP() + ";wprevPort:" + str(module.selfid.getPort()) + ";"
                        print "Sending Message 4: ", MESSAGE
                    else:
                        pass
                    tcpParent.send(MESSAGE)
                    module.insertData(data)
                else:
                    pass
            elif module.decode(data) == 3:
    			print "Received Message 3 and sending it to parent: ", data
    			tcpParent.send(data)
            elif module.decode(data) == 4:
				child = data[data.find('child') + 6:]
				child = child[:child.find(';')]
				jumps = data[data.find('jumps') + 6:]
				jumps = int(jumps[:jumps.find(';')])
				rem_str = data[data.find('wprev'):]
				if child == 'right':
					child = module.selfid.getSelfChild()
					jumps += 1
					MESSAGE = 'msg:4;child:' + child + ';jumps:' + str(jumps) + ';' + rem_str
					tcpParent.send(MESSAGE)
				elif child == 'left':
					jumps -= 1
					MESSAGE = 'msgr:4;child:' + child + ';jumps:' + str(jumps) + ';' + rem_str 
					conn = module.selfid.getRchild()
					conn.send(MESSAGE)
            elif module.decode(data) == 5:
                tcpParent.send(data)
                module.insertData(data)
            elif module.decode(data) == 6:
                print "Recived message 6!"
                t_data = data
                data = data.split(';')
                temp = data.pop()
                d = [] #list of data
                for i in data:
                    d.append((i[:i.find(':')], i[i.find(':') + 1:]))
                
                # print d
                # print d[1][1]
                (flag, MESSAGE) = queryData(d[1][1])
                # print flag, " ", MESSAGE
                if flag == 0:
                    #send to its parent
                    tcpParent.send(t_data)
                else:
                    #make connection to send
                    #connecting to the parent
                    tcpReply = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    tcpReply.connect((d[2][1], int(d[3][1])))

                    MESSAGE = module.getfiledest(d[1][1])
                    # MESSAGE = "msg:7;"
                    print 'successful'
                    tcpReply.send(MESSAGE)
                    tcpReply.close()
            elif module.decode(data) == 7:
                print "Recived message 7! Now can connect to peer containign file directly"
                t_data = data
                data = data.split(';')
                temp = data.pop()
                d = [] #list of data
                for i in data:
                    d.append((i[:i.find(':')], i[i.find(':') + 1:]))
                dip = d[2][1]
                dport = d[3][1]
                print "dip:", dip, ":", dport
                tcpFile = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcpFile.connect((dip, int(dport)))
                print d[1][1]
                print "Message 8 send"
                MESSAGE = "msg:8;get:" + d[1][1] + ";ip:" + module.selfid.getIP() + ";port:" + str(module.selfid.getPort()) + ";" 
                tcpFile.send("msg:8;get:" + d[1][1] + ";ip:" + module.selfid.getIP() + ";port:" + str(module.selfid.getPort()) + ";")
                size = tcpFile.recv(1024)
                ss = int(size)
                print decode(MESSAGE)
                print "After sending message 8"
                f = open(d[1][1], "wb")
                count = 0
                while(count < ss):
                    count += 1
                    l = tcpFile.recv(1)
                    f.write(l)
                    # print "jojo"
                    if count == ss:
                        break
                print "Copy Complete"
                f.close()
                tcpFile.close()
            elif module.decode(data) == 8:
                print "Message 8 recieved "
                data = data.split(';')
                temporary =  data.pop()
                d = []
                for i in data:
                    d.append((i[:i.find(':')], i[i.find(':') + 1:]))
                print d[2][1], " : ", d[3][1]
                temp = system('ls -l ' + d[1][1] + ' > a.txt')
                temp = open('a.txt', 'r')
                temp = temp.readlines()[0]
                size = int(temp.split(' ')[4])
                temp = system('rm -rf a.txt')
                
                self.conn.send(str(size))

                try:
                    print "inside 8 try"
                    f = open(d[1][1], 'rb')
                    r = f.read(1)
                    count = 0
                    while r:
                        self.conn.send(r)
                        count += 1
                        r = f.read(1)
                    print "Finished sending: ", count 
                    f.close()   
                    c.shutdown()
                    c.close()
                except Exception as e:
                    pass
            else:
                pass
 
class ParentThread(Thread):#check  Thread to obj
    def __init__(self,conn):
        Thread.__init__(self)
        self.tcpParent = conn
        #print "[+] New server socket thread started for " + ip + ":" + str(port)
    def run(self):
        while True :
            data = self.tcpParent.recv(2048)
            if module.RDecode(data)== 4:
                jumps = data[data.find('jumps') + 6:]
                jumps = int(jumps[:jumps.find(';')])
                # print data#
                # print "Jumps: ", jumps
                rem_str = data[data.find('wprev'):]         
                if jumps == 0:
                	print "Heya received 0 jumps. Sending message to parent"
                	# print module.selfid.getPort()
                	MESSAGE = "msg:3;" +  rem_str + "wnewIP:" + module.selfid.getIP() + ";wnewPort:" + str(module.selfid.getPort()) + ";"
                	print "Message send by leaf to parent: ", MESSAGE
                	self.tcpParent.send(MESSAGE)
                else:
                	jumps = jumps - 1
                	MESSAGE = 'msgr:4;child:random' + ';jumps:' + str(jumps) + ';' + rem_str
                	print "Sending message 4 to left child: ", MESSAGE
                	conn = module.selfid.getLchild()
                	conn.send(MESSAGE)
            elif module.decode(data) == 9:
                MESSAGE = 'msgr:9;type:pong;'
                self.tcpParent.send(MESSAGE)
                print 'Sending Pong Message'
# Multithreaded Python server : TCP Server Socket Program Stub

# print "YOYOYOYOYO"

#starting server thread
BUFFER_SIZE = 1024  # Usually 1024, but we need quick  
tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((module.selfid.getIP(), module.selfid.getPort()))
module.selfid.set(module.selfid.getIP(), tcpServer.getsockname()[1])
print 'Server => ip: ' + module.selfid.getIP() + ' port: ' + str(module.selfid.getPort())
servert = ServerThread(tcpServer)
servert.start()
#c = createdatabase()
pingt = module.PingPong()
pingt.start()

#connecting to the root server
root = module.node('0.0.0.0', 3003)
BUFFER_SIZE = 2000
tcpRoot = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpRoot.connect((root.getIP(), root.getPort()))
MESSAGE = "msg:2;"
 
while True:
    tcpRoot.send(MESSAGE)    
    data = tcpRoot.recv(BUFFER_SIZE)
    #decode
    #print data
    # print '\n'
    values = module.RDecode(data)
    # print values[1][1]
    # print values[2][1]

    parent = module.node(values[1][1], int(values[2][1]))

    tcpRoot.close()
    break
print "PARENT DETAILS"
print parent.getIP(), " ", parent.getPort()

MESSAGE = module.metadatacreate()
print MESSAGE
module.insertData(MESSAGE)


#connecting to the parent
tcpParent = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpParent.connect((parent.getIP(), parent.getPort()))
tcpParent.send(MESSAGE)
data = tcpParent.recv(BUFFER_SIZE)

childpos = module.RDecode(data)
print "IP: ", module.selfid.getIP(), "Port: ", module.selfid.getPort()
print "Self position: ", childpos
module.selfid.setSelfChild(childpos)

parentt = ParentThread(tcpParent)
parentt.start()

print "making thread!!"
queryt = QueryThread(tcpParent)
queryt.start()

queryt.join()

parentt.join()