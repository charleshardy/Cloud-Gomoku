#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This program is a five in row game, which is used for the coding
camp 2015 in WindRiver.com"""

from pygame import *
time.Clock()

import threading
import json

from node import Node
from config import cloud_configs

CHESS_BOARD_BLOCK_COUNTS = 11
DRAW = 0
CONTINUE = 1
WIN = 2
ERROR = 3

class Game(threading.Thread):
    
    def __init__(self, gameid, cloud_name="Mashery"):

        # Waiting for connection
        #self.init_server_conn()
        threading.Thread.__init__(self)
        self.data_name = gameid
	self.cloud_name = cloud_name
        self.node = Node(cloud_name, cloud_configs[cloud_name])
        self.data_id = self.node.dataId(self.data_name)
	self.winnerspawns = []
	self.pos = []
        data = {'SeqID':'', 'PosX':'', 'PosY':'', 'Status':''}
	try: self.node.setData(self.data_id, json.dumps(data))
        except:
            print("Fail to set data %s" % self.data_name)

    def run(self):
	game_not_over = True

	del(self.pos[:])
        self.pos.extend([['_']*CHESS_BOARD_BLOCK_COUNTS for foo in range(CHESS_BOARD_BLOCK_COUNTS)])

	current_role = 0
	while game_not_over:
        # get data
	    try: data = json.loads(self.node.getData(self.data_id))
            except:
                print("Fail to get data %s" % self.data_name)
                continue
            if data['Status'] != DRAW:
	        continue
	    else:
	        current_role = data['SeqID'] % 2
	        self.current_pawn = current_role^1
	        X = data['PosX']
		Y = data['PosY']
	        if self.pos[X][Y] != '_':
		    game_not_over = False
	            new_data = {'SeqID':data['SeqID'], 'PosX':data['PosX'], 'PosY':data['PosY'],'Status':ERROR}
		    try: self.node.setData(self.data_id, json.dumps(new_data))
		    except:
		        print("Fail to set data %s" % self.data_name)
		        return
	        self.pos[X][Y] = str(self.current_pawn)
                self.actual_pos = (X, Y)
	        result = self.is_winner()
	        new_data = {'SeqID':data['SeqID'], 'PosX':data['PosX'], 'PosY':data['PosY'], 'Status':result, 'WinSpawns':self.winnerspawns}
		try: self.node.setData(self.data_id, json.dumps(new_data))
                except:
                    print("Fail to set data %s" % self.data_name)
                    return
                else:
                    print("set to data X=%d, Y=%d, status=%d" % (X, Y, result))

		if result == WIN:
	            game_not_over = False
    
    def is_winner(self):
        X,Y = self.actual_pos
        pawn = self.current_pawn
        row1 = [((X,y),self.pos[X][y])for y in range(CHESS_BOARD_BLOCK_COUNTS)]#+[('',invpawn)]
        print "----------row1="+str(row1)
        row2 = [((x,Y),self.pos[x][Y])for x in range(CHESS_BOARD_BLOCK_COUNTS)]#+[('',invpawn)]
        print "----------row2="+str(row2)
        foo = X-Y
        row3 = [((x,x-foo),self.pos[x][x-foo])for x in range(CHESS_BOARD_BLOCK_COUNTS)if x-foo<CHESS_BOARD_BLOCK_COUNTS]#+[('',invpawn)]
        foo = X+Y
        row4 = [((x,foo-x),self.pos[x][foo-x])for x in range(CHESS_BOARD_BLOCK_COUNTS)if foo-x<CHESS_BOARD_BLOCK_COUNTS]#+[('',invpawn)]
        print "----------row3="+str(row3)
        print "----------row4="+str(row4)
        for row in (row1,row2,row3,row4):
            coords,pawns = zip(*row)
            pawns = ''.join(pawns)
            print "-------coords="+str(coords)
            print "-------pawns="+str(pawns)
	    print "-------pawn="+str(pawn)*5
            index1 = pawns.find(str(pawn)*5)
            if index1 == -1: continue
            #index2 = pawns[index1:].find(pawn+invpawn)
            #index2bis = pawns[index1:].find(pawn+'_')
            #if -1 < index2 and -1 < index2bis: index2 = min(index2,index2bis)
            #else: index2 = max(index2,index2bis)
            #if index2 == -1: continue
           # print "-----index1="+str(index1)
            #print "-----index2="+str(index2)
            self.winnerspawns.extend((coords[index1:index1+1]))
            self.winnerspawns.extend((coords[index1+4:index1+5]))
       # print "-------self.winnerspawns="+str(self.winnerspawns)
	if self.winnerspawns:
            print "----------------winnerspawns="+str(self.winnerspawns)
            return WIN
	else:
	    return CONTINUE

data_name = "vlv_game_id"
cloud_name = "Mashery"
node = Node(cloud_name, cloud_configs[cloud_name])
data_id = node.dataId(data_name)

vlv_GAME_ID = string.atoi(node.getData(data_id))

while True:
    vlv_GAME_S_ID = node.getData(data_id)
    if vlv_GAME_S_ID != None:
        print "=================vlv_GAME_S_ID = "+ str(vlv_GAME_S_ID)
        vlv_GAME_NEW_ID = string.atoi(vlv_GAME_S_ID)
        if vlv_GAME_NEW_ID > vlv_GAME_ID:
            while vlv_GAME_NEW_ID > vlv_GAME_ID:
                game_id = 'vlv_GMOVE_' + str(vlv_GAME_ID)
                game = Game(game_id)   
                game.start()

                print "========vlv_GAME_ID="+str(vlv_GAME_ID)
                vlv_GAME_ID += 1

