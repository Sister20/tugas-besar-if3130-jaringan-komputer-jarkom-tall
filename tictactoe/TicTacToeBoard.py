class TicTacToeBoard():
    def __init__(self) -> None:
        self.matrix = [[" ", " ", " "],
                [" ", " ", " "],
                [" ", " ", " "]]
        return
    
    def print(self):
        print("---+---+---")
        for r in range(3):
            print(self.matrix[r][0], " |", self.matrix[r][1], "|", self.matrix[r][2])
            print("---+---+---")
        return self.matrix
    
    def put(self, symbol: chr, row: int, column: int):
        if(column > 2 or column < 0 or row > 2 or row < 0): raise Exception("The square you picked out of bounds. Pick another one.")
        if(self.matrix[row][column] != " "): raise Exception("The square you picked is already filled. Pick another one.")
        self.matrix[row][column] = symbol
        return self.matrix
    
    def clear(self):
        self.matrix = [[" ", " ", " "],
                [" ", " ", " "],
                [" ", " ", " "]]
        return
    
    def check_winner(self, symbol_1: chr, symbol_2: chr) -> (bool, chr):
        for row in range (0, 3):
            if (self.matrix[row][0] == self.matrix[row][1] == self.matrix[row][2] == symbol_1):
                print("Player " + symbol_1 + ", have won")
                return True, symbol_1
            elif (self.matrix[row][0] == self.matrix[row][1] == self.matrix[row][2] == symbol_2):
                print("Player " + symbol_2 + ", have won")
                return True, symbol_2

        for col in range (0, 3):
            if (self.matrix[0][col] == self.matrix[1][col] == self.matrix[2][col] == symbol_1):
                print("Player " + symbol_1 + ", have won")
                return True, symbol_1
            elif (self.matrix[0][col] == self.matrix[1][col] == self.matrix[2][col] == symbol_2):
                print("Player " + symbol_2 + ", have won")
                return True, symbol_2

        if self.matrix[0][0] == self.matrix[1][1] == self.matrix[2][2] == symbol_1:
            winner = True
            print("Player " + symbol_1 + ", have won")
            return True, symbol_1
        elif self.matrix[0][0] == self.matrix[1][1] == self.matrix[2][2] == symbol_2:
            print("Player " + symbol_2 + ", have won")
            return True, symbol_2
        elif self.matrix[0][2] == self.matrix[1][1] == self.matrix[2][0] == symbol_1:
            print("Player " + symbol_1 + ", have won")
            return True, symbol_1
        elif self.matrix[0][2] == self.matrix[1][1] == self.matrix[2][0] == symbol_2:
            print("Player " + symbol_2 + ", have won")
            return True, symbol_2
        
        return False, None