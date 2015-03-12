#! /usr/bin/env python
import sys, time

CHESS_BOARD_POINT_COUNTS=11

# Score board given
class Evaluation (object):

    def __init__ (self):
        self.POS = []
        for i in xrange(CHESS_BOARD_POINT_COUNTS):
            row = [(7 - max(abs(i - 7), abs(j - 7))) for j in xrange(CHESS_BOARD_POINT_COUNTS)]
            self.POS.append(tuple(row))
        self.POS = tuple(self.POS)
        self.STWO = 1 
        self.STHREE = 2
        self.SFOUR = 3
        self.TWO = 4 
        self.THREE = 5
        self.FOUR = 6 
        self.FIVE = 7 
        self.DFOUR = 8
        self.FOURT = 9
        self.DTHREE = 10
        self.NOTYPE = 11    
        self.ANALYSED = 255
        self.TODO = 0  
        self.result = [0 for i in xrange(CHESS_BOARD_POINT_COUNTS * 2)] 
        self.line = [0 for i in xrange(CHESS_BOARD_POINT_COUNTS * 2)] 
        self.record = []
        for i in xrange(CHESS_BOARD_POINT_COUNTS):
            self.record.append([])
            self.record[i] = []
            for j in xrange(CHESS_BOARD_POINT_COUNTS):
                self.record[i].append([ 0, 0, 0, 0])
        self.count = []
        for i in xrange(3):
            data = [ 0 for i in xrange(20) ]
            self.count.append(data)
        self.reset()

    def reset (self):
        TODO = self.TODO
        count = self.count
        for i in xrange(CHESS_BOARD_POINT_COUNTS):
            line = self.record[i]
            for j in xrange(CHESS_BOARD_POINT_COUNTS):
                line[j][0] = TODO
                line[j][1] = TODO
                line[j][2] = TODO
                line[j][3] = TODO
        for i in xrange(20):
            count[0][i] = 0
            count[1][i] = 0
            count[2][i] = 0
        return 0

    def evaluate (self, board, turn):
        score = self.__evaluate(board, turn)
        count = self.count
        if score < -9000:
            stone = turn == 1 and 2 or 1
            for i in xrange(20):
                if count[stone][i] > 0:
                    score -= i
        elif score > 9000:
            stone = turn == 1 and 2 or 1
            for i in xrange(20):
                if count[turn][i] > 0:
                    score += i
        return score
    
    def __evaluate (self, board, turn):
        record, count = self.record, self.count
        TODO, ANALYSED = self.TODO, self.ANALYSED
        self.reset()
        for i in xrange(CHESS_BOARD_POINT_COUNTS):
            boardrow = board[i]
            recordrow = record[i]
            for j in xrange(CHESS_BOARD_POINT_COUNTS):
                if boardrow[j] != 0:
                    if recordrow[j][0] == TODO: 
                        self.__analysis_horizon(board, i, j)
                    if recordrow[j][1] == TODO: 
                        self.__analysis_vertical(board, i, j)
                    if recordrow[j][2] == TODO:
                        self.__analysis_left(board, i, j)
                    if recordrow[j][3] == TODO:
                        self.__analysis_right(board, i, j)

        FIVE, FOUR = self.FIVE, self.FOUR
        THREE, TWO = self.THREE, self.TWO
        SFOUR, STHREE, STWO = self.SFOUR, self.STHREE, self.STWO
        check = {}

        for c in (FIVE, FOUR, SFOUR, THREE, STHREE, TWO, STWO):
            check[c] = 1
        for i in xrange(CHESS_BOARD_POINT_COUNTS):
            for j in xrange(CHESS_BOARD_POINT_COUNTS):
                stone = board[i][j]
                if stone != 0:
                    for k in xrange(4):
                        ch = record[i][j][k]
                        if ch in check:
                            count[stone][ch] += 1
        
        BLACK, WHITE = 1, 2
        if turn == WHITE:     
            if count[BLACK][FIVE]:
                return -9999
            if count[WHITE][FIVE]:
                return 9999
        else:
            if count[WHITE][FIVE]:
                return -9999
            if count[BLACK][FIVE]:
                return 9999
        
        if count[WHITE][SFOUR] >= 2:
            count[WHITE][FOUR] += 1
        if count[BLACK][SFOUR] >= 2:
            count[BLACK][FOUR] += 1

        wvalue, bvalue, win = 0, 0, 0
        if turn == WHITE:
            if count[WHITE][FOUR] > 0: return 9990
            if count[WHITE][SFOUR] > 0: return 9980
            if count[BLACK][FOUR] > 0: return -9970
            if count[BLACK][SFOUR] and count[BLACK][THREE]: 
                return -9960
            if count[WHITE][THREE] and count[BLACK][SFOUR] == 0:
                return 9950
            if    count[BLACK][THREE] > 1 and \
                count[WHITE][SFOUR] == 0 and \
                count[WHITE][THREE] == 0 and \
                count[WHITE][STHREE] == 0:
                    return -9940
            if count[WHITE][THREE] > 1:
                wvalue += 2000
            elif count[WHITE][THREE]:
                wvalue += 200
            if count[BLACK][THREE] > 1:
                bvalue += 500
            elif count[BLACK][THREE]:
                bvalue += 100
            if count[WHITE][STHREE]:
                wvalue += count[WHITE][STHREE] * 10
            if count[BLACK][STHREE]:
                bvalue += count[BLACK][STHREE] * 10
            if count[WHITE][TWO]:
                wvalue += count[WHITE][TWO] * 4
            if count[BLACK][TWO]:
                bvalue += count[BLACK][TWO] * 4
            if count[WHITE][STWO]:
                wvalue += count[WHITE][STWO]
            if count[BLACK][STWO]:
                bvalue += count[BLACK][STWO]
        else:
            if count[BLACK][FOUR] > 0: return 9990
            if count[BLACK][SFOUR] > 0: return 9980
            if count[WHITE][FOUR] > 0: return -9970
            if count[WHITE][SFOUR] and count[WHITE][THREE]:
                return -9960
            if count[BLACK][THREE] and count[WHITE][SFOUR] == 0:
                return 9950
            if    count[WHITE][THREE] > 1 and \
                count[BLACK][SFOUR] == 0 and \
                count[BLACK][THREE] == 0 and \
                count[BLACK][STHREE] == 0:
                    return -9940
            if count[BLACK][THREE] > 1:
                bvalue += 2000
            elif count[BLACK][THREE]:
                bvalue += 200
            if count[WHITE][THREE] > 1:
                wvalue += 500
            elif count[WHITE][THREE]:
                wvalue += 100
            if count[BLACK][STHREE]:
                bvalue += count[BLACK][STHREE] * 10
            if count[WHITE][STHREE]:
                wvalue += count[WHITE][STHREE] * 10
            if count[BLACK][TWO]:
                bvalue += count[BLACK][TWO] * 4
            if count[WHITE][TWO]:
                wvalue += count[WHITE][TWO] * 4
            if count[BLACK][STWO]:
                bvalue += count[BLACK][STWO]
            if count[WHITE][STWO]:
                wvalue += count[WHITE][STWO]
        
        wc, bc = 0, 0
        for i in xrange(CHESS_BOARD_POINT_COUNTS):
            for j in xrange(CHESS_BOARD_POINT_COUNTS):
                stone = board[i][j]
                if stone != 0:
                    if stone == WHITE:
                        wc += self.POS[i][j]
                    else:
                        bc += self.POS[i][j]
        wvalue += wc
        bvalue += bc
        
        if turn == WHITE:
            return wvalue - bvalue

        return bvalue - wvalue
    
    def __analysis_horizon (self, board, i, j):
        line, result, record = self.line, self.result, self.record
        TODO = self.TODO
        for x in xrange(CHESS_BOARD_POINT_COUNTS):
            line[x] = board[i][x]
        self.analysis_line(line, result, CHESS_BOARD_POINT_COUNTS, j)
        for x in xrange(CHESS_BOARD_POINT_COUNTS):
            if result[x] != TODO:
                record[i][x][0] = result[x]
        return record[i][j][0]
    
    def __analysis_vertical (self, board, i, j):
        line, result, record = self.line, self.result, self.record
        TODO = self.TODO
        for x in xrange(CHESS_BOARD_POINT_COUNTS):
            line[x] = board[x][j]
        self.analysis_line(line, result, CHESS_BOARD_POINT_COUNTS, i)
        for x in xrange(CHESS_BOARD_POINT_COUNTS):
            if result[x] != TODO:
                record[x][j][1] = result[x]
        return record[i][j][1]
    
    def __analysis_left (self, board, i, j):
        line, result, record = self.line, self.result, self.record
        TODO = self.TODO
        if i < j: x, y = j - i, 0
        else: x, y = 0, i - j
        k = 0
        while k < CHESS_BOARD_POINT_COUNTS:
            if x + k > CHESS_BOARD_POINT_COUNTS - 1 or y + k > CHESS_BOARD_POINT_COUNTS - 1:
                break
            line[k] = board[y + k][x + k]
            k += 1
        self.analysis_line(line, result, k, j - x)
        for s in xrange(k):
            if result[s] != TODO:
                record[y + s][x + s][2] = result[s]
        return record[i][j][2]

    def __analysis_right (self, board, i, j):
        line, result = self.line, self.result
        record = self.record
        TODO = self.TODO
        if (CHESS_BOARD_POINT_COUNTS - 1) - i < j: x, y, realnum = j - (CHESS_BOARD_POINT_COUNTS - 1) + i, (CHESS_BOARD_POINT_COUNTS - 1), (CHESS_BOARD_POINT_COUNTS - 1) - i
        else: x, y, realnum = 0, i + j, j
        k = 0
        while k < CHESS_BOARD_POINT_COUNTS:
            if x + k > (CHESS_BOARD_POINT_COUNTS - 1) or y - k < 0:
                break
            line[k] = board[y - k][x + k]
            k += 1
        self.analysis_line(line, result, k, j - x)
        for s in xrange(k):
            if result[s] != TODO:
                record[y - s][x + s][3] = result[s]
        return record[i][j][3]
    
    def analysis_line (self, line, record, num, pos):
        TODO, ANALYSED = self.TODO, self.ANALYSED
        THREE, STHREE = self.THREE, self.STHREE
        FOUR, SFOUR = self.FOUR, self.SFOUR
        while len(line) < CHESS_BOARD_POINT_COUNTS * 2: line.append(0xf)
        while len(record) < CHESS_BOARD_POINT_COUNTS * 2: record.append(TODO)
        for i in xrange(num, CHESS_BOARD_POINT_COUNTS * 2):
            line[i] = 0xf
        for i in xrange(num):
            record[i] = TODO
        if num < 5:
            for i in xrange(num): 
                record[i] = ANALYSED
            return 0
        stone = line[pos]
        inverse = (0, 2, 1)[stone]
        num -= 1
        xl = pos
        xr = pos
        while xl > 0:   
            if line[xl - 1] != stone: break
            xl -= 1
        while xr < num: 
            if line[xr + 1] != stone: break
            xr += 1
        left_range = xl
        right_range = xr
        while left_range > 0:
            if line[left_range - 1] == inverse: break
            left_range -= 1
        while right_range < num:
            if line[right_range + 1] == inverse: break
            right_range += 1
        
        if right_range - left_range < 4:
            for k in xrange(left_range, right_range + 1):
                record[k] = ANALYSED
            return 0
        
        for k in xrange(xl, xr + 1):
            record[k] = ANALYSED
        
        srange = xr - xl

        if srange >= 4:    
            record[pos] = self.FIVE
            return self.FIVE
        
        if srange == 3:    
            leftfour = False 
            if xl > 0:
                if line[xl - 1] == 0:
                    leftfour = True
            if xr < num:
                if line[xr + 1] == 0:
                    if leftfour:
                        record[pos] = self.FOUR 
                    else:
                        record[pos] = self.SFOUR
                else:
                    if leftfour:
                        record[pos] = self.SFOUR
            else:
                if leftfour:
                    record[pos] = self.SFOUR
            return record[pos]
        
        if srange == 2:
            left3 = False 
            if xl > 0:
                if line[xl - 1] == 0:
                    if xl > 1 and line[xl - 2] == stone:
                        record[xl] = SFOUR
                        record[xl - 2] = ANALYSED
                    else:
                        left3 = True
                elif xr == num or line[xr + 1] != 0:
                    return 0
            if xr < num:
                if line[xr + 1] == 0:
                    if xr < num - 1 and line[xr + 2] == stone:
                        record[xr] = SFOUR
                        record[xr + 2] = ANALYSED
                    elif left3:
                        record[xr] = THREE
                    else:
                        record[xr] = STHREE
                elif record[xl] == SFOUR:
                    return record[xl]
                elif left3:
                    record[pos] = STHREE
            else:
                if record[xl] == SFOUR:
                    return record[xl]
                if left3:
                    record[pos] = STHREE
            return record[pos]
        
        if srange == 1:
            left2 = False
            if xl > 2:
                if line[xl - 1] == 0:
                    if line[xl - 2] == stone:
                        if line[xl - 3] == stone:
                            record[xl - 3] = ANALYSED
                            record[xl - 2] = ANALYSED
                            record[xl] = SFOUR
                        elif line[xl - 3] == 0:
                            record[xl - 2] = ANALYSED
                            record[xl] = STHREE
                    else:
                        left2 = True
            if xr < num:
                if line[xr + 1] == 0:
                    if xr < num - 2 and line[xr + 2] == stone:
                        if line[xr + 3] == stone:
                            record[xr + 3] = ANALYSED
                            record[xr + 2] = ANALYSED
                            record[xr] = SFOUR
                        elif line[xr + 3] == 0:
                            record[xr + 2] = ANALYSED
                            record[xr] = left2 and THREE or STHREE
                    else:
                        if record[xl] == SFOUR:
                            return record[xl]
                        if record[xl] == STHREE:
                            record[xl] = THREE
                            return record[xl]
                        if left2:
                            record[pos] = self.TWO
                        else:
                            record[pos] = self.STWO
                else:
                    if record[xl] == SFOUR:
                        return record[xl]
                    if left2:
                        record[pos] = self.STWO
            return record[pos]
        return 0


