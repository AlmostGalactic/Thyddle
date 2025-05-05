from Thyddle.thyddle import run_file, run_repl
from Thyddle.interpreter import Interpreter

if __name__ == "__main__":
    import sys
    
    interpreter = Interpreter()
    
    if len(sys.argv) > 1:
        run_file(sys.argv[1], interpreter)
    else:
        run_file("repl.thy", interpreter)