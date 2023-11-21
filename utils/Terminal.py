class Terminal:
    ALERT_SYMBOL = "[!]"
    CRITICAL_SYMBOL = "[!!]"
    INPUT_SYMBOL = "[?]"

    @staticmethod
    def input(message:str, descriptor:str=None):
        print(Terminal.INPUT_SYMBOL,end=" ")
        if descriptor != None:
            print(f"[{descriptor}]",end=" ")
        print(f"{message}",end=" ")
        return input()
    
    @staticmethod
    def log(message:str, symbol:str=None, descriptor:str=None):
        if symbol != None:
            print(f"{symbol}",end=" ")
        if descriptor != None:
            print(f"[{descriptor}]",end=" ")
        print(f"{message}",end="\n")
