#!/usr/bin/env python

"""This program is a five in row game, which is used for the coding
camp 2015 in WindRiver.com"""

import os
import pygame as pg
import socket
import threading
import json
from toolbox import button
from toolbox import tools

# Cloud API
from node import Node
from config import mashery_cloud_config

#TODO
#from ..pyCloundAPILib import *
#from ..pyCloundAPILib.node import Node
#from ..pyCloundAPILib.config import mashery_cloud_config


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

GRID_LINE     = (105,  50,   6)

#CHESS_BOARD_BLOCK_COUNTS = 14
#CHESS_BOARD_BLOCK_COUNTS = 8
CHESS_BOARD_BLOCK_COUNTS = 10

#TOUCH_SCREEN = False
TOUCH_SCREEN = True

if __name__ == '__main__':

    config = {'CHESS BOARD BLOCK COUNTS': 10, 'SCREEN WIDTH': 320, 'SCREEN HIGHT': 240, 
        'USER NAME': 'You', 'FIRST START': True, 'TOUCH SCREEN': True}

    #with open('config.json', 'w') as f:
    #    json.dump(config, f)

    with open('config.json', 'r') as f:
        config = json.load(f)

    CHESS_BOARD_BLOCK_COUNTS = config['CHESS BOARD BLOCK COUNTS']
    SCREEN_WIDTH = config['SCREEN WIDTH']
    SCREEN_HIGHT = config['SCREEN HIGHT']
    TOUCH_SCREEN = config['TOUCH SCREEN']
    USER_NAME = config['USER NAME']
    FIRST_START = config['FIRST START']

    ##write it back to the file
    #with open('config.json', 'w') as f:
    #    json.dump(config, f)
    
    #exit()

    #if TOUCH_SCREEN == True:
    #    SCREEN_WIDTH = 320
    #    SCREEN_HIGHT = 240
    #else:
    #    SCREEN_WIDTH = 800
    #    SCREEN_HIGHT = 600

    class Game(tools.States):
        def __init__(self):

            pg.init()

            self.done = False

            self.scr = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HIGHT))

            # TODO: input box
            text = "Please input your name:"
            self.waiting_text, self.waiting_rect = self.make_text(text, GREEN, 
                (SCREEN_WIDTH // 2 , 
                SCREEN_HIGHT // 2), 14)

            name = ""
            font = pg.font.Font(None, 50)
            for evt in pg.event.get():
                if evt.type == pg.KEYDOWN:
                    if evt.unicode.isalpha():
                        name += evt.unicode
                    elif evt.key == pg.K_BACKSPACE:
                        name = name[:-1]
                    elif evt.key == pg.K_RETURN:
                        print "name:", name
                        break
                elif evt.type == pg.QUIT:
                    return
            self.scr.fill((0, 0, 0))
            block = font.render(name, True, (255, 255, 255))
            rect = block.get_rect()
            rect.center = self.scr.get_rect().center
            self.scr.blit(block, rect)
            pg.display.flip()


            text = "Waiting for cloud server ..."
            self.waiting_text, self.waiting_rect = self.make_text(text, GREEN, 
                (SCREEN_WIDTH // 2 , 
                SCREEN_HIGHT // 2), 14)

            self.scr.blit(self.waiting_text, self.waiting_rect)
            pg.display.update()
            
            self.init_client_conn_cloud_api()

            self.T = threading.Thread(target=self.read_from_cloud)
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
                    self.clean()
                elif ev.type == pg.USEREVENT+1:
                    if ev.data['action'] == 'assigned':
                        self.clientId = ev.data['clientId']
                        self.clientRole = ev.data['clientRole']
                        break
                    else: event.post(ev)

            print "self.clientId:", self.clientId
            print "self.clientRole:", self.clientRole


            self.clock = pg.time.Clock()
    
            # load background image
            self.board = pg.image.load('resources/images/Board.png')

            self.black = pg.image.load('resources/images/Black.png')
            self.white = pg.image.load('resources/images/White.png')
        
            # start fullscreen mode
            if TOUCH_SCREEN == True:
                #self.scr = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HIGHT), pg.FULLSCREEN)
                self.scr = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HIGHT))
            else:
                self.scr = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HIGHT))
    
            # turn off the mouse pointer
            #if TOUCH_SCREEN == True:
                ##pg.mouse.set_visible(0)
                #pg.event.set_allowed(None)
                #pg.event.set_allowed(pg.MOUSEBUTTONDOWN)
                ##pg.event.set_allowed(pg.MOUSEBUTTONDOWN)
                ##pg.event.set_allowed(pg.MOUSEBUTTONUP)
    
            if TOUCH_SCREEN == True:
                self.board_margin_left = 15
                self.board_margin_top = 15
                self.chess_radius = 10
            else:
                self.board_margin_left = 20
                self.board_margin_top = 20
                self.chess_radius = 18
    
            self.block_width = ((SCREEN_WIDTH * 833 // 1000) - self.board_margin_left * 2) // ( CHESS_BOARD_BLOCK_COUNTS + 1 )
            self.block_hight = self.block_width

            self.shrinkx = SCREEN_WIDTH
            self.shrinky = SCREEN_HIGHT
    

            self.black_image = pg.transform.smoothscale(self.black, (self.chess_radius * 2 , self.chess_radius * 2))
            self.white_image = pg.transform.smoothscale(self.white, (self.chess_radius * 2 , self.chess_radius * 2))


            tools.States.__init__(self)


            self.won_game = False
            self.screen_rect = self.scr.get_rect()
            self.overlay = pg.Surface((self.screen_rect.width, self.screen_rect.height))
            self.overlay.fill(0)
            self.overlay.set_alpha(0)

            self.X = 0
            self.Y = 0
 
            if TOUCH_SCREEN == True:
                self.last_put_X = 8
                self.last_put_Y = 8
            else:
                self.last_put_X = 16
                self.last_put_Y = 16

            self.last_put_color = self.black

    
            # 3 Show Board
            #self.board_width = 833
            #self.bg_width = 1000
            #self.block_width = (self.shrinkx * (self.board_width / self.bg_width) - self.board_margin_left * 2) / 15 - 1
            
            self.board_image = pg.transform.smoothscale(self.board, (self.shrinkx, self.shrinky))
            self.scr.blit(self.board_image, (0,0))
            if TOUCH_SCREEN == True:
                self.grid_width = 1
            else:
                self.grid_width = 2
            self.draw_grid(CHESS_BOARD_BLOCK_COUNTS)
            pg.display.flip()


            self.setup_btns()
            
            self.right_board_x = CHESS_BOARD_BLOCK_COUNTS*self.block_width+self.board_margin_left * 2
            # Guest1
            if TOUCH_SCREEN == True:
                #TODO
                # White chess
                x1 = self.right_board_x + (self.board_margin_left//2)
                pg.display.update(self.scr.blit(self.white_image,
                    (x1, 
                    1*self.block_hight + self.board_margin_top)))
    
                text = "Guest1"
                self.guest_text, self.guest_rect = self.make_text(text, YELLOW, 
                    (x1 + (self.chess_radius * 2) + self.board_margin_left + 2 , 
                    1*self.block_hight + self.board_margin_top + self.chess_radius - 1), 14)
    
                # Your chess
                pg.display.update(self.scr.blit(self.black_image,
                    (x1, 
                    5*self.block_hight + self.board_margin_top)))
    
                text = USER_NAME
                self.host_text, self.host_rect = self.make_text(text, YELLOW, 
                    (x1 + (self.chess_radius * 2) + self.board_margin_left - 2, 
                    5*self.block_hight + self.board_margin_top + self.chess_radius - 1), 14)

                self.put_pawn(0,0, self.black_image)
                self.put_pawn(1,1, self.white_image)   
            else: 
                pg.display.update(self.scr.blit(self.white,
                    (CHESS_BOARD_BLOCK_COUNTS*self.block_width+self.board_margin_left * 2 + 20, 
                    2*self.block_hight + self.board_margin_top)))
    
                text = "Guest1"
                self.guest_text, self.guest_rect = self.make_text(text, YELLOW, 
                    (CHESS_BOARD_BLOCK_COUNTS*self.block_width+self.board_margin_left * 2 + self.chess_radius * 2 + 20 + 20 + 5, 
                    2*self.block_hight + self.board_margin_top + self.chess_radius), 
                    20)
    
                # You
                pg.display.update(self.scr.blit(self.black,
                    (CHESS_BOARD_BLOCK_COUNTS*self.block_width+self.board_margin_left * 2 + 20, 
                    10*self.block_hight + self.board_margin_top)))
    
                text = "You" 
                self.host_text, self.host_rect = self.make_text(text, YELLOW, 
                    (CHESS_BOARD_BLOCK_COUNTS*self.block_width+self.board_margin_left * 2 + self.chess_radius * 2 + 20 + 20, 
                    10*self.block_hight + self.board_margin_top + self.chess_radius), 
                    20)
           
                self.put_pawn(0,0, self.black)
                self.put_pawn(1,1, self.white)   

            pg.display.update()
    
            self.grid = [[0 for x in range(CHESS_BOARD_BLOCK_COUNTS + 1)] for y in range(CHESS_BOARD_BLOCK_COUNTS + 1)]

            if TOUCH_SCREEN == True:
                pass
            else:
                pass
                # Let server known after chess board shown done?
#                data = {'clientId':self.clientId, 'action':'show board', 'status':'done'}
#                try: self.conn.send(json.dumps(data))
#                except: print('pipe broken')
            
            ### Your turn: Put down the first chess at the center of the board
            self.your_turn = True 
    
            # 4 Gaming/run (end natually/quit/replay/)
            # Get actions from server
            # Take actions when gets data from socket

            #self.done = False
            #while not self.done: self.gaming()
    
            # Show Game results
            # self.done = False
    
        def draw_grid(self, n):
            for i in range(0, n + 1):
                # Rows
                x1 = self.board_margin_left
                y1 = self.board_margin_top + i * self.block_width
                x2 = self.board_margin_left + n * self.block_width
                y2 = self.board_margin_top + i * self.block_width
                pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)

                # Columns
                x1 = self.board_margin_left + i * self.block_width
                y1 = self.board_margin_top
                x2 = self.board_margin_left + i * self.block_width
                y2 = self.board_margin_top + n * self.block_width
                pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)

        def patch_grid(self, n, x, y):
            self.patch_grid_x0_xn(n, x, y)
            self.patch_grid_y0_yn(n, x, y)
            self.patch_grid_inner(n, x, y)

        def patch_grid_x0_xn(self, n, x, y):
            if x == 0:
                x1 = self.board_margin_left
                if y == 0:
                    y1 = self.board_margin_top

                    # Rows
                    x2 = self.board_margin_left + self.chess_radius
                    y2 = self.board_margin_top
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    x2 = self.board_margin_left
                    y2 = self.board_margin_top + self.chess_radius
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
                elif y == n:
                    # Rows
                    y1 = self.board_margin_top + (y * self.block_width)
                    x2 = self.board_margin_left + self.chess_radius
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    y1 = self.board_margin_top + (y * self.block_width - self.chess_radius)
                    x2 = self.board_margin_left
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)

                else:
                    # Rows
                    y1 = self.board_margin_top + (y * self.block_width)
                    x2 = self.board_margin_left + self.chess_radius
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    y1 = self.board_margin_top + (y * self.block_width - self.chess_radius)
                    x2 = self.board_margin_left
                    y2 = self.board_margin_top + (y * self.block_width + self.chess_radius)
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
            elif x == n:
                x1 = self.board_margin_left + (x * self.block_width)
                if y == 0:

                    # Rows
                    x2 = self.board_margin_left + (x * self.block_width) - self.chess_radius
                    y2 = self.board_margin_top
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    x2 = self.board_margin_left + (x * self.block_width)
                    y2 = self.board_margin_top + self.chess_radius
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
                elif y == n:
                    # Rows
                    y1 = self.board_margin_top + (y * self.block_width)
                    x2 = self.board_margin_left + (x * self.block_width) - self.chess_radius
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    y1 = self.board_margin_top + (y * self.block_width - self.chess_radius)
                    x2 = self.board_margin_left + (x * self.block_width)
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)

                else:
                    # Rows
                    y1 = self.board_margin_top + (y * self.block_width)
                    x2 = self.board_margin_left + (x * self.block_width) - self.chess_radius
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    y1 = self.board_margin_top + (y * self.block_width - self.chess_radius)
                    x2 = self.board_margin_left + (x * self.block_width)
                    y2 = self.board_margin_top + (y * self.block_width + self.chess_radius)
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)

        def patch_grid_y0_yn(self, n, x, y):
            if y == 0:
                if not x == 0 and not x == n:
                    y1 = self.board_margin_top
                    x1 = self.board_margin_left + (x * self.block_width) - self.chess_radius
    
                    # Rows
                    x2 = self.board_margin_left + (x * self.block_width) + self.chess_radius
                    y2 = self.board_margin_top
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
       
                    # Columns
                    x1 = self.board_margin_left + (x * self.block_width)
                    x2 = self.board_margin_left + (x * self.block_width)
                    y2 = self.board_margin_top + self.chess_radius
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
            elif y == n:
                if not x == 0 and not x == n:
                    y1 = self.board_margin_top + (y * self.block_width)
                    x1 = self.board_margin_left + (x * self.block_width) - self.chess_radius
    
                    # Rows
                    x2 = self.board_margin_left + (x * self.block_width) + self.chess_radius
                    y2 = y1
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
       
                    # Columns
                    x1 = self.board_margin_left + (x * self.block_width)
                    x2 = x1
                    y2 = y1 - self.chess_radius
                    pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)

        def patch_grid_inner(self, n, x, y):
            if x > 0 and x < n and y > 0 and y < n:
                # Rows
                x1 = self.board_margin_left + (x * self.block_width) - self.chess_radius
                y1 = self.board_margin_top + (y * self.block_width)
                
                x2 = self.board_margin_left + (x * self.block_width) + self.chess_radius
                y2 = y1
    
                pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)
                
                # Columns
                x1 = self.board_margin_left + (x * self.block_width)
                x2 = x1
                
                y1 = self.board_margin_top + (y * self.block_width) - self.chess_radius
                y2 = self.board_margin_top + (y * self.block_width) + self.chess_radius
                pg.draw.line(self.scr, GRID_LINE, (x1,y1), (x2,y2), self.grid_width)

        def init_client_conn_cloud_api(self):
            self.data_name = "vlv_benchmark"
            self.node = Node(mashery_cloud_config)
            self.data_id = self.node.dataId(self.data_name)
            print "self.data_id:", self.data_id

        def init_client_conn_socket(self):
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
    
        def set_last_chess_prompt(self, x, y):
            if TOUCH_SCREEN == True:
                pass
            else:
                pass
                # left top
                # -
                pg.display.update(self.scr.fill(pg.Color('red'),
                    (x*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                    y*self.block_hight + self.board_margin_top - self.chess_radius - 1,8,2)))
    
                # |
                pg.display.update(self.scr.fill(pg.Color('red'),
                    (x*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                    y*self.block_hight + self.board_margin_top - self.chess_radius - 1,2,8)))
    
                # right down
                pg.display.update(self.scr.fill(pg.Color('red'),
                    (x*self.block_width + self.board_margin_left + self.chess_radius + 1 - 2, 
                    y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 8,2,8)))
    
                # -
                pg.display.update(self.scr.fill(pg.Color('red'),
                    (x*self.block_width + self.board_margin_left + self.chess_radius + 1 - 8, 
                    y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 2,8,2)))
                # ----------------------------------------------------
                # left down 
                # -
                pg.display.update(self.scr.fill(pg.Color('red'),
                    (x*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                    y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 2, 8,2)))
                # |
                pg.display.update(self.scr.fill(pg.Color('red'),
                    (x*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                    y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 8, 2,8)))
    
                # right top
                # -
                pg.display.update(self.scr.fill(pg.Color('red'),
                    (x*self.block_width + self.board_margin_left + self.chess_radius + 1 - 8, 
                    y*self.block_hight + self.board_margin_top - self.chess_radius - 1,8,2)))
                # |
                pg.display.update(self.scr.fill(pg.Color('red'),
                    (x*self.block_width + self.board_margin_left + self.chess_radius + 1 - 2, 
                    y*self.block_hight + self.board_margin_top - self.chess_radius - 1,2,8)))
    
                if self.last_put_X < CHESS_BOARD_BLOCK_COUNTS + 1 and self.last_put_Y < CHESS_BOARD_BLOCK_COUNTS + 1:
                    # left top
                    r1 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                            self.last_put_Y*self.block_hight + self.board_margin_top - self.chess_radius - 1,8,2)
                    self.scr.blit(self.board_image,r1,r1)
    
                    r2 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                            self.last_put_Y*self.block_hight + self.board_margin_top - self.chess_radius - 1,2,8)
                    self.scr.blit(self.board_image,r2,r2)
    
                    # right top
                    r3 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left + self.chess_radius + 1 - 2, 
                            self.last_put_Y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 8,2,8)
                    self.scr.blit(self.board_image,r3,r3)
    
                    r4 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left + self.chess_radius + 1 - 8, 
                            self.last_put_Y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 2,8,2)
                    self.scr.blit(self.board_image,r4,r4)
    
                    # ----------------------------------------------           
                    # left down
                    r5 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                            self.last_put_Y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 2,8,2)
                    self.scr.blit(self.board_image,r5,r5)
    
                    r6 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                            self.last_put_Y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 8 ,2,8)
                    self.scr.blit(self.board_image,r6,r6)
    
                    # right down
                    r7 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left + self.chess_radius + 1 - 8, 
                            self.last_put_Y*self.block_hight + self.board_margin_top - self.chess_radius - 1 ,8,2)
                    self.scr.blit(self.board_image,r7,r7)
    
                    r8 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left + self.chess_radius + 1 - 2, 
                            self.last_put_Y*self.block_hight + self.board_margin_top - self.chess_radius - 1 ,2,8)
                    self.scr.blit(self.board_image,r8,r8)
                 
        def put_pawn(self,x,y,color):
            print ("### put chess (x: %s, y: %s)" % (x,y))
            print ("### x pos : %s" % str(x*self.block_width + self.board_margin_left))
            print ("### x pos : %s" % str(x*self.block_width + self.board_margin_left - self.chess_radius))
            pg.display.update(self.scr.blit(color,
                (x*self.block_width + self.board_margin_left - self.chess_radius, 
                y*self.block_hight + self.board_margin_top - self.chess_radius)))

            self.set_last_chess_prompt(x,y)

            self.last_put_X = x
            self.last_put_Y = y
            self.last_put_color = color

        def setup_btns(self):
            button_config = {
                "clicked_font_color" : (0,0,0),
                "hover_font_color"   : (205,195, 0),
                'font_color'         : (255,255,255),
                'font'               : tools.Font.load('impact.ttf', 18),
                'border_color'       : (0,0,0),
                'border_hover_color' : (100,100,100),
            }

