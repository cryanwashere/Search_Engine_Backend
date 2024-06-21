

class Logger: 
    def __init__(self, object_name):
        self.verbose = False
        self.object_name = object_name
        self.importance_threshold = 0

    def debug(self, message):
        if self.debug: 
            print(f"[{self.object_name}.debug] {message}")
    def error(self, message):
        print(f"[{self.object_name}.error] {message}")

    def log(self, message, importance=1):
        if self.verbose and importance > self.importance_threshold: 
            print(f"[{self.object_name}.log] {message}")
            
    @staticmethod
    def format_number(num):
        num_str = str(num)
        return ' ' * (4 - len(num_str)) + num_str
