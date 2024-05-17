

class Logger: 
    def __init__(self):
        pass
    def debug(self, message):
        if self.debug: 
            print(f"[debug] {message}")
    def error(self, message):
        print(f"[ERROR] {message}")
    def log(self, message):
        print(f"{message}")
    @staticmethod
    def format_number(num):
        num_str = str(num)
        return ' ' * (4 - len(num_str)) + num_str
