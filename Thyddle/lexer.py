# Fix for lexer.py
from enum import Enum, auto
import re

class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    MODULO = auto()
    PIPE = auto()      # Pipe operator for function chaining
    ARROW = auto()     # Arrow for lambdas
    DOUBLE_COLON = auto()  # For type hints
    
    # Comparisons
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    COLON = auto()     # For object literals and type hints
    
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    MULTILINE_STRING = auto()  # Triple quoted strings
    
    # Keywords
    AND = auto()
    OR = auto()
    IF = auto()
    ELSE = auto()
    ELSEIF = auto()
    TRUE = auto()
    FALSE = auto()
    NIL = auto()
    FUNC = auto()      # Changed from FUNCTION to FUNC
    VAR = auto()
    CONST = auto()
    RETURN = auto()
    WHILE = auto()
    FOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    IMPORT = auto()
    UNLESS = auto()    # Reverse of IF
    UNTIL = auto()     # Reverse of WHILE
    MAYBE = auto()     # Optional chaining
    DEFAULT = auto()   # For default values
    MATCH = auto()     # Pattern matching
    CASE = auto()      # For match cases
    
    EOF = auto()

class Token:
    def __init__(self, token_type, lexeme, literal, line):
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"
    
    def __repr__(self):
        return self.__str__()

