# parser.py
from Thyddle.lexer import TokenType, Token

class ParseError(Exception):
    pass

class Expression:
    pass

class Binary(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"({self.left} {self.operator.lexeme} {self.right})"

class Grouping(Expression):
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return f"(group {self.expression})"

class Literal(Expression):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value) if self.value is not None else "nil"

class Unary(Expression):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"({self.operator.lexeme} {self.right})"

class Variable(Expression):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"(var {self.name.lexeme})"

class Assign(Expression):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"(assign {self.name.lexeme} {self.value})"

class Logical(Expression):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __str__(self):
        return f"({self.operator.lexeme} {self.left} {self.right})"

class Call(Expression):
    def __init__(self, callee, paren, arguments):
        self.callee = callee
        self.paren = paren
        self.arguments = arguments
    
    def __str__(self):
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"(call {self.callee} [{args_str}])"

class Get(Expression):
    def __init__(self, obj, name):
        self.obj = obj
        self.name = name
    
    def __str__(self):
        return f"(get {self.obj} {self.name.lexeme})"

class Set(Expression):
    def __init__(self, obj, name, value):
        self.obj = obj
        self.name = name
        self.value = value
    
    def __str__(self):
        return f"(set {self.obj} {self.name.lexeme} {self.value})"

class Index(Expression):
    def __init__(self, obj, index):
        self.obj = obj
        self.index = index
    
    def __str__(self):
        return f"(index {self.obj} {self.index})"

class SetIndex(Expression):
    def __init__(self, obj, index, value):
        self.obj = obj
        self.index = index
        self.value = value
    
    def __str__(self):
        return f"(set-index {self.obj} {self.index} {self.value})"

class ArrayLiteral(Expression):
    def __init__(self, elements):
        self.elements = elements
    
    def __str__(self):
        elements_str = ", ".join(str(elem) for elem in self.elements)
        return f"[{elements_str}]"

class ObjectLiteral(Expression):
    def __init__(self, properties):
        self.properties = properties
    
    def __str__(self):
        prop_strs = []
        for key, value in self.properties:
            prop_strs.append(f"{key.lexeme}: {value}")
        return f"{{{', '.join(prop_strs)}}}"

class Statement:
    pass

class LambdaExpression(Expression):
    def __init__(self, params, body):
        self.params = params  # List of parameter tokens
        self.body = body      # Body statement or expression
    
    def __str__(self):
        params_str = ", ".join(param.lexeme for param in self.params)
        return f"(lambda ({params_str}) {self.body})"

class ExpressionStatement(Statement):
    def __init__(self, expression):
        self.expression = expression
    
    def __str__(self):
        return f"{self.expression};"

class VarStatement(Statement):
    def __init__(self, name, initializer, is_const=False):
        self.name = name
        self.initializer = initializer
        self.is_const = is_const
    
    def __str__(self):
        keyword = "const" if self.is_const else "var"
        initializer = f" = {self.initializer}" if self.initializer else ""
        return f"{keyword} {self.name.lexeme}{initializer};"

class BlockStatement(Statement):
    def __init__(self, statements):
        self.statements = statements
    
    def __str__(self):
        stmts = "\n".join(str(stmt) for stmt in self.statements)
        return f"{{\n{stmts}\n}}"

