import socket
from threading import Thread
from SocketServer import ThreadingMixIn
import sqlite3
import time
from imp import load_source
module = load_source('functions', '../functions.py')

query = ""
wnew = module.node('0.0.0.0', 3003)
wprev = module.node(-1, -1)

# Multithreaded Python server : TCP Server Socket Program Stub
module.selfid.set('0.0.0.0', 3003)

class ClientThread(Thread):
    def __init__(self,ip,port, conn):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        #print "[+] New server socket thread started for " + ip + ":" + str(port)
    def run(self):
        global tcpParent
        global wnew
        global wprev
        #global module.selfid
        global c
        while True:
            data = self.conn.recv(2048)
            if module.decode(data) == 4:
                child = data[data.find('child') + 6:]
                child = child[:child.find(';')]
                jumps = data[data.find('jumps') + 6:]
                jumps = int(jumps[:jumps.find(';')])
                rem_str = data[data.find('wprev'):]
                jumps -= 1
                if child == 'left':
                    MESSAGE = 'msgr:4;child:random' + ';jumps:' + str(jumps) + ';' + rem_str
                    conn = module.selfid.getRchild()
                    conn.send(MESSAGE)
                    print "Sending to Right Child Message 4: ", MESSAGE
                else:
                    jumps += 1
                    MESSAGE = 'msgr:4;child:random' + ';jumps:' + str(jumps) + ';' + rem_str
                    conn = module.selfid.getLchild()
                    conn.send(MESSAGE)
                    print "Sending to Left child Message 4: ", MESSAGE
    				# print "hello world"
            elif module.decode(data) == 3:
    			#if data.find('msg:3') != -1:
    			# print data
                print "Hola !Received message 3"
                data = ''.join(list(data[:len(data) - 1]))
                data = data[data.find(';') + 1:]
                data_values = data.split(';')
                values = {}
                for i in data_values:
                    values[i[:i.find(':')]] = i[i.find(':') + 1:]
                wprev.set(values['wprevIP'], int(values['wprevPort']))
                wnew.set(values['wnewIP'], int(values['wnewPort']))
                print "W Updated successfully As: ", wprev.getIP(), ":", wprev.getPort(), "  ", wnew.getIP(), ":", wnew.getPort()
            elif module.decode(data) == 2:
                MESSAGE = 'msgr:2;'
                MESSAGE += 'wip:' + wnew.getIP() + ';'
                MESSAGE += 'wport:' + str(wnew.getPort()) + ';'
                self.conn.send(MESSAGE)
            elif module.decode(data) == 1:
                if module.selfid.getCount() < 2:
                    module.selfid.incCount()
                    if module.selfid.getCount() == 1:
                        module.selfid.setLchild(self.conn)
                        self.conn.send("msgr:1;child:left;")
                        wnew.set(module.selfid.getIP(), module.selfid.getPort())
                        wprev.set(module.selfid.getIP(), module.selfid.getPort())
                        print "W Updated successfully As: ", wprev.getIP(), ":", wprev.getPort(), "  ", wnew.getIP(), ":", wnew.getPort()
                    elif module.selfid.getCount() == 2:
                        module.selfid.setRchild(self.conn)
                        self.conn.send("msgr:1;child:right;")
                        MESSAGE = "msgr:4;" + "child:" + module.selfid.getSelfChild() +";jumps:0;wprevIP:" + module.selfid.getIP() + ";wprevPort:" + str(module.selfid.getPort()) + ";"
                        conn = module.selfid.getLchild()
                        conn.send(MESSAGE)
                    else:
                        pass
                module.insertData(data)
            elif module.decode(data) == 5:
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
                (flag, MESSAGE) = module.queryData(d[1][1])
                # print flag, " ", MESSAGE
                # if flag == 0:
                #     #send to its parent
                #     tcpParent.send(t_data)
                # else:
                #make connection to send
                #connecting to the parent
                tcpReply = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcpReply.connect((d[2][1], int(d[3][1])))
                MESSAGE = module.getfiledest(d[1][1])
                # MESSAGE = "msg:7;"
                print 'successful'
                tcpReply.send(MESSAGE)
                tcpReply.close()
BUFFER_SIZE = 1024  # Usually 1024, but we need quick response
 
tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpServer.bind((module.selfid.getIP(), module.selfid.getPort()))
threads = []

pingt = module.PingPong()
pingt.start()

while True:
    tcpServer.listen(10)
    #print "Root : Waiting for connections from TCP clients..."
    try:
    	(conn, (ip,port)) = tcpServer.accept()
    	newthread = ClientThread(ip,port, conn)
    	newthread.start()
    	threads.append(newthread)

	#MESSAGE = "msg:4;" + "child:" + module.selfid.getSelfChild() +";jumps:1;wprevIP:" + module.selfid.getIP() + ";wprevPort:" + str(module.selfid.getPort()) + ";"					
    except Exception as e:
        print("something's wrong with %s:%d. Exception is %s" % (ip, port, e))


for t in threads:
    t.join()