# thyddle.py
from Thyddle.lexer import Lexer, TokenType
from Thyddle.parser import Parser, ParseError
from Thyddle.interpreter import Interpreter

def run(source, interpreter=None):
    ret = None
    if interpreter is None:
        interpreter = Interpreter()
    if source:
        ret = interpreter.interpret(source)
    
    return ret

def run_file(path, interpreter=None):
    with open(path, 'r') as file:
        source = file.read()
    return run(source, interpreter)

def run_repl(interpreter=None):
    if interpreter is None:
        interpreter = Interpreter()
    
    print("Thyddle REPL v0.1")
    print("Type 'exit()' to exit")
    
    while True:
        try:
            line = input(">>> ")
            if line.strip() == "exit()":
                break
            pr = run(line, interpreter)
            
            if pr:
                print(pr)
        except KeyboardInterrupt:
            print("\nUse 'exit()' to exit")
        except Exception as e:
            print(f"Error: {e}")
    
    print("Goodbye!")

if __name__ == "__main__":
    import sys
    
    interpreter = Interpreter()
    
    if len(sys.argv) > 1:
        run_file(sys.argv[1], interpreter)
    else:
        run_repl(interpreter)