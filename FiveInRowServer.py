#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This program is a five in row game, which is used for the coding
camp 2015 in WindRiver.com"""

from pygame import *
time.Clock()
import socket
import threading
import json

    
class Game(list,object):
    
    def __init__(self):

        init()

        # Waiting for connection
        self.init_server_conn()

        T = threading.Thread(target=self.read)
        T.start()

        self.game_over = False

        # Connected and send user id and role
        playerorder = 0
        #self.conn.send(str(playerorder).encode('UTF-8'))

        data = {'action':'assigned', 'clientRole':'host', 'clientId':'0'}
        #data = {'role':'host', 'id':'0'}
        try: self.conn.send(json.dumps(data))
        except: print('pipe broken')

        #del(self[:])
        #self.extend([['_']*15 for foo in range(15)])

        # turn from 120 decreasing
        #self.turn = 120
        #self.playable_pos = [(9,9)]

        #while True:

        self.cli2_turn = False
        self.x = 1
        self.y = 1
        self.chess_count = 5

        #self.addchess_tmp = False
        self.client1_turn = False
        while not self.game_over: 
            #print "### 1 "
            for ev in event.get():
                #print ('### 1 ###  ev %s' % str(ev))
                #print ('type(ev.data) %s' % str(type(ev.data)))
                if ev.type == QUIT:
                    self.game_over = True
                    return
                elif ev.type == USEREVENT+1:
                    #print "### ev.data", ev.data
                    if ev.data['action'] == "show board":
                        print "Server: %s show board is %s" % (ev.data['clientId'], ev.data['status'])
                        #if ev.data['status'] == "done" and ev.data['clientRole'] == "host":
                        #    data = {'clientId':'0','action':'put chess', 'pos':'x,y'}
                        #    try: self.conn.send(json.dumps(data))
                        #    except: print('pipe broken')
                        #else: send wait
                    elif ev.data['action'] == "put chess":
                        print "Server: client %s put chess at:%s" % (ev.data['clientId'] , str(ev.data['pos']))
                        #print "Server: client %s put chess at:%s" % (ev.data['clientId'] , ev.data['pos'])
                        if ev.data['clientId'] == "0":
                           self.client1_turn = True
                        else:
                           self.client1_turn = False

#                        break
#                    else:
#                        print ('Unhandled user event %s' % str(ev.data))
#                        break
#                else: print ('Unhandled event %s' % str(ev))

            #if self.game_over == True: break;

            self.ai_action()

            time.wait(10)

##        sboard1 = True
##    
##        print "### 1"
##        while sboard1:
##            ev = event.wait()
##            if ev.type == USEREVENT+1:
##                print "### 3"
##                sboard1 = False
##                break

##        while not self.game_over: self.update()

#                # Game over results : win, tied, and no place to put chess pieces
#                if self.winnerspawns:
#                    self.show_winnerspawns()
#                elif not self.turn:
#                    display.update(self.scr.fill((255,128,128),(14,14,541,541),BLEND_RGB_ADD))
#                    print('tie game')
#                elif not self.playable_pos:
#                    display.update(self.scr.fill((255,128,128),(14,14,541,541),BLEND_RGB_ADD))
#                    print('game stuck')
#                else: replay = False
#
#                self.game_over = False
#                if replay:
#                    while not self.game_over:
#                        ev = event.wait()
#                        if ev.type == KEYDOWN: break
#                        else: event.post(ev)
#                    self.scr.fill(0)
#                    display.flip()
#                    replay = slidemenu(['Replay','Quit'],pos='center',color1=(100,100,100),color2=(200,200,200))[1]^1
        #else: exit()
        #try: self.conn.send('"quit"'.encode('UTF-8'))
        data = {'action':'quit'}
        try: self.conn.send(json.dumps(data))
        except: print('pipe broken')
        T.join()
        self.conn.close()
    
    def init_server_conn(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.settimeout(5.0)

        soc.bind(('',50007))
        soc.listen(1)
        ### attend un client temps que l'on ne quitte pas
        while True:
            try:
                print('awaiting for player connection')
                self.conn = soc.accept()[0]
                break
            except:
                for ev in event.get():
                    if ev.type == QUIT: exit()
        soc.settimeout(None)

    def ai_action(self):
        if self.chess_count > 0 and self.client1_turn == True:
            self.x += 1
            self.y += 1
            data = {'clientId':'1','action':'update chess', 'pos':[self.x,self.y]}
            try: self.conn.send(json.dumps(data))
            except: 
                print('pipe broken')
                return
            self.client1_turn = False
            self.chess_count -= 1
            print "### self.chess_count:", str(self.chess_count)

#    def ai_action(self):
#
#        if self.addchess_tmp == False:
#            print "### update chess to client "
#            self.x = self.x+1;
#            self.y = self.y+1;
#            data = {'clientId':'1','action':'update chess', 'pos':(self.x,self.y)}
#            try: self.conn.send(json.dumps(data))
#            except: print('pipe broken')
#            self.addchess_tmp = True 
#            return
#        else: 
#            data = {'clientId':'0','action':'put chess'}
#            try: self.conn.send(json.dumps(data))
#            except: print('pipe broken')
#            self.addchess_tmp = False
#            return
#        # two people one by one in turn
#        if self.cli2_turn == True:
#            print "### 3"
#            if self.x > 15: 
#                self.game_over = True
#                return  
#            print "send x, y: ", self.x, self.y 
#            #self.conn.send(str((self.x,self.y)).encode('UTF-8'))
#            data = {'clientId':'1','action':'update chess', 'pos':'x,y'}
#            try: self.conn.send(json.dumps(data))
#            except: print('pipe broken')
#       
#            self.x = self.x + 1
#            self.y = self.y + 1
#
#            self.cli2_turn = False
#
#        else:
#            print "### 4"
#            time.wait(1)
#            self.cli2_turn = True
            
    def is_winner(self):
        # ToDo
        return False
    
    def read(self):
        while True:
            #try: data = eval(self.conn.recv(20))
            try: data = json.loads(self.conn.recv(1024))
            except:
                print('pipe broken')
                data = 'quit'
            if data == 'quit':
                self.game_over = True
                break
            event.post(event.Event(USEREVENT+1,{'data':data}))
            print('# Recieve data : ', data)
        

Game()
quit()