class Lexer:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        
        self.keywords = {
            "and": TokenType.AND,
            "or": TokenType.OR,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "elseif": TokenType.ELSEIF,
            "true": TokenType.TRUE,
            "false": TokenType.FALSE,
            "nil": TokenType.NIL,
            "func": TokenType.FUNC,       # Changed from "function" to "func"
            "var": TokenType.VAR,
            "const": TokenType.CONST,
            "return": TokenType.RETURN,
            "while": TokenType.WHILE,
            "for": TokenType.FOR,
            "break": TokenType.BREAK,
            "continue": TokenType.CONTINUE,
            "import": TokenType.IMPORT,
            "unless": TokenType.UNLESS,   # New keyword
            "until": TokenType.UNTIL,     # New keyword
            "maybe": TokenType.MAYBE,     # New keyword
            "default": TokenType.DEFAULT, # New keyword
            "match": TokenType.MATCH,     # New keyword
            "case": TokenType.CASE        # New keyword
        }
    
    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens
    
    def is_at_end(self):
        return self.current >= len(self.source)
    
    def scan_token(self):
        c = self.advance()
        
        if c == '(':
            self.add_token(TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(TokenType.RIGHT_BRACE)
        elif c == '[':
            self.add_token(TokenType.LEFT_BRACKET)
        elif c == ']':
            self.add_token(TokenType.RIGHT_BRACKET)
        elif c == ',':
            self.add_token(TokenType.COMMA)
        elif c == '.':
            self.add_token(TokenType.DOT)
        elif c == '-':
            if self.match('>'):
                self.add_token(TokenType.ARROW)
            else:
                self.add_token(TokenType.MINUS)
        elif c == '+':
            self.add_token(TokenType.PLUS)
        elif c == ';':
            self.add_token(TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(TokenType.STAR)
        elif c == '%':
            self.add_token(TokenType.MODULO)
        elif c == '|':
            self.add_token(TokenType.PIPE)
        elif c == ':':
            # Fixed colon handling
            self.add_token(TokenType.DOUBLE_COLON if self.match(':') else TokenType.COLON)
        elif c == '!':
            self.add_token(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
        elif c == '=':
            self.add_token(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
        elif c == '<':
            self.add_token(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
        elif c == '>':
            self.add_token(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
        elif c == '/':
            if self.match('/'):
                # A comment goes until the end of the line
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('*'):
                # Multiline comment
                self.multiline_comment()
            else:
                self.add_token(TokenType.SLASH)
        elif c in [' ', '\r', '\t']:
            # Ignore whitespace
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self.string('"')
        elif c == "'":
            self.string("'")
        elif self.is_digit(c):
            self.number()
        elif self.is_alpha(c):
            self.identifier()
        else:
            print(f"Unexpected character at line {self.line}: {c}")
    
    def multiline_comment(self):
        while not self.is_at_end():
            if self.peek() == '*' and self.peek_next() == '/':
                self.advance()  # Consume *
                self.advance()  # Consume /
                return
            elif self.peek() == '\n':
                self.line += 1
            
            self.advance()
    
    def multiline_string(self):
        start_line = self.line
        
        while not (self.peek() == '"' and self.peek_next() == '"' and self.peek_next_next() == '"') and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()
        
        if self.is_at_end():
            print(f"Unterminated multiline string starting at line {start_line}")
            return
        
        # Consume the closing triple quotes
        self.advance()  # First "
        self.advance()  # Second "
        self.advance()  # Third "
        
        # Get the string value (without the triple quotes)
        value = self.source[self.start + 3:self.current - 3]
        
        # Fix: Use raw strings for regex patterns to avoid escape issues
        value = re.sub(r'\\n', '\n', value)
        value = re.sub(r'\\t', '\t', value)
        value = re.sub(r'\\r', '\r', value)
        value = re.sub(r'\\\\', '\\', value)
        value = re.sub(r'\\"', '"', value)
        value = re.sub(r"\\'", "'", value)
        
        self.add_token(TokenType.MULTILINE_STRING, value)
    
    def peek_next_next(self):
        if self.current + 2 >= len(self.source):
            return '\0'
        return self.source[self.current + 2]
    
    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char
    
    def match(self, expected):
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        
        self.current += 1
        return True
    
    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]
    
    def string(self, quote_type):
        while self.peek() != quote_type and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            if self.peek() == '\\' and self.peek_next() == quote_type:
                self.advance()  # Skip the escape character
            self.advance()
        
        if self.is_at_end():
            print(f"Unterminated string at line {self.line}")
            return
        
        # The closing quote
        self.advance()
        
        # Get the string value (without the quotes)
        value = self.source[self.start + 1:self.current - 1]
        
        # Fix: Use safe substitution for escape sequences
        try:
            # Process escape sequences
            value = value.replace('\\n', '\n')
            value = value.replace('\\t', '\t')
            value = value.replace('\\r', '\r')
            value = value.replace('\\\\', '\\')
            value = value.replace('\\"', '"')
            value = value.replace("\\'", "'")
        except Exception as e:
            print(f"Error processing string escape sequences: {e}")
        
        self.add_token(TokenType.STRING, value)
    
    def is_digit(self, c):
        return c >= '0' and c <= '9'
    
    def number(self):
        # Handle hex numbers (0x...)
        if self.peek() == 'x' and self.previous() == '0':
            self.advance()  # Consume 'x'
            while self.is_hex_digit(self.peek()):
                self.advance()
            
            hex_value = int(self.source[self.start + 2:self.current], 16)
            self.add_token(TokenType.NUMBER, hex_value)
            return
        
        # Handle binary numbers (0b...)
        if self.peek() == 'b' and self.previous() == '0':
            self.advance()  # Consume 'b'
            while self.is_binary_digit(self.peek()):
                self.advance()
            
            bin_value = int(self.source[self.start + 2:self.current], 2)
            self.add_token(TokenType.NUMBER, bin_value)
            return
            
        # Normal decimal numbers
        while self.is_digit(self.peek()):
            self.advance()
        
        # Look for a fractional part
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Consume the '.'
            self.advance()
            
            while self.is_digit(self.peek()):
                self.advance()
        
        value = float(self.source[self.start:self.current])
        # If it's an integer value, store it as an int
        if value.is_integer():
            value = int(value)
            
        self.add_token(TokenType.NUMBER, value)
    
    def is_hex_digit(self, c):
        return self.is_digit(c) or ('a' <= c.lower() <= 'f')
    
    def is_binary_digit(self, c):
        return c == '0' or c == '1'
    
    def previous(self):
        return self.source[self.current - 1]
    
    def is_alpha(self, c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'
    
    def is_alphanumeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)
    
    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()
        
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        
        self.add_token(token_type)
    
    def add_token(self, token_type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))