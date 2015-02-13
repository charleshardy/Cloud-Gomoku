#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This program is a five in row game, which is used for the coding
camp 2015 in WindRiver.com"""

from pygame import *
import socket
import threading
import json
    
#            R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)
RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

##Define some useful colours
BLACK = (0,0,0)
#white = (255,255,255)
#blue = (0,0,255)
#red = (150,0,0)
#green = (0,150,0)
#bright_red = (255,0,0)
#bright_green = (0,255,0)
#yellow = (255,255,0)
  
BGCOLOR = NAVYBLUE

class Game(list,object):
    
    # initialize display
    init()
    display.init()

    black = image.load('Images/Black.png')
    white = image.load('Images/White.png')
    # load background image
    board = image.load('Images/Board2.png')
    
    def __init__(self):

        # 0 Init Env
        self.scr = display.set_mode((800,600))

        # start fullscreen mode
        #self.scr = display.set_mode((800, 600), FULLSCREEN)
        # turn off the mouse pointer
        #mouse.set_visible(0)

        self.board_margin_left = 18
        self.board_margin_top = 15

        self.block_width = 46
        self.block_hight = 40

        self.chess_radius = 18

        shrinkx = 800
        shrinky = 600

        # start fullscreen mode
        # turn off the mouse pointer
        #pygame.mouse.set_visible(0)

        self.init_client_conn()

        # Start a thread to read rom socket then add a event
        T = threading.Thread(target=self.read)
        T.start()

        # 1 Regist

#        # 2 Get id and role from server (client - 1 /host - 0)
#        # Reponse from server in Jason format :
        #{
#        #   "Client ID": "1",
#        #   "Command ID":  "1",
#        #   "Command":  "Show Board",
#        #   "CMD Parameters": "15x15"
#        #},


        self.clientId = "-1"
        while self.clientId == "-1":
            print ('#')
            ev = event.wait()
            print ('## ev.data %s' % str(ev))
            if ev.type == USEREVENT+1:
                #print ('## 1 ### ev.data %s' % ev.data)
                if ev.data['action'] == 'assigned':
                    #print ('type(ev.data) %s' % str(type(ev.data)))
                    self.clientId = ev.data['clientId']
                    self.clientRole = ev.data['clientRole']
                    print "clientId:", self.clientId
                    print "clientRole:", self.clientRole
                    break
                else: event.post(ev)
            elif ev.type == KEYDOWN and ev.key == K_ESCAPE or ev.type == QUIT:
                #self.game_over = True
                self.clientId = "quit"


        # 3 Show Board

        del(self[:])
        self.extend([['_']*15 for foo in range(15)])

        image = transform.smoothscale(self.board, (shrinkx, shrinky))
        self.scr.blit(image, (0,0))
        display.flip()


        #largeText = pygame.font.SysFont("comicsansms",115)
        #largeText = font.SysFont("comicsansms",115)
        #TextSurf, TextRect = text_objects("A bit Racey", largeText)
        #TextRect.center = ((1024/2),(768/2))
        #self.scr.blit(TextSurf, TextRect)
    
        #button("GO!",150,450,100,50,green,bright_green,game_loop)
        self.button("Quit",700,500,100,50,YELLOW,ORANGE,self.quitgame)
    
        display.update()

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

        # 4 Gaming (end natually/quit/replay/)
        # Get actions from server
        # Take actions when gets data from socket
        self.game_over = False
        while not self.game_over: self.gaming()

        # Show Game results
        # self.game_over = False

        # 5 Quit
        ## Tell server to quit from socket
        #try: self.conn.send('"quit"'.encode('UTF-8'))
        #except: print('pipe broken')

        data = {'clientId':'0','action':'quit'}
        try: self.conn.send(json.dumps(data))
        except: print('pipe broken')

        T.join()

        self.conn.close()

        #exit()
    
    def init_client_conn(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        soc.settimeout(5.0)
        foo = True # pour break un double-while
        while foo:
            #ip = entry('host ip   : <15,15>',width = 280)
            ip = ["127.0.0.1"]
            if not ip or not ip[0]: print('exit');exit()
            while True:
                try:
                    print('try to connect...')
                    soc.connect((ip[0],50007))
                    foo = False
                    print('connected')
                    break
                except socket.timeout:
                    print('good ip ... ?')
                    break
                except socket.error:
                    print('...refused')
                    time.wait(1000)
                    for ev in event.get():
                        if ev.type == QUIT:
                            print('exit game')
                            exit()
            self.conn = soc
        soc.settimeout(None)

    def gaming(self):

        for ev in event.get():
            #print ('### 1 ###  ev %s' % str(ev))
            if self.game_over == True:
                return

            if ev.type == KEYDOWN and ev.key == K_ESCAPE or ev.type == QUIT:
                self.game_over = True
                return
            elif ev.type == USEREVENT+1:
                #print "### ev.data", ev.data
                if ev.data['clientId'] == self.clientId and  ev.data['action'] == "put chess":
                    print "Your turn please!"
                    self.your_turn = True
                    break
                elif ev.data['action'] == "update chess":
                    print "###1  ev.data", ev.data
                    #pos = str(ev.data['pos'].split(","))
                    #print "pos:", pos
                    #pos = str(ev.data['pos'])
                    x,y = ev.data['pos']
                    print "### x, y##", x, y
                    #for x, y in pos.split(",")
                    self.put_pawn(x,y, Game.white)
                    self.your_turn = True
                    break
                else:
                    print ('Unhandled user event %s' % str(ev.data))
                    break

            elif self.your_turn == True and ev.type == MOUSEBUTTONUP and ev.button == 1:
                 print "put my chess"
                 x,y = ev.pos[0]//self.block_width,ev.pos[1]//self.block_hight
                 print "### ev.pos[0]", ev.pos[0]
                 print "### ev.pos[1]", ev.pos[1]

                 x,y = ev.pos[0]//self.block_width,ev.pos[1]//self.block_hight
                 #if (x,y) in self.playable_pos:
                 self.put_pawn(x,y, Game.black)
                 data = {'clientId':self.clientId, 'action':'put chess', 'pos':[x, y]}
                 try: self.conn.send(json.dumps(data))
                 except: print('pipe broken')
                 self.your_turn = False
            #else: print ('Unhandled event %s' % str(ev))

            time.wait(10)
            
    def put_pawn(self,x,y,color):
        #display.update(self.scr.blit(Game.black if self.your_turn else Game.white,(x*30-2,y*30-2)))
        #display.update(self.scr.blit(color,(x*self.block_width-2,y*self.block_width-2)))
        display.update(self.scr.blit(color,(x*self.block_width+self.board_margin_left - self.chess_radius, y*self.block_hight + self.board_margin_top - self.chess_radius)))

    def read(self):
        while True:
            #try: data = eval(self.conn.recv(8))
            try: data = json.loads(self.conn.recv(1024))
            except:
                print('pipe broken')
                data = 'quit'
            if data == 'quit':
                self.game_over = True
                break
            event.post(event.Event(USEREVENT+1,{'data':data}))
            print "# rec data:", data
            #self.your_turn = False
        
    def text_objects(self,text,font):
        '''Renders the font on the screen and puts it in a rectangle'''
        textSurface = font.render(text,True , BLACK)
        return textSurface, textSurface.get_rect()

    def button(self, msg,x,y,w,h,ic,ac,action=None):
        mouse_pos = mouse.get_pos()
        click = mouse.get_pressed()
        print(click)
        if x+w > mouse_pos[0] > x and y+h > mouse_pos[1] > y:
            draw.rect(self.scr, ac,(x,y,w,h))
    
            if click[0] == 1 and action != None:
                action()         
        else:
            draw.rect(self.scr, ic,(x,y,w,h))
    
        #smallText = font.SysFont("comicsansms",20)
        smallText = font.SysFont("Arial", 20)
        textSurf, textRect = self.text_objects(msg, smallText)
        textRect.center = ( (x+(w/2)), (y+(h/2)) )
        self.scr.blit(textSurf, textRect)

    def quitgame(self):
        self.game_over = True

##class Button:
##
##    __init__(self, name, position, image_file, sound_file):
##         self.name = name
##         self.image = pygame.image.load(image_file)
##         self.sound = pygame.mixer.Sound(sound_file)
##         self.position = position
##
##         self.rect = pygame.Rect(position, self.image.get_size())
##
##buttons = []
##buttons.add( Button("red", (0,0), "red.png", "red.mp3") )
##...
##
##Then you can use it in the main loop:
##
##while True:
##    for event in pygame.event.get():
##        if event.type==pygame.QUIT:
##            raise SystemExit
##        elif event.type==pygame.MOUSEBUTTONDOWN:
##            for b in buttons:
##                 if b.rect.collidepoint(event.pos):
##                      b.sound.play()
##


Game()


##if __name__ == '__main__':
##    # check input parameters
##    if len(sys.argv) < 2:
##        print ("Usage: %s ImageFile [-t] [-convert_alpha]" % sys.argv[0])
##        print ("       [-t] = Run Speed Test\n")
##        print ("       [-convert_alpha] = Use convert_alpha() on the surf.\n")
##    else:
##        main(sys.argv[1],
##             convert_alpha = '-convert_alpha' in sys.argv,
##             run_speed_test = '-t' in sys.argv)

quit()
