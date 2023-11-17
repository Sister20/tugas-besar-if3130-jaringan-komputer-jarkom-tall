class Logger:
    ALERT_SYMBOL = "[!]"
    CRITICAL_SYMBOL = "[!!]"
    INPUT_SYMBOL = "[?]"
    
    @staticmethod
    def alert(message:str):
        print(f"{Logger.ALERT_SYMBOL} {message}")

    @staticmethod
    def input(message:str):
        return input(f"{Logger.INPUT_SYMBOL} {message} ")
    
    @staticmethod
    def critical(message:str):
        print(f"{Logger.CRITICAL_SYMBOL} {message}")
    
