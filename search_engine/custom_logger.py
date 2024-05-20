

class Logger: 
    def __init__(self):
        self.verbose = False
    def debug(self, message):
        if self.debug: 
            print(f"[debug] {message}")
    def error(self, message):
        print(f"[ERROR] {message}")



    def log(self, message):
        if self.verbose: 
            print(f"{message}")
    @staticmethod
    def format_number(num):
        num_str = str(num)
        return ' ' * (4 - len(num_str)) + num_str