#            button_config = {
#                "clicked_font_color" : (0,0,0),
#                "hover_font_color"   : (205,195, 0),
#                'font'               : tools.Font.load('impact.ttf', 18),
#                'font_color'         : (255,255,255),
#                'border_color'       : (0,0,0),
#            }
    
            if TOUCH_SCREEN == True:
                self.right_board_x = CHESS_BOARD_BLOCK_COUNTS*self.block_width+self.board_margin_left * 2
                self.btn1 = button.Button((self.right_board_x + 5, 190, 70,30), (0,0,100), 
                    self.quit_click, text='QUIT', 
                    clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
    
#                self.btn2 = button.Button((self.board_margin_left * 2 + self.block_width * 14 + 10, 200, 50,35), (0,0,100), 
#                    self.test_click, text='TEST', 
#                    clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
            else:
                self.btn1 = button.Button((self.board_margin_left * 2 + self.block_width * CHESS_BOARD_BLOCK_COUNTS + 10, 500, 100,35), (0,0,100), 
                    self.quit_click, text='QUIT', 
                    clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
    
                self.btn2 = button.Button((self.board_margin_left * 2 + self.block_width * CHESS_BOARD_BLOCK_COUNTS + 10, 10, 100,35), (0,0,100), 
                    self.test_click, text='TEST', 
                    clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
    
            if TOUCH_SCREEN == True:
                self.buttons = [self.btn1]
            else:
                self.buttons = [self.btn1, self.btn2]

        def read_from_cloud(self):
            while not self.done:
                try: data = json.loads(self.node.getData(self.data_id))
                except:
                    print("Fail to get data %s" % self.data_name)
                    #break
                try: pg.event.post(pg.event.Event(pg.USEREVENT+1,{'data':data}))
                except:
                    print("Fail to post event ")
                    break
            print "## read_from_cloud thread exit"

        def read_from_socket(self):
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
            self.done = True
            #if TOUCH_SCREEN == True:
            #    self.clean()
            

        def show_how_won(self, (x1, y1), (x2, y2)):
            x1_pos = x1*self.block_width + self.board_margin_left
            y1_pos = y1*self.block_hight + self.board_margin_top 
            x2_pos = x2*self.block_width + self.board_margin_left
            y2_pos = y2*self.block_hight + self.board_margin_top 
            r = pg.draw.line(self.scr, RED, (x1_pos,y1_pos), (x2_pos,y2_pos), 2)
            pg.display.update(r)

        def test_click(self):
            self.won_game = True
            start_pos = (2,2)
            end_pos = (6,6)
            self.show_how_won(start_pos, end_pos)

            print('TEST button pressed')

        def easefocus(self,x,y):
            r = pg.Rect(x*self.block_width + self.board_margin_left - self.chess_radius, y*self.block_hight + self.board_margin_top - self.chess_radius,self.chess_radius * 2,self.chess_radius * 2)
            self.scr.blit(self.board_image,r,r)
            self.patch_grid(CHESS_BOARD_BLOCK_COUNTS, x, y)
            # Rows
            return r

        def events(self):
            for ev in pg.event.get():

                if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE or ev.type == pg.QUIT:
                    self.done = True
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
                        if TOUCH_SCREEN == True:
                            self.put_pawn(x,y, self.white_image)
                        else:
                            self.put_pawn(x,y, self.white)
                        #self.put_pawn(x,y, 'white')
                        self.grid[x][y] = 2 # 2: white
                        self.your_turn = True

                    else:
                        print ('Unhandled other USER event %s' % str(ev.data))
    
                elif self.your_turn == True and ev.type == pg.MOUSEBUTTONUP and ev.button == 1:
                #elif self.your_turn == True and ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                #elif self.your_turn == True and ev.type == pg.MOUSEBUTTONDOWN:
                #elif ev.type == pg.MOUSEBUTTONDOWN:
                     #print "#### MOUSEBUTTONDOWN ####"
                     x,y = ev.pos[0]//self.block_width,ev.pos[1]//self.block_hight
                     if x < CHESS_BOARD_BLOCK_COUNTS + 1 and y < CHESS_BOARD_BLOCK_COUNTS + 1:
                         if self.grid[x][y] == 0:
                             if TOUCH_SCREEN == True:
                                 self.put_pawn(x,y, self.black_image)
                             else:
                                 self.put_pawn(x,y, self.black)
                             # TODO     
## Server

#                                 self.grid[x][y] = 1 # 1: black
#                                 print "### 1 ### grid[x][y]", str(self.grid[x][y])
#                                 data = {'clientId':self.clientId, 'action':'put chess', 'pos':[x, y]}
#                                 try: self.conn.send(json.dumps(data))
#                                 except: print('pipe broken')
#                                 self.your_turn = False

### Server
                #elif self.your_turn == True and ev.type == pg.MOUSEMOTION:
                elif ev.type == pg.MOUSEMOTION:
                     if TOUCH_SCREEN == False:
                         x,y = ev.pos[0]//self.block_width,ev.pos[1]//self.block_hight
                         if x < CHESS_BOARD_BLOCK_COUNTS + 1 and y < CHESS_BOARD_BLOCK_COUNTS + 1 and not self.won_game:
                             if self.grid[self.X][self.Y] == 0:
                                 r = self.easefocus(self.X,self.Y)
                             if self.grid[x][y] == 0:
                                 pg.display.update(self.scr.blit(self.black, 
                                     (x*self.block_width+self.board_margin_left - self.chess_radius, 
                                     y*self.block_hight + self.board_margin_top - self.chess_radius)))
    
                                 self.X = x
                                 self.Y = y

                else:
                    print "#### ev.type:", str(ev.type)

        #def won_game(self):
        #    return True
     
        def update_label(self):
    
            #self.sec_timelapse, self.sec_timelapse_rect = self.make_text('Sec: {}'.format(self.timelapse), (0,0,0), (60, 150), 20)
    
            ##best = DB.load()['save']['shortest']
            #if not self.best:
            #    best = None
            #else:
            #    best = self.best
            #self.shortest_time_text, self.shortest_time_rect = self.make_text('Best: {}'.format(best), (0,0,0), (60, 175), 20)
            pass
    

        def update(self):
            msg = 'Game Over'
            if self.won_game:
                msg = 'You Won'
            self.game_over, self.game_over_rect = self.make_text(msg, RED, self.screen_rect.center, 50)
    
            #self.games_won_text, self.games_won_rect = self.make_text('Won: {}'.format(self.games_won), (0,0,0), (60, 200), 20)
            #self.games_lost_text, self.games_lost_rect = self.make_text('Lost: {}'.format(self.games_lost), (0,0,0), (60, 225), 20)
            #self.points_text, self.points_rect = self.make_text('Points:', (0,0,0), (60, 250), 20)
            #self.points_num_text, self.points_num_rect = self.make_text('{}'.format(self.points), (0,0,0), (60, 275), 20)
            #pass
    
        def render(self):
            #self.screen.fill((255,255,255))

            for button in self.buttons:
                button.render(self.scr)

            self.scr.blit(self.host_text, self.host_rect)
            self.scr.blit(self.guest_text, self.guest_rect)

            #self.scr.blit(self.games_won_text, self.games_won_rect)
            #self.scr.blit(self.games_lost_text, self.games_lost_rect)
            #self.scr.blit(self.sec_timelapse, self.sec_timelapse_rect)

            #if self.lost_game or self.won_game():
            if self.won_game:
                self.scr.blit(self.overlay, (0,0))
                self.scr.blit(self.game_over, self.game_over_rect)

            #self.scr.blit(self.chess_cursor, self.chess_cursor_rect)
            #pg.draw.rect(self.scr, (255, 255, 255, 127), pg.Rect(0, 0, 100, 75))

            #self.scr.blit(self.sec_timelapse, self.sec_timelapse_rect)
            #pg.draw.rect(self.scr, (255, 255, 255, 127), pg.Rect(0, 0, 100, 75))
            #pg.draw.rect(self.scr, (255, 255, 255, 127), pg.Rect(0, 0, 100, 75))
    
        def run(self):
            while not self.done:
                self.events()
                self.update()
                self.render()
                pg.display.update()
                self.clock.tick(60)

        def clean(self):
            print "### 1"
            #if TOUCH_SCREEN == True:
            #    pass
            #else:
                #pass
                #self.conn.close()
            print "### 2"
            self.T.join(1)
            print "### 3"
            pg.quit()
            print "### 4"
            exit()
            #sys.exit(0)

    app = Game()
    app.run()
    app.clean()
