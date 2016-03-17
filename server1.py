import socket 
import os 
import time
import sys
import multiprocessing
import subprocess
import hashlib
import re
import magic

self_ip = ''
self_port = ''
client_ip = ''
client_port = ''
share_dir = ''
own_dir = ''

def server_func(server_socket):
    m = magic.open(magic.MAGIC_MIME)
    m.load()
    print "server started"    
    server_socket.listen(5)
    while True:
        
        c,addr = server_socket.accept()
        command = c.recv(1024)
        command_list = command.split(' ')
        if command_list[0] == 'IndexGet' :
            file_list = os.listdir(share_dir)
            output = []
            if  command_list[1] == 'longlist':
                for i in range(len(file_list)):    
                    if os.path.isfile(share_dir+'/'+str(file_list[i])):
                        info = os.stat(share_dir+'/' + file_list[i])
                        output.append(str(file_list[i])+' ')
                        output.append(str(info.st_size)+' ')
                        output.append(str(time.ctime(info.st_mtime)))
                        output.append(str(m.file(share_dir+'/'+str(file_list[i]))))
                        output.append(str('\n'))

                send_str=''
                for i in range(len(output)):
                    send_str+=str(output[i])
                c.send(send_str)

            elif command_list[1] == 'shortlist':
                t1 = str(command_list[2]+' '+command_list[3])
                t2 = str(command_list[4]+' '+command_list[5])
                timestamp1 = time.mktime(time.strptime(t1, '%d/%m/%Y %H:%M:%S'))
                timestamp2 = time.mktime(time.strptime(t2, '%d/%m/%Y %H:%M:%S'))
                file_list = os.listdir(share_dir)
                output = [] 
                for i in range(len(file_list)):    
                        info = os.stat(share_dir+'/' + file_list[i])
                        if os.path.isfile(share_dir+'/'+str(file_list[i])) and info.st_mtime>timestamp1 and info.st_mtime<timestamp2:
                            output.append(str(file_list[i])+' ')
                            output.append(str(info.st_size)+' ')
                            output.append(str(time.ctime(info.st_mtime)))
                            output.append(str(m.file(share_dir+'/'+str(file_list[i]))))
                            output.append(str('\n'))

                send_str=''
                for i in range(len(output)):
                    send_str+=str(output[i])
                c.send(send_str)
                continue
            

            elif command_list[1]=='regex':
                pattern = re.compile(str(command_list[2]))
                
                file_list = os.listdir(share_dir)
                output = [] 
                for i in range(len(file_list)):    
                        info = os.stat(share_dir+'/' + file_list[i])
                        if os.path.isfile(share_dir+'/'+str(file_list[i])) and pattern.match(str(file_list[i])):
                            output.append(str(file_list[i])+' ')
                            output.append(str(info.st_size)+' ')
                            output.append(str(time.ctime(info.st_mtime)))
                            output.append(str(m.file(share_dir+'/'+str(file_list[i]))))
                            output.append(str('\n'))

                send_str=''
                for i in range(len(output)):
                    send_str+=str(output[i])
                c.send(send_str)
                continue

        elif command_list[0] == 'FileHash':
            if command_list[1] == 'verify' :
                if os.path.isfile(share_dir + '/'+ str(command_list[2])) == False :
                    c.send("No such file exists")
                
                else :
                    output = []
                    info = os.stat(share_dir+'/' + str(command_list[2]))
                    output.append(str(command_list[2])+' ')
                    output.append(hashlib.md5(open(share_dir+'/' + str(command_list[2]) , 'rb').read()).hexdigest())
                    output.append(str(time.ctime(info.st_mtime)))
                    output.append(str('\n'))

                send_str=''
                for i in range(len(output)):
                    send_str+=str(output[i])
                c.send(send_str)

            elif command_list[1] == 'checkall' :
                file_list = os.listdir(share_dir)
                output = []
                for i in range(len(file_list)):    
                    if os.path.isfile(share_dir+'/'+str(file_list[i])):
                        info = os.stat(share_dir+'/' + file_list[i])
                        output.append(str(file_list[i])+' ')
                        output.append(hashlib.md5(open(share_dir+'/' + str(file_list[i]) , 'rb').read()).hexdigest())
                        output.append(str(time.ctime(info.st_mtime)))
                        output.append(str('\n'))

                send_str=''
                for i in range(len(output)):
                    send_str+=str(output[i])
                c.send(send_str)

        elif command_list[0] == 'FileDownload' :
            if os.path.isfile(share_dir + '/' + command_list[1]) == False :
                c.send("Not")
                continue;
            else :
                c.send(str(os.path.getsize(share_dir + '/' + command_list[1])))
                response = c.recv(1024)
                if response[0]=='Y':
                    f = open(share_dir + '/' + command_list[1],'r')
                    while True :
                        fc = str(f.read(1024))
                        if fc == "":
                            c.send(fc)
                            break
                        else :
                            c.send(fc)
                    file_hash = str(hashlib.md5(open(share_dir + '/' + command_list[1], 'rb').read()).hexdigest())
                    c.send(file_hash) 
                    output = []
                    info = os.stat(share_dir+'/' + command_list[1])
                    output.append(str(command_list[1])+' ')
                    output.append(hashlib.md5(open(share_dir+'/' + str(command_list[1]) , 'rb').read()).hexdigest())
                    output.append(str(time.ctime(info.st_mtime)))
                    output.append(str('\n'))
                    send_str=''
                    for i in range(len(output)):
                        send_str+=str(output[i])
                    c.send(send_str)

                elif response[0]=='N':
                    continue
        else :
            c.send("invalid")
            
