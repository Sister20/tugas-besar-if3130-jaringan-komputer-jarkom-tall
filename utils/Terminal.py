class Terminal:
    ALERT_SYMBOL = "[!]"
    CRITICAL_SYMBOL = "[!!]"
    INPUT_SYMBOL = "[?]"
    INFO_SYMBOL = "[i]"

    @staticmethod
    def input(message: str, descriptor: str = None):
        print(Terminal.INPUT_SYMBOL, end=" ")
        if descriptor is not None:
            print(f"[{descriptor}]", end=" ")
        print(f"{message}", end=" ")
        return input()

    @staticmethod
    def log(message: str, symbol: str = None, descriptor: str = None):
        if symbol is not None:
            print(f"{symbol}", end=" ")
        if descriptor is not None:
            print(f"[{descriptor}]", end=" ")
        print(f"{message}", end="\n")