class IfStatement(Statement):
    def __init__(self, condition, then_branch, else_if_branches, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_if_branches = else_if_branches
        self.else_branch = else_branch
    
    def __str__(self):
        result = f"if ({self.condition}) {self.then_branch}"
        for condition, branch in self.else_if_branches:
            result += f" elseif ({condition}) {branch}"
        if self.else_branch:
            result += f" else {self.else_branch}"
        return result

class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
    
    def __str__(self):
        return f"while ({self.condition}) {self.body}"

class ForStatement(Statement):
    def __init__(self, initializer, condition, increment, body):
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body
    
    def __str__(self):
        init = str(self.initializer) if self.initializer else ";"
        cond = str(self.condition) if self.condition else ""
        inc = str(self.increment) if self.increment else ""
        return f"for ({init} {cond}; {inc}) {self.body}"

class FunctionStatement(Statement):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    
    def __str__(self):
        params_str = ", ".join(param.lexeme for param in self.params)
        return f"function {self.name.lexeme}({params_str}) {self.body}"

class ReturnStatement(Statement):
    def __init__(self, keyword, value):
        self.keyword = keyword
        self.value = value
    
    def __str__(self):
        value = f" {self.value}" if self.value else ""
        return f"return{value};"

class BreakStatement(Statement):
    def __init__(self, keyword):
        self.keyword = keyword
    
    def __str__(self):
        return "break;"

class ContinueStatement(Statement):
    def __init__(self, keyword):
        self.keyword = keyword
    
    def __str__(self):
        return "continue;"

class ImportStatement(Statement):
    def __init__(self, module_name):
        self.module_name = module_name
    
    def __str__(self):
        return f"import {self.module_name};"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
    
    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements
    
    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration(False)
            if self.match(TokenType.CONST):
                return self.var_declaration(True)
            if self.match(TokenType.FUNC):
                return self.function_declaration()
            if self.match(TokenType.IMPORT):
                return self.import_declaration()
            
            return self.statement()
        except ParseError:
            self.synchronize()
            return None
    
    def var_declaration(self, is_const):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStatement(name, initializer, is_const)
    
    def function_declaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name.")
        parameters = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
            while self.match(TokenType.COMMA):
                if len(parameters) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before function body.")
        body = self.block()
        
        return FunctionStatement(name, parameters, body)
    
    def import_declaration(self):
        # Check if the module is a string literal
        if self.match(TokenType.STRING):
            module_token = self.previous()  # Get the string token
            module_name = module_token.literal  # Extract the actual module name (without quotes)
        else:
            # If it's not a string, it's an identifier
            module_token = self.consume(TokenType.IDENTIFIER, "Expect module name.")
            module_name = module_token.lexeme  # Extract the identifier's name
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after import statement.")
        return ImportStatement(module_name)



    
    def statement(self):
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        if self.match(TokenType.BREAK):
            return self.break_statement()
        if self.match(TokenType.CONTINUE):
            return self.continue_statement()
        if self.match(TokenType.LEFT_BRACE):
            return BlockStatement(self.block())
        
        return self.expression_statement()
    
    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        
        then_branch = self.statement()
        
        else_if_branches = []
        while self.match(TokenType.ELSEIF):
            self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'elseif'.")
            elseif_condition = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after elseif condition.")
            elseif_branch = self.statement()
            else_if_branches.append((elseif_condition, elseif_branch))
        
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        
        return IfStatement(condition, then_branch, else_if_branches, else_branch)
    
    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        
        return WhileStatement(condition, body)
    
    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        
        # Initializer
        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration(False)
        elif self.match(TokenType.CONST):
            initializer = self.var_declaration(True)
        else:
            initializer = self.expression_statement()
        
        # Condition
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        
        # Increment
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        
        body = self.statement()
        
        return ForStatement(initializer, condition, increment, body)
    
    def return_statement(self):
        keyword = self.previous()
        value = None
        
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStatement(keyword, value)
    
    def break_statement(self):
        keyword = self.previous()
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'break'.")
        return BreakStatement(keyword)
    
    def continue_statement(self):
        keyword = self.previous()
        self.consume(TokenType.SEMICOLON, "Expect ';' after 'continue'.")
        return ContinueStatement(keyword)
    
    def block(self):
        statements = []
        
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    def expression_statement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStatement(expr)
    
    def expression(self):
        return self.assignment()
    
    def assignment(self):
        expr = self.or_expr()
        
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            
            if isinstance(expr, Variable):
                return Assign(expr.name, value)
            elif isinstance(expr, Get):
                return Set(expr.obj, expr.name, value)
            elif isinstance(expr, Index):
                return SetIndex(expr.obj, expr.index, value)
            
            self.error(equals, "Invalid assignment target.")
        
        return expr
    
    def or_expr(self):
        expr = self.and_expr()
        
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_expr()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def and_expr(self):
        expr = self.equality()
        
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def equality(self):
        expr = self.comparison()
        
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def comparison(self):
        expr = self.term()
        
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def term(self):
        expr = self.factor()
        
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def factor(self):
        expr = self.unary()
        
        while self.match(TokenType.SLASH, TokenType.STAR, TokenType.MODULO):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        
        return expr
    
    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        
        return self.call()
    
    def call(self):
        expr = self.primary()
        
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expr = Get(expr, name)
            elif self.match(TokenType.LEFT_BRACKET):
                index = self.expression()
                self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after array index.")
                expr = Index(expr, index)
            else:
                break
        
        return expr
    
    def finish_call(self, callee):
        arguments = []
        
        if not self.check(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            
            while self.match(TokenType.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(), "Cannot have more than 255 arguments.")
                arguments.append(self.expression())
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        
        return Call(callee, paren, arguments)
    
    # Fix for parser.py - Lambda Expression Handling

    def primary(self):
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        
        # Handle lambdas with arrow syntax
        if self.match(TokenType.LEFT_PAREN):
            # Check if this is a lambda expression or just a grouping
            if self.check(TokenType.RIGHT_PAREN) or self.check(TokenType.IDENTIFIER):
                # Save current position in case this is not a lambda
                current_pos = self.current
                params = []
                
                if not self.check(TokenType.RIGHT_PAREN):
                    params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                    while self.match(TokenType.COMMA):
                        if len(params) >= 255:
                            self.error(self.peek(), "Cannot have more than 255 parameters.")
                        params.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                
                # If we see => after parameters, it's a lambda
                if self.match(TokenType.RIGHT_PAREN) and self.match(TokenType.ARROW):
                    # Parse the body - this could be a block or a single expression
                    body = None
                    
                    if self.match(TokenType.LEFT_BRACE):
                        body = BlockStatement(self.block())
                    else:
                        expr = self.expression()
                        body = ReturnStatement(None, expr)
                    
                    return LambdaExpression(params, body)
                else:
                    # Not a lambda, restore position and continue as grouping
                    self.current = current_pos
            
            # Regular grouping expression
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        
        if self.match(TokenType.LEFT_BRACKET):
            elements = []
            
            if not self.check(TokenType.RIGHT_BRACKET):
                elements.append(self.expression())
                
                while self.match(TokenType.COMMA):
                    if len(elements) >= 255:
                        self.error(self.peek(), "Cannot have more than 255 elements in an array.")
                    elements.append(self.expression())
            
            self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after array elements.")
            return ArrayLiteral(elements)
        
        if self.match(TokenType.LEFT_BRACE):
            properties = []
            
            if not self.check(TokenType.RIGHT_BRACE):
                # Get the first property name
                if not self.check(TokenType.IDENTIFIER):
                    self.error(self.peek(), "Expect property name.")
                key = self.consume(TokenType.IDENTIFIER, "Expect property name.")
                
                # Ensure colon exists
                self.consume(TokenType.COLON, "Expect ':' after property name.")
                
                # Get the property value
                value = self.expression()
                properties.append((key, value))
                
                # Handle additional properties
                while self.match(TokenType.COMMA):
                    if len(properties) >= 255:
                        self.error(self.peek(), "Cannot have more than 255 properties in an object.")
                    
                    # Get next property
                    if not self.check(TokenType.IDENTIFIER):
                        self.error(self.peek(), "Expect property name.")
                    key = self.consume(TokenType.IDENTIFIER, "Expect property name.")
                    
                    # Ensure colon exists
                    self.consume(TokenType.COLON, "Expect ':' after property name.")
                    
                    # Get the property value
                    value = self.expression()
                    properties.append((key, value))
            
            self.consume(TokenType.RIGHT_BRACE, "Expect '}' after object properties.")
            return ObjectLiteral(properties)
        
        raise self.error(self.peek(), "Expect expression.")

    
    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        
        return False
    
    def check(self, type):
        if self.is_at_end():
            return False
        return self.peek().type == type
    
    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def is_at_end(self):
        return self.peek().type == TokenType.EOF
    
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]
    
    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        
        raise self.error(self.peek(), message)
    
    # Completing the parser.py file
    def error(self, token, message):
        if token.type == TokenType.EOF:
            print(f"Error at end: {message}")
        else:
            print(f"Error at '{token.lexeme}': {message}")
        
        return ParseError()
    
    def synchronize(self):
        self.advance()
        
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            
            if self.peek().type in [
                TokenType.FUNC,
                TokenType.VAR,
                TokenType.CONST,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.RETURN,
                TokenType.IMPORT
            ]:
                return
            
            self.advance()