if __name__ == '__main__':


    print "Enter your server ip you want to set ",
    while self_ip == '':
        self_ip = raw_input()
        try :
            socket.inet_aton(self_ip)
        except socket.error:
            print "Incorrect Format .Enter in correct ipv4 format : %s ",
            self_ip = ''


    server_socket = socket.socket()
    print "Enter your server port you want to set (from 1 to 65535 )",
    self_port = raw_input()
    while int(self_port)<1 or int(self_port)>65535:
        print "port not in valid range enter again ",
        self_port = raw_input()
    try:
        port_result = server_socket.bind((self_ip,int(self_port)))
    except :
        print "Make sure that you have permissions to use the port"
        print "Couldn't bind . Try again later"
        sys.exit()

    print 

    print "enter the directory you want to share ",
    share_dir = raw_input()
    while os.path.isdir(share_dir)==False:
        print "path entered is not a directory, please enter full path ",
        share_dir = raw_input()

    print "enter the directory where files will be downloaded ",
    own_dir = raw_input()
    while os.path.isdir(own_dir)==False:
        print "path entered is not a directory, please enter full path ",
        own_dir = raw_input()


    print "Enter your server ip you want to connect to ",
    while client_ip == '':
        client_ip = raw_input()
        try :
            socket.inet_aton(self_ip)
        except socket.error:
            print "Incorrect Format .Enter in correct ipv4 format : %s ",
            client_ip = ''

    print "Enter the server port you want to connect to (from 1 to 65535 )",
    client_port = raw_input()
    while int(client_port)<1 or int(client_port)>65535:
        print "port not in valid range enter again ",
        client_port = raw_input()
    '''self_ip = '127.0.0.1'
    self_port = 5000
    client_ip = '127.0.0.2'
    client_port = 5000
    share_dir = '/home/raj'
    own_dir = '/home/raj/Downloads'
    '''


    server_socket = socket.socket()
    port_result = server_socket.bind((self_ip,int(self_port)))
    p = multiprocessing.Process (target=server_func, args = (server_socket,) )
    p.start()

    while True :
        s = socket.socket()
        try:
            print "Enter command ",
            temp1 = raw_input().split()
            s.connect((client_ip, int(client_port)))
            send_str =''
            if  temp1[0]!='FileDownload' and temp1[0]!='IndexGet' and temp1[0]!='FileHash' :
                print "Invalid command"
                continue
            for i in range(len(temp1)):
                send_str+=str(temp1[i])+' '
            s.send(send_str)
            if temp1[0] == 'FileDownload' and temp1[1]=='UDP' :
                ud = socket.socket()

            if temp1[0] == 'FileDownload' :
                out = s.recv(1024)
                out_list = out.split('\n')
                if out_list[0]=="NOT":
                    print "No such file exists"
                    continue

                else :
                    print "The size of "+ temp1[1] + " is " + out_list[0] + " Download ? (Y/N) ",
                    resp = raw_input().split()
                    s.send(str(resp[0]))
                    if resp[0]=='Y' :
                        f = open(own_dir+'/'+str(temp1[1])+'_new','w')
                        downl = 0
                        while downl < int(out_list[0]) :
                            chunk = s.recv(1024)
                            downl+=int(len(chunk))
                            if chunk == "":
                                break
                            else :
                                f.write(chunk)
                        f.close()
                        hash_f = s.recv(1024)
                        hash_f_final = str(hashlib.md5(open(own_dir+'/'+str(temp1[1])+'_new', 'rb').read()).hexdigest())
                        if hash_f == hash_f_final:
                            print "MD5 hash verified "
                        else :
                            os.system('rm -rf '+ own_dir+'/'+str(temp1[1])+'_new' )
                            print "MD5 hash didn't match . Please try again "
                        out = s.recv(1024)
                        out_list = out.split('\n')
                        for i in range(len(out_list)):
                            print out_list[i]

                    elif resp[0] == 'N':
                        continue;

            else :
                out = s.recv(1024)
                out_list = out.split('\n')
                for i in range(len(out_list)):
                    print out_list[i]
        except socket.error:
            print "Caught exception socket.error, coudln't connect to target server "
            print "next attemp in 5 seconds"
            time.sleep(5)

