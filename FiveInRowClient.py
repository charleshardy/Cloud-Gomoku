#!/usr/bin/env python

"""This program is a five in row game, which is used for the coding
camp 2015 in WindRiver.com"""

import os
import sys, getopt
import pygame as pg
import threading
import json
from toolbox import button
from toolbox import tools

# Cloud API
from node import Node
from config import *

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

DRAW = 0
CONTINUE = 1
WIN = 2
ERROR = 3

cloud_service = "Mashery"

def usage():

    USAGE = """\

Usage: %s <-i config_file> [options]

  -i, --ifile=     Input the config file, which contains player user name, 
                   screen width and hight, and input method, etc. 
Options:
  -h, --help       Show this message
  -g, --gameid=    Enter into watching mode and watch the game of [gameid]
                   
Examples:
  %s -i config.json_pc 
  %s -i config.json_touch
  %s -i config.json_watch -g 1
"""
    print (USAGE % ((os.path.basename(__file__),) * 4))


if __name__ == "__main__":

    inputfile = ''
    watch_mode = 0
    watch_game = -1
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:g:",["help","ifile=", "gameid="])
    except getopt.GetoptError as err:
        print str(err) 
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--ifile="):
            inputfile = arg
        elif opt in ("-g", "--gameid="):
            watch_mode = 1
            try:
                watch_game = int(arg)
            except:
                print "Find latest game to watch", arg

    if inputfile == '':
        usage()
        sys.exit(2)
    else:
        if not os.path.isfile(inputfile):
            print "The file of input doesn't exit"
            sys.exit(2)

    #config = {'CHESS BOARD BLOCK COUNTS': 10, 'SCREEN WIDTH': 320, 'SCREEN HIGHT': 240, 
    #    'USER NAME': 'Charles', 'TOUCH SCREEN': True, 
    #    'CLOUD_SERVICE': 'Mashery', 
    #    'BOARD MARGIN LEFT': 15, 'BOARD MARGIN TOP': 15, 'CHESS RADIUS': 10,
    #    'CLIENT ROLE': 1  # (BLACK) First Start
    #    }

    #with open('config.json', 'w') as f:
    #    json.dump(config, f)
    #exit()

    #with open('config.json', 'r') as f:
    with open(inputfile, 'r') as f:
        config = json.load(f)
    print "config:", config

    CHESS_BOARD_BLOCK_COUNTS = config['CHESS BOARD BLOCK COUNTS']
    SCREEN_WIDTH = config['SCREEN WIDTH']
    SCREEN_HIGHT = config['SCREEN HIGHT']
    TOUCH_SCREEN = config['TOUCH SCREEN']
    BOARD_MARGIN_LEFT = config['BOARD MARGIN LEFT']
    BOARD_MARGIN_TOP = config['BOARD MARGIN TOP']
    CHESS_RADIUS = config['CHESS RADIUS']
         
    USER_NAME = config['USER NAME']
    SHOW_MOUSEMOTION = False
    KEYBOARD_INPUT = config['KEYBOARD INPUT']
    USER_NAME_TEXT_COLOR = config['USER NAME TEXT COLOR']
    BOARD_GRID_LINE_COLOR = config['BOARD GRID LINE COLOR']

    class Game(tools.States):
        def __init__(self):

            #if TOUCH_SCREEN == True:
                #os.putenv('SDL_MOUSEDEV' , '/dev/input/event2')
            
            pg.init()

            if TOUCH_SCREEN == True:
                pg.mouse.set_visible(0)

            self.done = False

            self.scr = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HIGHT))

            # Guest1
            if TOUCH_SCREEN == True:
                waiting_font_size = 12
            else: 
                waiting_font_size = 20
            text = "Waiting for cloud server ..."
            self.waiting_text, self.waiting_rect = self.make_text(text, GREEN, 
                (SCREEN_WIDTH // 2 , 
                SCREEN_HIGHT // 2), waiting_font_size)

            self.scr.blit(self.waiting_text, self.waiting_rect)
            pg.display.update()
            

            # 1 Regist and start game get game ID, client role
            self.debug = True
            #self.role_id = '0' # Host as default
            self.seq_id = 0

            self.init_for_cloud()
            
            if watch_mode >0:
            	self.role_id = "2"
            	if watch_game >= 0:
            	    self.game_id = str(watch_game)
            	else:
            	    #find lastest game
            	    self.game_id = str(self.findlatest_game())
            else:
                r = self.client_register()
                if not r:
                    print("fails to first player register")
                else:
                    r = json.loads(r)
                    #print "### r", r
                    #print("First player register: role id %s, game id %s" % (r["roleId"], r["gameId"]))
                    self.game_id = r["gameId"]
                    self.role_id = r["roleId"]

            self.clock = pg.time.Clock()
    
            # load background image
            self.board = pg.image.load('resources/images/Board.png')
            self.black = pg.image.load('resources/images/Black.png')
            self.white = pg.image.load('resources/images/White.png')
        
            self.scr = pg.display.set_mode((SCREEN_WIDTH,SCREEN_HIGHT))
    
            self.board_margin_left = BOARD_MARGIN_LEFT
            self.board_margin_top = BOARD_MARGIN_TOP
            self.chess_radius = CHESS_RADIUS
    
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

            # TODO (enabling quit in thread)
            # Get player 2 user name (blocking)
            self.competitor_name = self.get_competitor_name(self.game_id,self.role_id)

            self.draw_user_info()

            
            # Init chess focus
            self.cur_x = CHESS_BOARD_BLOCK_COUNTS // 2
            self.cur_y = self.cur_x
            if self.role_id == '0':
                self.set_last_chess_prompt(self.cur_x,self.cur_y)
                self.last_put_X = CHESS_BOARD_BLOCK_COUNTS + 10 #not exits
                self.last_put_Y = CHESS_BOARD_BLOCK_COUNTS + 10

            pg.display.update()
    
            self.grid = [[0 for x in range(CHESS_BOARD_BLOCK_COUNTS + 1)] for y in range(CHESS_BOARD_BLOCK_COUNTS + 1)]

            ### Your turn: Put down the first chess at the center of the board
            if self.role_id == '0':
                self.your_turn = True 
            else:
                self.your_turn = False
            # WATCHING MODE
            self.fetch_data = True
            if self.role_id == "2":
                self.get_history_from_cloud()
            if self.fetch_data == True:
                self.T = threading.Thread(target=self.read_from_cloud)
                self.T.start()
    
        def draw_user_info(self):
        
            # Guest1
            if TOUCH_SCREEN == True:
                name_font_size = 12
            else: 
                name_font_size = 20

            # Competitor chess
            x1 = self.right_board_x + (SCREEN_WIDTH - self.right_board_x)/2 - self.chess_radius

            pg.display.update(self.scr.blit(self.black_image if self.role_id == '1' else self.white_image,
                (x1, 
                1*self.block_hight + self.board_margin_top)))

            x1 = self.right_board_x + (SCREEN_WIDTH - self.right_board_x)/2
            text = self.competitor_name
            self.guest_text, self.guest_rect = self.make_text(text, USER_NAME_TEXT_COLOR, 
                (x1,
                1*self.block_hight + self.board_margin_top - self.chess_radius), name_font_size)

            # Your chess
            x1 = self.right_board_x + (SCREEN_WIDTH - self.right_board_x)/2 - self.chess_radius
            pg.display.update(self.scr.blit(self.white_image if self.role_id == '1' else self.black_image,
                (x1, 
                5*self.block_hight + self.board_margin_top)))

            text = self.user_name
            x1 = self.right_board_x + (SCREEN_WIDTH - self.right_board_x)/2
            self.host_text, self.host_rect = self.make_text(text, USER_NAME_TEXT_COLOR, 
                (x1,
                5*self.block_hight + self.board_margin_top - self.chess_radius), name_font_size)

        def set_dataitem(self,node, data_name, data_val):
            data_id = node.dataId(data_name)
    
            if self.debug:
                    print("setting data item %s = %s" % (data_id, str(data_val)))
    
            if not node.setData(data_id, json.dumps(data_val)):
                    print("Fail to set data item %s = %s" % (data_id, data_val))
                    return False
    
            return True
    
        def get_dataitem(self, node, data_id):
            val = node.getData(data_id)
            if not val:
                    print("Fail to query data item %s" % data_id)
                    return None
    
            if self.debug:
                    print("fetch data item %s = %s" % (data_id, str(val)))
    
            return val
    
        def __update_role_id(self):
            r = self.role_id
            self.role_id += 1
            self.role_id &= 1
            if self.debug:
                    print("assign new role id %d" % r)
            return r

        def init_for_cloud(self):
            self.node = Node(cloud_service, cloud_configs[cloud_service])

        def client_register(self):

            scripto = self.node.cloud.scripto()

            registration = json.dumps({
                "playerName": USER_NAME,
            })
            data = {
            "registration": registration
            }
            
            r = scripto.execute('vlvRegistration', data)
            return r


        def draw_grid(self, n):
            for i in range(0, n + 1):
                # Rows
                x1 = self.board_margin_left
                y1 = self.board_margin_top + i * self.block_width
                x2 = self.board_margin_left + n * self.block_width
                y2 = self.board_margin_top + i * self.block_width
                pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)

                # Columns
                x1 = self.board_margin_left + i * self.block_width
                y1 = self.board_margin_top
                x2 = self.board_margin_left + i * self.block_width
                y2 = self.board_margin_top + n * self.block_width
                pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
            
            # Reference points
            if TOUCH_SCREEN == True:
                radius = 3
            else: 
                radius = 6

            ## left top
            x1 = self.board_margin_left + 2 * self.block_width
            y1 = self.board_margin_top + 2 * self.block_width
            pg.draw.circle(self.scr, BOARD_GRID_LINE_COLOR, (x1, y1), radius, 0)

            ## right top 
            x1 = self.board_margin_left + (n - 2) * self.block_width
            y1 = self.board_margin_top + 2 * self.block_width
            pg.draw.circle(self.scr, BOARD_GRID_LINE_COLOR, (x1, y1), radius, 0)

            ## left bottom
            x1 = self.board_margin_left + 2 * self.block_width
            y1 = self.board_margin_top + (n - 2) * self.block_width
            pg.draw.circle(self.scr, BOARD_GRID_LINE_COLOR, (x1, y1), radius, 0)

            ## right bottom
            x1 = self.board_margin_left + (n - 2) * self.block_width
            y1 = self.board_margin_top + (n - 2) * self.block_width
            pg.draw.circle(self.scr, BOARD_GRID_LINE_COLOR, (x1, y1), radius, 0)

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
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    x2 = self.board_margin_left
                    y2 = self.board_margin_top + self.chess_radius
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
                elif y == n:
                    # Rows
                    y1 = self.board_margin_top + (y * self.block_width)
                    x2 = self.board_margin_left + self.chess_radius
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    y1 = self.board_margin_top + (y * self.block_width - self.chess_radius)
                    x2 = self.board_margin_left
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)

                else:
                    # Rows
                    y1 = self.board_margin_top + (y * self.block_width)
                    x2 = self.board_margin_left + self.chess_radius
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    y1 = self.board_margin_top + (y * self.block_width - self.chess_radius)
                    x2 = self.board_margin_left
                    y2 = self.board_margin_top + (y * self.block_width + self.chess_radius)
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
            elif x == n:
                x1 = self.board_margin_left + (x * self.block_width)
                if y == 0:

                    # Rows
                    x2 = self.board_margin_left + (x * self.block_width) - self.chess_radius
                    y2 = self.board_margin_top
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    x2 = self.board_margin_left + (x * self.block_width)
                    y2 = self.board_margin_top + self.chess_radius
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
                elif y == n:
                    # Rows
                    y1 = self.board_margin_top + (y * self.block_width)
                    x2 = self.board_margin_left + (x * self.block_width) - self.chess_radius
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    y1 = self.board_margin_top + (y * self.block_width - self.chess_radius)
                    x2 = self.board_margin_left + (x * self.block_width)
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)

                else:
                    # Rows
                    y1 = self.board_margin_top + (y * self.block_width)
                    x2 = self.board_margin_left + (x * self.block_width) - self.chess_radius
                    y2 = self.board_margin_top + (y * self.block_width)
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
    
                    # Columns
                    y1 = self.board_margin_top + (y * self.block_width - self.chess_radius)
                    x2 = self.board_margin_left + (x * self.block_width)
                    y2 = self.board_margin_top + (y * self.block_width + self.chess_radius)
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)

        def patch_grid_y0_yn(self, n, x, y):
            if y == 0:
                if not x == 0 and not x == n:
                    y1 = self.board_margin_top
                    x1 = self.board_margin_left + (x * self.block_width) - self.chess_radius
    
                    # Rows
                    x2 = self.board_margin_left + (x * self.block_width) + self.chess_radius
                    y2 = self.board_margin_top
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
       
                    # Columns
                    x1 = self.board_margin_left + (x * self.block_width)
                    x2 = self.board_margin_left + (x * self.block_width)
                    y2 = self.board_margin_top + self.chess_radius
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
            elif y == n:
                if not x == 0 and not x == n:
                    y1 = self.board_margin_top + (y * self.block_width)
                    x1 = self.board_margin_left + (x * self.block_width) - self.chess_radius
    
                    # Rows
                    x2 = self.board_margin_left + (x * self.block_width) + self.chess_radius
                    y2 = y1
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
       
                    # Columns
                    x1 = self.board_margin_left + (x * self.block_width)
                    x2 = x1
                    y2 = y1 - self.chess_radius
                    pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)

        def patch_grid_inner(self, n, x, y):
            if x > 0 and x < n and y > 0 and y < n:
                # Rows
                x1 = self.board_margin_left + (x * self.block_width) - self.chess_radius
                y1 = self.board_margin_top + (y * self.block_width)
                
                x2 = self.board_margin_left + (x * self.block_width) + self.chess_radius
                y2 = y1
    
                pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)
                
                # Columns
                x1 = self.board_margin_left + (x * self.block_width)
                x2 = x1
                
                y1 = self.board_margin_top + (y * self.block_width) - self.chess_radius
                y2 = self.board_margin_top + (y * self.block_width) + self.chess_radius
                pg.draw.line(self.scr, BOARD_GRID_LINE_COLOR, (x1,y1), (x2,y2), self.grid_width)

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

            print "set_last_chess_prompt (", "x:", x, "y:", y, ")"
            if x <= CHESS_BOARD_BLOCK_COUNTS  and y <= CHESS_BOARD_BLOCK_COUNTS and x >= 0 and y >= 0:
                
                self.cur_x = x
                self.cur_y = y

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
    
                self.clear_last_chess_prompt()

        def clear_last_chess_prompt(self):
            print "clear_last_chess_prompt (", "x:", self.last_put_X, "y:", self.last_put_Y, ")"
            # Clean chess focus
            if self.last_put_X <= CHESS_BOARD_BLOCK_COUNTS and self.last_put_Y <= CHESS_BOARD_BLOCK_COUNTS and self.last_put_X >= 0 and self.last_put_Y >= 0:
                # left top
                r1 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                        self.last_put_Y*self.block_hight + self.board_margin_top - self.chess_radius - 1,8,2)
                self.scr.blit(self.board_image,r1,r1)
                pg.display.update(r1)

                r2 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                        self.last_put_Y*self.block_hight + self.board_margin_top - self.chess_radius - 1,2,8)
                self.scr.blit(self.board_image,r2,r2)
                pg.display.update(r2)

                # right top
                r3 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left + self.chess_radius + 1 - 2, 
                        self.last_put_Y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 8,2,8)
                self.scr.blit(self.board_image,r3,r3)
                pg.display.update(r3)

                r4 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left + self.chess_radius + 1 - 8, 
                        self.last_put_Y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 2,8,2)
                self.scr.blit(self.board_image,r4,r4)
                pg.display.update(r4)

                # ----------------------------------------------           
                # left down
                r5 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                        self.last_put_Y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 2,8,2)
                self.scr.blit(self.board_image,r5,r5)
                pg.display.update(r5)

                r6 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left - self.chess_radius - 1, 
                        self.last_put_Y*self.block_hight + self.board_margin_top + self.chess_radius + 1 - 8 ,2,8)
                self.scr.blit(self.board_image,r6,r6)
                pg.display.update(r6)

                # right down
                r7 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left + self.chess_radius + 1 - 8, 
                        self.last_put_Y*self.block_hight + self.board_margin_top - self.chess_radius - 1 ,8,2)
                self.scr.blit(self.board_image,r7,r7)
                pg.display.update(r7)

                r8 = pg.Rect(self.last_put_X*self.block_width + self.board_margin_left + self.chess_radius + 1 - 2, 
                        self.last_put_Y*self.block_hight + self.board_margin_top - self.chess_radius - 1 ,2,8)
                self.scr.blit(self.board_image,r8,r8)
                pg.display.update(r8)
                 
        def put_pawn(self,x,y,color):
            print ("### put chess (x: %s, y: %s)" % (x,y))
            pg.display.update(self.scr.blit(color,
                (x*self.block_width + self.board_margin_left - self.chess_radius, 
                y*self.block_hight + self.board_margin_top - self.chess_radius)))

            self.set_last_chess_prompt(x,y)

            self.last_put_X = x
            self.last_put_Y = y

        def setup_btns(self):
            
            if TOUCH_SCREEN == True:
                button_font_size = 18
            else: 
                button_font_size = 22

            button_config = {
                "clicked_font_color" : (0,0,0),
                "hover_font_color"   : (205,195, 0),
                'font_color'         : (255,255,255),
                'font'               : tools.Font.load('impact.ttf', button_font_size),
                'border_color'       : (0,0,0),
                'border_hover_color' : (100,100,100),
            }

            self.right_board_x = CHESS_BOARD_BLOCK_COUNTS*self.block_width+self.board_margin_left * 2
            button_hight = self.board_margin_top * 2
            button_width = SCREEN_WIDTH - self.right_board_x - self.board_margin_left * 2
            self.btn1 = button.Button((self.right_board_x + self.board_margin_left, 
                                          SCREEN_HIGHT - self.board_margin_left - button_hight, 
                                          button_width,button_hight), (0,0,100), 
            self.quit_click, text='QUIT', 
            clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
    
#                self.btn2 = button.Button((self.board_margin_left * 2 + self.block_width * 14 + 10, 200, 50,35), (0,0,100), 
#                    self.test_click, text='TEST', 
#                    clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
                #self.btn1 = button.Button((self.board_margin_left * 2 + self.block_width * CHESS_BOARD_BLOCK_COUNTS + 10, 500, 100,35), (0,0,100), 
                #    self.quit_click, text='QUIT', 
                #    clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
    
            #    self.btn2 = button.Button((self.board_margin_left * 2 + self.block_width * CHESS_BOARD_BLOCK_COUNTS + 10, 10, 100,35), (0,0,100), 
            #        self.test_click, text='TEST', 
            #        clicked_color=(255,255,255), hover_color=(0,0,130), **button_config)
    
            self.buttons = [self.btn1]
            #self.buttons = [self.btn1, self.btn2]

        def get_competitor_name(self, game_id, role_id):

            data_id = self.node.dataId("vlv_GMETA_" + game_id)

            while not self.done:
                gmeta = self.get_dataitem(self.node, data_id)
                competitor_name = '' 
                if gmeta:
                    data = json.loads(gmeta)
                    print "### data : ", data
                    if role_id == '0':
                        competitor_name = data['player2']
                        self.user_name = USER_NAME
                    elif role_id == '1':
                        competitor_name = data['player1']
                        self.user_name = USER_NAME
                    elif role_id == '2':
                        self.user_name = data['player1']
                        competitor_name = data['player2']
                    if not competitor_name == '':
                        print "### competitor_name", competitor_name
                        return competitor_name

        def read_from_cloud(self):

            data_name = "vlv_GMOVE_" + str(self.game_id)
            data_id = self.node.dataId(data_name)
            old_data = ''
            while not self.done:
                try: 
                    data = json.loads(self.node.getData(data_id))
                    if not data['Status'] == 0 and data['Status'] and data != old_data:
                        old_data = data
                        try: pg.event.post(pg.event.Event(pg.USEREVENT+1,{'data':data}))
                        except:
                            print("Fail to post event ")
                            break
                except:
                    print("Fail to get data %s" % data_name)
            print "## read_from_cloud thread exit"
        def findlatest_game(self):
            data_name = "vlv_game_id"
            data_id = self.node.dataId(data_name)
            vlv_GAME_S_ID = self.node.getData(data_id)
            vlv_GAME_ID = int(vlv_GAME_S_ID)
            return vlv_GAME_ID - 1
        def get_history_from_cloud(self):
            self.his_data = []
            data_name = "vlv_GMOVE_" + str(self.game_id)
            data_id = self.node.dataId(data_name)
            datas = self.node.getHistoricalData(data_id, pageSize=1000)
            if len(datas) == 0:
                print "No game data"
                self.fetch_data = False
                self.done = True
                return
            j = 0
            for i in range(2, len(datas)):
                print("Raw move ", datas[i]);
                try:data = json.loads(datas[i])
                except:
                    continue
                if data['Status'] > 0 and data['Status']:
                    print("Got " ,data['SeqID'],"move", datas[i]);
                    j = data['SeqID']
                    self.his_data.insert(j - 1,data)
            #Only last entry to judge if game is over
            if j == 0:
            #    print "No game data"
                self.fetch_data = True
            #    self.done = True
                return
            if self.his_data[j-1]['Status'] == 2:
                self.fetch_data = False
                #print("Got End @ %s", str(data['SeqID']))
            self.his_data_len=j;
            #debug
            #self.fetch_data = False
            #Draw current status
            print("his data total %d,move"%self.his_data_len)
            if self.fetch_data == True:
                for i in range(0, self.his_data_len):
                    print('his data %s'%str(self.his_data[i]))
                    pg.event.post(pg.event.Event(pg.USEREVENT+1,{'data':self.his_data[i]}))
                    self.events()
            else:
                pg.event.post(pg.event.Event(pg.USEREVENT+1,{'data':self.his_data[0]}))
                self.his_data_move = 1
                self.events()
        def history_next_move(self):
            print("history_next_move %d" %self.his_data_move)
            if self.his_data_move < self.his_data_len:
                pg.event.post(pg.event.Event(pg.USEREVENT+1,{'data':self.his_data[self.his_data_move]}))
                self.events()
                self.his_data_move = self.his_data_move + 1
            else:
                print("Max move")
        def quit_click(self):
            self.done = True
            

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
                     #print "# new user event!"
                     #print "---------------ev.data[seqid]=" + str(ev.data['SeqID'])
                     print "---------------ev.data" + str(ev.data)
                     self.turn = ev.data['SeqID'] % 2
                     self.pawn = self.turn^1
                     result = ev.data['Status']

                     if result == WIN:
                         start_pos, end_pos = ev.data['WinSpawns']
                         #print "## start_pos:", start_pos
                         #print "## end_pos:", end_pos
                         self.show_how_won(start_pos, end_pos)
                         self.won_game = True

                     if int(self.role_id) == self.pawn:
                      
                         if result == CONTINUE:
                             pass    
                         else:
                          # TODO
                          # generated error
                          # To be done
                              pass
                     else: #peer draw
                         X = ev.data['PosX']
                         Y = ev.data['PosY']
                         self.seq_id = ev.data['SeqID']
                         self.put_pawn(X, Y, self.black_image if self.seq_id % 2 == 1 else self.white_image)
                         if not self.role_id == "2":
                             self.your_turn = True                    
                         self.grid[X][Y] = 2 if self.role_id == "1" else 1
                         #print "### 1 ### grid[X][Y]", str(self.grid[X][Y])
#                    else:
#                        print ('Unhandled other USER event %s' % str(ev.data))
                elif self.fetch_data == False and ev.type == pg.MOUSEBUTTONUP  and ev.button == 1:
                    self.history_next_move()
                elif self.fetch_data == True and self.your_turn == True and ev.type == pg.MOUSEBUTTONUP and ev.button == 1 and not self.won_game == True:
                     x,y = ev.pos[0]//self.block_width,ev.pos[1]//self.block_hight
                     self.put_my_chess(x, y)

                #elif ev.type == pg.KEYDOWN:
                elif self.fetch_data == False and ev.type == pg.KEYDOWN and KEYBOARD_INPUT == True:
                    self.history_next_move()
                elif self.fetch_data == True and ev.type == pg.KEYDOWN and KEYBOARD_INPUT == True:
                     print "### print key press"
                     if ev.key == pg.K_SPACE:
                         print "### print space"
                         if self.your_turn == True and not self.won_game == True:
                             print "### Pressed space key ###", self.cur_x, self.cur_y 
                             self.put_my_chess(self.cur_x, self.cur_y)
                     elif ev.key == pg.K_DOWN:
                         print "### print down"
                         if self.your_turn == True and not self.won_game == True:
                             if self.cur_x <= CHESS_BOARD_BLOCK_COUNTS  and self.cur_y + 1 <= CHESS_BOARD_BLOCK_COUNTS and self.cur_x >= 0 and self.cur_y >= 0:
                                 self.last_put_X = self.cur_x
                                 self.last_put_Y = self.cur_y
                                 self.cur_y += 1
                                 self.set_last_chess_prompt(self.cur_x,self.cur_y)
                     elif ev.key == pg.K_UP:
                         print "### print up"
                         if self.your_turn == True and not self.won_game == True:
                             if self.cur_x <= CHESS_BOARD_BLOCK_COUNTS  and self.cur_y <= CHESS_BOARD_BLOCK_COUNTS and self.cur_x >= 0 and self.cur_y - 1 >= 0:
                                 self.last_put_X = self.cur_x
                                 self.last_put_Y = self.cur_y
                                 self.cur_y -= 1
                                 self.set_last_chess_prompt(self.cur_x,self.cur_y)
                     elif ev.key == pg.K_RIGHT:
                         print "### print right"
                         if self.your_turn == True and not self.won_game == True:
                             if self.cur_x + 1 <= CHESS_BOARD_BLOCK_COUNTS  and self.cur_y <= CHESS_BOARD_BLOCK_COUNTS and self.cur_x >= 0 and self.cur_y >= 0:
                                 self.last_put_X = self.cur_x
                                 self.last_put_Y = self.cur_y
                                 self.cur_x += 1
                                 self.set_last_chess_prompt(self.cur_x,self.cur_y)
                     elif ev.key == pg.K_LEFT:
                         print "### print left"
                         if self.your_turn == True and not self.won_game == True:
                             if self.cur_x <= CHESS_BOARD_BLOCK_COUNTS  and self.cur_y <= CHESS_BOARD_BLOCK_COUNTS and self.cur_x - 1 >= 0 and self.cur_y >= 0:
                                 self.last_put_X = self.cur_x
                                 self.last_put_Y = self.cur_y
                                 self.cur_x -= 1
                                 self.set_last_chess_prompt(self.cur_x,self.cur_y)

                elif self.your_turn == True and ev.type == pg.MOUSEMOTION:
                     # TODO
                     #if TOUCH_SCREEN == False and self.your_turn == True:
                     if SHOW_MOUSEMOTION == True:
                         x,y = ev.pos[0]//self.block_width,ev.pos[1]//self.block_hight
                         if x < CHESS_BOARD_BLOCK_COUNTS + 1 and y < CHESS_BOARD_BLOCK_COUNTS + 1 and not self.won_game:
                             if self.grid[self.X][self.Y] == 0:
                                 r = self.easefocus(self.X,self.Y)
                             if self.grid[x][y] == 0:
                                 pg.display.update(self.scr.blit(self.white_image if self.role_id == "1" else self.black_image,
                                     (x*self.block_width+self.board_margin_left - self.chess_radius, 
                                     y*self.block_hight + self.board_margin_top - self.chess_radius)))
    
                                 self.X = x
                                 self.Y = y
                #else:
                #    print "#### ev.type:", str(ev.type)

        def put_my_chess(self, x, y):
            if x < CHESS_BOARD_BLOCK_COUNTS + 1 and y < CHESS_BOARD_BLOCK_COUNTS + 1:
                if self.grid[x][y] == 0:
                    self.put_pawn(x,y, self.white_image if self.role_id == "1" else self.black_image)
                    self.put_chess_to_cloud((x,y))
                    self.your_turn = False
                    self.grid[x][y] = 1 if self.role_id == "1" else 2

        def put_chess_to_cloud(self, (x,y)):
            data_name="vlv_GMOVE_" + str(self.game_id)
            data_id = self.node.dataId(data_name)
            self.seq_id += 1
            data_val = {'SeqID': self.seq_id, 'PosX': x, 'PosY': y, 'Status': DRAW}
            if not self.node.setData(data_id, json.dumps(data_val)):
                print("Fail to set data %s = %s" % (data_name, data_val))
            else:
                print("Data set chess pos (x:%s, y%s) to cloud" % (str(x), str(y))),

        def update(self):
            msg = 'Game Over'
            if self.won_game:
                x = self.right_board_x // 2
                y = SCREEN_HIGHT // 2

                if TOUCH_SCREEN == True:
                    msg_font_size = 50
                else:
                    msg_font_size = 120

                if self.role_id == "2":
                    msg = 'Got Winner!'
                    self.game_over, self.game_over_rect = self.make_text(msg, RED, (x,y), msg_font_size)
                elif int(self.role_id) == self.pawn:
                    msg = 'You Won!'
                    self.game_over, self.game_over_rect = self.make_text(msg, RED, (x,y), msg_font_size)
                else:
                    msg = 'You Lost!'
                    self.game_over, self.game_over_rect = self.make_text(msg, BLUE, (x,y), msg_font_size)

    
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
                #self.clock.tick(60)

        def clean(self):
            if self.fetch_data == True:
                self.T.join(1)
            pg.quit()
            exit()

    app = Game()
    app.run()
    app.clean()
