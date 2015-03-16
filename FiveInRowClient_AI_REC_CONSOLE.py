#!/usr/bin/env python

"""This program is a five in row game, which is used for the coding
camp 2015 in WindRiver.com"""

import os
import sys, getopt
import threading
from AI import searcher
import time
from REC import chess_board_recognition
import copy

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

CHESS_BOARD_BLOCK_COUNTS=10
if __name__ == "__main__":

    class Game():
        def __init__(self):

            self.done = False

            self.debug = True

            self.seq_id = 0

            # AI mode
            self.game_id = '0001'
            self.role_id = '0' # You're first starter (black chess)

            self.won_game = False

            self.X = 0
            self.Y = 0
 
            self.competitor_name = "PC AI"
            self.user_name = "Charles"

            self.grid = [[0 for x in range(CHESS_BOARD_BLOCK_COUNTS + 1)] for y in range(CHESS_BOARD_BLOCK_COUNTS + 1)]
            self.grid_ai = [[0 for x in range(CHESS_BOARD_BLOCK_COUNTS + 1)] for y in range(CHESS_BOARD_BLOCK_COUNTS + 1)]

            ### Your turn: Put down the first chess at the center of the board
            if self.role_id == '0':
                self.your_turn = True 
            else:
                self.your_turn = False

            # Recognizing Mode
            self.rec_data = True
            if self.rec_data == True:
                #self.T_CAMERA_REC = threading.Thread(target = chess_board_recognition.main, args = (0, chess_board_recognition.DEBUG_DETECT_OBJECT, 100))
                self.T_CAMERA_REC = threading.Thread(target = chess_board_recognition.main, args = (0, 0, 0))
                self.T_CAMERA_REC.start()
             
        def quit_click(self):
            self.done = True
            
        def show_how_won(self, (x1, y1), (x2, y2)):
            x1_pos = x1*self.block_width + self.board_margin_left
            y1_pos = y1*self.block_hight + self.board_margin_top 
            x2_pos = x2*self.block_width + self.board_margin_left
            y2_pos = y2*self.block_hight + self.board_margin_top 
            print "How won : from ", (x1, y1), "to ", (x2, y2)

        def test_click(self):
            self.won_game = True
            start_pos = (2,2)
            end_pos = (6,6)
            self.show_how_won(start_pos, end_pos)

        # The player, who first starts the game, will put black color chess
        # self.role_id = "0" is the first starter, the second player's role id is "1"
        # self.grid notes
        # init values <==> "_"
        # black color <==> "0"
        # white color <==> "1"
        def put_human_chess(self, x, y, who_put):
            if x < CHESS_BOARD_BLOCK_COUNTS + 1 and y < CHESS_BOARD_BLOCK_COUNTS + 1:
                if self.grid[x][y] == 0:
                    self.grid[x][y] = who_put # 1
                    self.your_turn = False

        def show_real_chess(self):
            #print "   ###################### who_put: ", str(who_put)
            print "   ######## REAL ########"
            print "   0 1 2 3 4 5 6 7 8 9 10"
            print "   ######################"
            for iy in range(0, CHESS_BOARD_BLOCK_COUNTS + 1):
                print '{:2}#'.format(str(iy)),
                for ix in range(0, CHESS_BOARD_BLOCK_COUNTS + 1):
                    print '{:1}'.format(str(self.grid[ix][iy])),
                print
            print "   ######################"

        def show_ai_chess(self):
            #print "   ###################### who_put: ", str(who_put)
            print "   ========= AI ========="
            print "   0 1 2 3 4 5 6 7 8 9 10"
            print "   ======================"
            for iy in range(0, CHESS_BOARD_BLOCK_COUNTS + 1):
                print '{:2}:'.format(str(iy)),
                for ix in range(0, CHESS_BOARD_BLOCK_COUNTS + 1):
                    print '{:1}'.format(str(self.grid_ai[ix][iy])),
                print
            print "   ======================"

        def is_game_over(self, x, y, who_put):
            #self.show_real_chess()

            return self.is_winner(x,y, who_put)

        def is_winner(self,X,Y,who_put):
            winnerspawns = []
            pawn = who_put 
            
            # vertical
            row1 = []
            for i in xrange(CHESS_BOARD_BLOCK_COUNTS + 1):
                row1.extend([((X,i),self.grid[X][i])])
            #print "----------row1="+str(row1)

            # horizon
            row2 = []
            for i in xrange(CHESS_BOARD_BLOCK_COUNTS + 1):
                row2.extend([((i,Y),self.grid[i][Y])])
            #print "----------row2="+str(row2)

            # left slash 
            row3 = []
            if X < Y: x, y = Y - X, 0
            else: x, y = 0, X - Y
            k = 0
            while k < CHESS_BOARD_BLOCK_COUNTS + 1:
                if x + k > CHESS_BOARD_BLOCK_COUNTS or y + k > CHESS_BOARD_BLOCK_COUNTS:
                    break
                row3.extend([((y + k,x + k),self.grid[y + k][x + k])])
                k += 1
            #print "----------row3="+str(row3)

            # right slash
            row4 = []
            if CHESS_BOARD_BLOCK_COUNTS - X < Y: 
                x, y = Y - CHESS_BOARD_BLOCK_COUNTS + X, CHESS_BOARD_BLOCK_COUNTS
            else: x, y = 0, X + Y
            k = 0
            while k < CHESS_BOARD_BLOCK_COUNTS + 1:
                if x + k > CHESS_BOARD_BLOCK_COUNTS or y - k < 0:
                    break
                row4.extend([((y - k,x + k), self.grid[y - k][x + k])])
                k += 1
            #print "----------row4="+str(row4)

            for row in (row1,row2,row3,row4):
                spawns=''
                coords,pawns = zip(*row)
                #print "pawns: ", pawns
                for i in pawns:
                    spawns+=''.join(str(i))
                #print "###### spawns:", spawns
                #print "-------coords="+str(coords)
                #print "-------pawns="+str(pawns)
                index1 = spawns.find(str(pawn)*5)
                if index1 == -1: continue
                winnerspawns.extend((coords[index1:index1+1]))
                winnerspawns.extend((coords[index1+4:index1+5]))
            if winnerspawns:
                self.pawn = who_put - 1
                #print "----------------winnerspawns="+str(winnerspawns)
                start_pos, end_pos = winnerspawns
                #self.show_how_won(start_pos, end_pos)
                self.won_game = True
                return True # WIN/LOST
            else:
                return False #CONTINUE
              
        def put_AI_chess(self,last_x, last_y, who_put):
            x,y = self.AI_put(last_x, last_y, who_put)
            if x < CHESS_BOARD_BLOCK_COUNTS + 1 and y < CHESS_BOARD_BLOCK_COUNTS + 1:
                if self.grid[x][y] == 0:
                    self.grid_ai = copy.deepcopy(self.grid)
                    self.grid_ai[x][y] = 8 # 2
                    self.your_turn = True
                    self.show_ai_chess()
            return x,y
         
        def AI_put(self, last_x, last_y, who_put):
            DEPTH=1
            s = searcher.searcher()
            s.board = self.grid
            print 'Intel Galileo is thinking now...'
            #score, row, col = s.search(2, DEPTH)
            score, row, col = s.search(who_put, DEPTH)
            print 'Intel Galileo moves to (%d,%d) (score:%d)'%(row, col, score)
            return (row,col)

    
        def run(self):
            old_data = ''
            while not self.done and not self.won_game:
                #try: 
                time.sleep(1)
                data = chess_board_recognition.get_put_chess()
                #if data == None: continue
                #print "data:", data
                #print "len(data):", len(data)
                #print "cmp(data,old_data):", cmp(data,old_data)
                if len(data) == 3 and data[0] >=0 and data[1] >=0 and data[2] >=0 and data[2] <= 1 and not cmp(data,old_data) == 0:
                    old_data = data
                    #print "# old_data", old_data
                    #print "# data", data
                    #print "# cmp(data,old_data):", cmp(data,old_data)
                    x = data[0]
                    #print "x:", x
                    y = data[1]
                    #print "y:", y
                    color = data[2]
                    #print "color:", color
                    if x < CHESS_BOARD_BLOCK_COUNTS + 1 and y < CHESS_BOARD_BLOCK_COUNTS + 1 and x >= 0 and y >= 0:
                        if color == 0: # black - Human / white - AI
                            self.put_human_chess(x, y, 1) # self.role_id:0/put chess value is 1/black
                            self.show_real_chess()
                            if not self.is_game_over(x,y,1): 
                                x1,y1 = self.put_AI_chess(x,y,2)
                                self.is_game_over(x1,y1,2)
                        elif color == 1: # white - real put 
                            #if self.grid[x][y] == 0:
                            #    print "Why didn't you put the chess as I suggested?"
                            self.put_human_chess(x, y, 2) # self.role_id:0/put chess value is 1/black
                            self.show_real_chess()
                            self.is_game_over(x,y,2) 
                            #Waiting for next put from the camera
                #except:
                #    print("Fail to get data %s" % data)
            print "## gave over and exit"


        def clean(self):
            if self.rec_data == True:
                self.T_CAMERA_REC.join(1)
            exit()

    app = Game()
    app.run()
    app.clean()