# Game Tree Searcher (DFS)
class searcher (object):

    def __init__ (self):
        self.evaluator = Evaluation()
        self.board = [ [ 0 for n in xrange(CHESS_BOARD_POINT_COUNTS) ] for i in xrange(CHESS_BOARD_POINT_COUNTS) ]
        self.gameover = 0
        self.overvalue = 0
        self.maxdepth = 3

    def genmove (self, turn):
        moves = []
        board = self.board
        POSES = self.evaluator.POS
        for i in xrange(CHESS_BOARD_POINT_COUNTS):
            for j in xrange(CHESS_BOARD_POINT_COUNTS):
                if board[i][j] == 0:
                    score = POSES[i][j]
                    moves.append((score, i, j))
        moves.sort()
        moves.reverse()
        return moves
    
    def __search (self, turn, depth, alpha, beta):

        if depth <= 0:
            score = self.evaluator.evaluate(self.board, turn)
            return score

        score = self.evaluator.evaluate(self.board, turn)
        if abs(score) >= 9999 and depth < self.maxdepth: 
            return score

        moves = self.genmove(turn)
        bestmove = None

        for score, row, col in moves:

            self.board[row][col] = turn
            
            nturn = turn == 1 and 2 or 1

            score = - self.__search(nturn, depth - 1, -beta, -alpha)

            self.board[row][col] = 0

            if score > alpha:
                alpha = score
                bestmove = (row, col)
                if alpha >= beta:
                    break
        
        if depth == self.maxdepth and bestmove:
            self.bestmove = bestmove

        return alpha

    def search (self, turn, depth = 3):
        self.maxdepth = depth
        self.bestmove = None
        score = self.__search(turn, depth, -0x7fffffff, 0x7fffffff)
        if abs(score) > 8000:
            self.maxdepth = depth
            score = self.__search(turn, 1, -0x7fffffff, 0x7fffffff)
        row, col = self.bestmove
        return score, row, col
