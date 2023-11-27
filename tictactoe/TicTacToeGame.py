# Reference source: https://gist.github.com/qianguigui1104/edb3b11b33c78e5894aad7908c773353
# Tic Tack Toe 

from tictactoe.TicTacToeBoard import TicTacToeBoard
from connection.TCPConnection import TCPConnection
from connection.OncomingConnection import OncomingConnection
from message.MessageInfo import MessageInfo
from message.Segment import Segment
from message.SegmentFlag import SegmentFlag

class TicTacToeGame():
    def __init__(self, connection: TCPConnection) -> None:
        self.connection = connection
        self.board = TicTacToeBoard()

    def set_peer(self, connection: OncomingConnection):
        self.peer_ip = connection.address[0]
        self.peer_port = connection.address[1]
        self.connectionInfo = connection
        
    def intro(self):
        print("\nHello! Welcome to Tic Tac Toe game!\n")
        print("Rules: Player 1 and player 2, represented by X and O, take turns "
            "marking the spaces in a 3*3 grid. The player who succeeds in placing "
            "three of their marks in a horizontal, vertical, or diagonal row wins. "
            "X goes first, O goes later.")

    def choose_symbol(self):
        self.own_symbol = ""
        while True:
            self.own_symbol = input("Do you want to be X, O, or N (ask let your opponent decide)? ")
            if self.own_symbol == "X":
                self.opponent_symbol = "O"
                print(f"Your opponent is O")
                break
            elif self.own_symbol == "O":
                self.opponent_symbol = "X"
                print("Your opponent is X. ")
                break
            elif self.own_symbol == "N":
                print("Asking opponent for symbols. ")
                self.opponent_symbol = "N"
                break
            else:
                print("Not a valid input. ")

        print("\n")

    def assign_symbol(self, symbol: chr):
        self.own_symbol = symbol
        if self.own_symbol == 'X':
            self.opponent_symbol = 'O'
        elif self.own_symbol == 'O':
            self.opponent_symbol = 'X'
        else:
            raise ValueError("Symbol should only be O or X")

    def start_move(self):
        self.board.print()
        print("Player "+ self.own_symbol + ", it is your turn. ")

        while True:
            try:
                row = int(input("Pick a row:"
                                "[upper row: enter 0, middle row: enter 1, bottom row: enter 2]: "))
                column = int(input("Pick a column:"
                                "[left column: enter 0, middle column: enter 1, right column enter 2]: "))
                self.board.put(self.own_symbol, row, column)
                
                # TODO: use proper messaging when sending
                self.connectionInfo = self.connection.sendStopNWait(
                    MessageInfo(
                        self.peer_ip,
                        self.peer_port,
                        Segment(
                            SegmentFlag.FLAG_NONE,
                            self.connectionInfo.seq_num,
                            self.connectionInfo.ack_num,
                            f"{row}{column}".encode()
                        )
                    )
                )
                # self.connection.send(f"{row}{column}".encode(), self.peer_ip, self.peer_port)
                break
            
            except Exception as e:
                print(e)
                print()
        
        self.board.print()
    
    def wait_move(self):
        print("It's player "+ self.opponent_symbol + "'s move")
        
        # TODO: use proper messaging when listening
        self.connectionInfo, data = self.connection.receiveStopNWait()
        # data, peer_address = self.connection.listen()
        data, checksum = Segment.unpack_str_payload(data)
        data = data.payload.decode()
        print(data)

        self.board.put(self.opponent_symbol, int(data[0]), int(data[1]))


    def start_game(self):
        count = 1
        winner = False

        if(self.own_symbol == 'O'):
            count += 1
            self.wait_move()

        winner_symbol = ""
        while count < 10 and not winner:
            self.start_move()
    
            if count == 9:
                print("The board is full.")
    
            winner, winner_symbol = self.board.check_winner(self.own_symbol, self.opponent_symbol)
            count += 1

            if count > 10 or winner:
                break

            self.wait_move()
            winner, winner_symbol = self.board.check_winner(self.own_symbol, self.opponent_symbol)
            count += 1
        
        if not winner:
            print("Game ended with a tie!")
        else:
            print(f"Game ended with player {winner_symbol}'s victory")


    def summary(self):
        print("------------------------------\n")
        print("Final result")
        self.board.print()

        winner, symbol = self.board.check_winner(self.own_symbol, self.opponent_symbol)
        if (winner == True):
            print("Winner : Player " + symbol + ".")
        else:
            print("The game ended with a tie. ")
            
    def initialize_finder(self):
        self.intro()
        self.board.clear()
        self.board.print()

        while True:
            self.choose_symbol()

            # TODO: use proper messaging when sending
            self.connectionInfo = self.connection.sendStopNWait(
                MessageInfo(
                    self.peer_ip,
                    self.peer_port,
                    Segment(
                        SegmentFlag.FLAG_NONE,
                        self.connectionInfo.seq_num,
                        self.connectionInfo.ack_num,
                        self.own_symbol.encode()
                    )
                )
            )
            # self.connection.send(self.own_symbol.encode(), self.peer_ip, self.peer_port)

            if self.own_symbol == "N":
                response, client_address = self.connection.listen()
                data = response.decode()
                if(data == "X"):
                    print(f"Your opponent chooses {response.decode()}")
                    self.assign_symbol("O")
                    break
                elif(data == "O"):
                    print(f"Your opponent chooses {response.decode()}")
                    self.assign_symbol("X")
                    break
                elif(data == "N"):
                    print("Your opponent lets you choose your symbol")
                    continue

            else:
                break

        self.start_game()

    def initialize_waiter(self):
        self.intro()
        self.board.clear()
        self.board.print()

        print("Waiting for finder to choose a symbol")

        while True:
            # TODO: use proper messaging when listening
            # response, client_address = self.connection.listen()
            self.connectionInfo, data = self.connection.receiveStopNWait()
            data, checksum = Segment.unpack_str_payload(data)
            data = data.payload.decode()
            if(data == "X"):
                print(f"Your opponent chooses {data}")
                self.assign_symbol("O")
                break
            elif(data == "O"):
                print(f"Your opponent chooses {data}")
                self.assign_symbol("X")
                break
            elif(data == "N"):
                print("Your opponent lets you choose your symbol")

                self.choose_symbol()
                
                self.connectionInfo = self.connection.sendStopNWait(
                    MessageInfo(
                        self.peer_ip,
                        self.peer_port,
                        Segment(
                            SegmentFlag.FLAG_NONE,
                            self.connectionInfo.seq_num,
                            self.connectionInfo.ack_num,
                            self.own_symbol.encode()
                        )
                    )
                )
                # self.connection.send(self.own_symbol.encode(), self.peer_ip, self.peer_port)
                if self.own_symbol == "N":
                    continue
                break

        self.start_game()
