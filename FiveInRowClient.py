#!/usr/bin/env python

"""This program is a five in row game, which is used for the coding
camp 2015 in WindRiver.com"""

import os
import pygame as pg
import socket
import threading
import json
from toolbox import button


#                 R    G    B
GRAY          = (100, 100, 100)
WHITE         = (255, 255, 255)
RED           = (255,   0,   0)
GREEN         = (  0, 255,   0)
BLUE          = (  0,   0, 255)
YELLOW        = (255, 255,   0)
ORANGE        = (255, 128,   0)
PURPLE        = (255,   0, 255)
CYAN          = (  0, 255, 255)
BLACK         = (  0,   0,   0)
BRIGHT_GREEN  = (  0, 255,   0)
BRIGHT_RED    = (255,   0,   0)
NAVYBLUE      = ( 60,  60, 100)

SCREEN_WIDTH = 800
SCREEN_HIGHT = 600

#CHESS_BLOCK_COUNTS = 15

#class Game(list,object):
if __name__ == '__main__':
    class Game:
        def __init__(self):

            pg.init()
            pg.display.init()

            self.done = False
            self.clock = pg.time.Clock()
    
            self.black = pg.image.load('Images/Black.png')
            self.white = pg.image.load('Images/White.png')
            # load background image
            self.board = pg.image.load('Images/Board.png')
        
            # start fullscreen mode
            self.scr = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HIGHT))
            #self.scr = pg.display.set_mode((800, 600), FULLSCREEN)
    
            # turn off the mouse pointer
            #pg.mouse.set_visible(0)
    
            self.board_margin_left = 18
            self.board_margin_top = 15
    
            self.block_width = 46
            self.block_hight = 40
    
            self.chess_radius = 18
    
            self.shrinkx = SCREEN_WIDTH
            self.shrinky = SCREEN_HIGHT
    
    
            self.init_client_conn()
    
            # Start a thread to read rom socket then add a event
            self.T = threading.Thread(target=self.read)
            self.T.start()
    
            # 1 Regist
    
            # 2 Get id and role from server (clientId is 0 as the host)
            # Reponse from server in Jason format :
            #{
            #   "action"     : "assigned",
            #   "clientID"   : "0",
            #   "clientRole" :  "host",
            #}
            self.clientId = "-1"

            while self.clientId == "-1":
                ev = pg.event.wait()
                if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE or ev.type == pg.QUIT:
                    self.done = True
                    self.quit()
                elif ev.type == pg.USEREVENT+1:
                    if ev.data['action'] == 'assigned':
                        self.clientId = ev.data['clientId']
                        self.clientRole = ev.data['clientRole']
                        break
                    else: event.post(ev)
    
            # 3 Show Board
    
            #del(self[:])
            #self.extend([['_']*15 for foo in range(15)])
    
            image = pg.transform.smoothscale(self.board, (self.shrinkx, self.shrinky))
            self.scr.blit(image, (0,0))
            pg.display.flip()
    
            #largeText = pygame.font.SysFont("comicsansms",115)
            #largeText = font.SysFont("comicsansms",115)
            #TextSurf, TextRect = text_objects("A bit Racey", largeText)
            #TextRect.center = ((1024/2),(768/2))
            #self.scr.blit(TextSurf, TextRect)
        
            #self.button("Quit",SCREEN_WIDTH - self.board_margin_left * 2 - self.block_width * 15 + 10, 500,80,50,YELLOW,ORANGE,self.quitgame)
            button_config = {
                "clicked_font_color" : (0,0,0),
                "hover_font_color"   : (205,195, 0),
                'font_color'         : (255,255,255),
                'border_color'       : (0,0,0),
                'border_hover_color' : (100,100,100),
            }
    
            self.btn1 = button.Button((self.board_margin_left * 2 + self.block_width * 14 + 10, 500, 100,35), (0,0,100), 
                self.quit_click, text='QUIT', 
                clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
    
            self.buttons = [self.btn1]
    
            pg.display.update()
    
            ## Server logical
            #self.turn = 120
    
    #        grid = [[0 for x in range(10)] for y in range(10)]
    #        initial_value = 0
    #        list_length = 5
    #        [[x[1]-y[1] for y in TeamList] for x in TeamList]
    #        sample_list = [ () for i in range(10)]
    #        sample_list = [initial_value]*list_length
    #        # sample_list ==[0,0,0,0,0]
    #
    #        self.playable_pos = [(1,1), (9,9)]
    #        self.playable_pos = [(9,9)]
    
            # Let server known after chess board shown done?
            data = {'clientId':self.clientId, 'action':'show board', 'status':'done'}
            #try: self.conn.send('"show board done"'.encode('UTF-8'))
            try: self.conn.send(json.dumps(data))
            except: print('pipe broken')
            
            ### Your turn: Put down the first chess at the center of the board
            self.your_turn = True 
            #if self.clientRole == "host":
            #    event.post(event.Event(MOUSEBUTTONUP,{'button':1,'pos':(270,270)}))
    
            # 4 Gaming/run (end natually/quit/replay/)
            # Get actions from server
            # Take actions when gets data from socket

            #self.done = False
            #while not self.done: self.gaming()
    
            # Show Game results
            # self.done = False
    
            # 5 Quit
            ## Tell server to quit from socket
            #try: self.conn.send('"quit"'.encode('UTF-8'))
            #except: print('pipe broken')
    
            #data = {'clientId':'0','action':'quit'}
            #try: self.conn.send(json.dumps(data))
            #except: print('pipe broken')
    
       
            #exit()
        
        def init_client_conn(self):
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.soc.settimeout(5.0)
            foo = True # pour break un double-while
            while foo:
                #ip = entry('host ip   : <15,15>',width = 280)
                ip = ["127.0.0.1"]
                if not ip or not ip[0]: print('exit');exit()
                while True:
                    try:
                        print('try to connect...')
                        self.soc.connect((ip[0],50007))
                        foo = False
                        print('connected')
                        break
                    except socket.timeout:
                        print('good ip ... ?')
                        break
                    except socket.error:
                        print('...refused')
                        pg.time.wait(1000)
                        for ev in pg.event.get():
                            if ev.type == pg.QUIT:
                                print('exit game')
                                exit()
                self.conn = self.soc
            self.soc.settimeout(None)
    
                
        def put_pawn(self,x,y,color):
            pg.display.update(self.scr.blit(color,
                (x*self.block_width+self.board_margin_left - self.chess_radius, 
                y*self.block_hight + self.board_margin_top - self.chess_radius)))
    
        def read(self):
            #self.soc.setblocking(0)
            while not self.done:
                try: data = json.loads(self.conn.recv(1024))
                except:
                    print('pipe broken')
                    data = 'quit'
                if data == 'quit':
                    self.done = True
                    break
                pg.event.post(pg.event.Event(pg.USEREVENT+1,{'data':data}))
                print "# rec data:", data
            print "## thread exit"
            
        def quit_click(self):
            #print('Quit button pressed')
            self.done = True
            self.quit()
    
        def events(self):
            for ev in pg.event.get():

                if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE or ev.type == pg.QUIT:
                    self.done = True
                    self.quit()
                    #break

                for button in self.buttons:
                    button.check_event(ev)

                if ev.type == pg.USEREVENT+1:
                    #if ev.data['action'] == 'assigned':
                    #    self.clientId = ev.data['clientId']
                    #    self.clientRole = ev.data['clientRole']

                    if ev.data['action'] == "put chess" and ev.data['clientId'] == self.clientId:
                        print "Your turn please!"
                        self.your_turn = True

                    elif ev.data['action'] == "update chess":
                        x,y = ev.data['pos']
                        self.put_pawn(x,y, self.white)
                        self.your_turn = True

                    else:
                        print ('Unhandled other USER event %s' % str(ev.data))
    
                elif self.your_turn == True and ev.type == pg.MOUSEBUTTONUP and ev.button == 1:
                     #print "put my chess"
                     x,y = ev.pos[0]//self.block_width,ev.pos[1]//self.block_hight
                     #print "### ev.pos[0]", ev.pos[0]
                     #print "### ev.pos[1]", ev.pos[1]
    
                     x,y = ev.pos[0]//self.block_width,ev.pos[1]//self.block_hight
                     #if (x,y) in self.playable_pos:
                     if x < 15 and y < 15:
                         self.put_pawn(x,y, self.black)
                         data = {'clientId':self.clientId, 'action':'put chess', 'pos':[x, y]}
                         try: self.conn.send(json.dumps(data))
                         except: print('pipe broken')
                         self.your_turn = False
    
        def update(self):
            pass
    
        def render(self):
            #self.screen.fill((255,255,255))
            for button in self.buttons:
                button.render(self.scr)
    
        def run(self):
            while not self.done:
                self.events()
                self.update()
                self.render()
                pg.display.update()
                self.clock.tick(60)

        def quit(self):
            print "### 1"
            self.conn.close()
            print "### 2"
            self.T.join(2)
            print "### 3"
            pg.quit()
            print "### 4"
            exit()

    app = Game()
    app.run()
    app.quit()
