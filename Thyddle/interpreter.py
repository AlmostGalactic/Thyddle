# interpreter.py
import math
import random

from Thyddle.lexer import TokenType
from Thyddle.lexer import Lexer
from Thyddle.parser import Parser
from Thyddle.parser import (
    Expression, Binary, Grouping, Literal, Unary, Variable, Assign, Logical,
    Call, Get, Set, Index, SetIndex, ArrayLiteral, ObjectLiteral, Statement,
    ExpressionStatement, VarStatement, BlockStatement, IfStatement, WhileStatement,
    ForStatement, FunctionStatement, ReturnStatement, BreakStatement, ContinueStatement,
    ImportStatement, LambdaExpression
)

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(self)

class BreakException(Exception):
    pass

class ContinueException(Exception):
    pass

class ThyddleRuntimeError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.constants = set()
        self.enclosing = enclosing
    
    def define(self, name, value, is_const=False):
        self.values[name] = value
        if is_const:
            self.constants.add(name)
    
    def get(self, name):
        if name in self.values:
            return self.values[name]
        
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise ThyddleRuntimeError(f"Undefined variable '{name}'.")
    
    def assign(self, name, value):
        if name in self.constants:
            raise ThyddleRuntimeError(f"Cannot reassign constant '{name}'.")
        
        if name in self.values:
            self.values[name] = value
            return
        
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        
        raise ThyddleRuntimeError(f"Undefined variable '{name}'.")


class ThyddleFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure
    
    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        
        for i in range(len(self.declaration.params)):
            environment.define(
                self.declaration.params[i].lexeme, 
                arguments[i]
            )
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnValue as return_value:
            return return_value.value
        
        return None
    
    def __str__(self):
        return f"<function {self.declaration.name.lexeme}>"

class ThyddleLambda(ThyddleFunction):
    def __init__(self, declaration, closure):
        self.declaration = declaration  # LambdaExpression
        self.closure = closure          # Environment where lambda was defined
    
    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        
        # Bind parameters to arguments
        for i in range(len(self.declaration.params)):
            environment.define(
                self.declaration.params[i].lexeme, 
                arguments[i]
            )
        
        # Execute the body based on its type
        if isinstance(self.declaration.body, BlockStatement):
            try:
                interpreter.execute_block(self.declaration.body.statements, environment)
            except ReturnValue as return_value:
                return return_value.value
        elif isinstance(self.declaration.body, ReturnStatement):
            # For expression-bodied lambdas
            return interpreter.evaluate(self.declaration.body.value)
            
        return None
    
    def __str__(self):
        params_str = ", ".join(param.lexeme for param in self.declaration.params)
        return f"<lambda ({params_str})>"

class ThyddleArray:
    def __init__(self, elements):
        self.elements = elements
    
    def get(self, index):
        if not isinstance(index, int):
            raise ThyddleRuntimeError("Array index must be an integer.")
        
        if index < 0 or index >= len(self.elements):
            raise ThyddleRuntimeError(f"Array index out of bounds: {index}")
        
        return self.elements[index]
    
    def set(self, index, value):
        if not isinstance(index, int):
            raise ThyddleRuntimeError("Array index must be an integer.")
        
        if index < 0 or index >= len(self.elements):
            raise ThyddleRuntimeError(f"Array index out of bounds: {index}")
        
        self.elements[index] = value
    
    def __str__(self):
        elements_str = ", ".join(str(elem) for elem in self.elements)
        return f"[{elements_str}]"

class ThyddleObject:
    def __init__(self, properties):
        self.properties = properties
    
    def get(self, name):
        if name in self.properties:
            return self.properties[name]
        return None
    
    def set(self, name, value):
        self.properties[name] = value
    
    def __str__(self):
        prop_strs = []
        for key, value in self.properties.items():
            prop_strs.append(f"{key}: {value}")
        return f"{{{', '.join(prop_strs)}}}"

class Interpreter:
    def __init__(self):
        self.globals = Environment()
        self.environment = self.globals
        self.setup_stdlib()
    
    def setup_stdlib(self):
        # Define print function
        def print_fn(interpreter, arguments):
            print(*arguments)
            return None
        
        def write_fn(interpreter, arguments):
            print(*arguments, end="")
            return None
        
        # Define input function
        def input_fn(interpreter, arguments):
            prompt = arguments[0] if arguments else ""
            return input(prompt)
        
        def pyth_fn(interpreter, arguments):
            if len(arguments) != 1:
                raise ThyddleRuntimeError("pyth() takes exactly one argument.")
            
            code = arguments[0]
            if not isinstance(code, str):
                raise ThyddleRuntimeError("pyth() argument must be a string.")
            
            eval(code)
            
        def eval_fn(interpreter, arguments):
            if len(arguments) != 1:
                raise ThyddleRuntimeError("eval() takes exactly one argument.")
            
            code = arguments[0]
            if not isinstance(code, str):
                raise ThyddleRuntimeError("eval() argument must be a string.")
            
            try:
                return interpreter.interpret(code)
            except ThyddleRuntimeError as error:
                raise ThyddleRuntimeError(f"Evalulation error: {error.message}")
            
        def num_fn(interpreter, arguments):
            if len(arguments) != 1:
                raise ThyddleRuntimeError("tonum() takes exactly one argument.")
            
            value = arguments[0]
            if isinstance(value, str):
                try:
                    return int(value)
                except ValueError:
                    try:
                        return float(value)
                    except ValueError:
                        return value
            elif isinstance(value, (int, float)):
                return value
            
            raise ThyddleRuntimeError("tonum() requires a string or number.")
        
        def str_fn(interpreter, arguments):
            if len(arguments) != 1:
                raise ThyddleRuntimeError("tostr() takes exactly one argument.")
            
            value = arguments[0]
            if isinstance(value, str):
                return value
            elif isinstance(value, (int, float)):
                return str(value)
            
            raise ThyddleRuntimeError("tostr() requires a string or number.")
        
        def type_fn(interpreter, arguments):
            if len(arguments) != 1:
                raise ThyddleRuntimeError("type() takes exactly one argument.")
            
            value = arguments[0]
            if isinstance(value, str):
                return "str"
            elif isinstance(value, (int, float)):
                return "num"
            elif isinstance(value, ThyddleArray):
                return "array"
            elif isinstance(value, ThyddleObject):
                return "object"
            
            raise ThyddleRuntimeError("type() requires a string, number, array, or object.")
        
        # Define string functions
        def len_fn(interpreter, arguments):
            if len(arguments) != 1:
                raise ThyddleRuntimeError("len() takes exactly one argument.")
            
            if isinstance(arguments[0], str):
                return len(arguments[0])
            elif isinstance(arguments[0], ThyddleArray):
                return len(arguments[0].elements)
            elif isinstance(arguments[0], ThyddleObject):
                return len(arguments[0].properties)
            else:
                raise ThyddleRuntimeError("len() requires a string, array, or object.")
        
        def appnd_fn(interpreter, arguments):
            if len(arguments) != 2:
                raise ThyddleRuntimeError("append() takes exactly two arguments.")
            
            array = arguments[0]
            value = arguments[1]
            
            if not isinstance(array, ThyddleArray):
                raise ThyddleRuntimeError("First argument must be an array.")
            
            array.elements.append(value)
            return None
        
        def revrs_fn(interpreter, arguments):
            if len(arguments) != 1:
                raise ThyddleRuntimeError("reverse() takes exactly one argument.")
            
            obj = arguments[0]
            
            ret = None
            
            if isinstance(obj, ThyddleArray):
                ret = ThyddleArray(obj.elements[::-1])
            elif isinstance(obj, ThyddleObject):
                ret = ThyddleObject({k: v for k, v in reversed(obj.properties.items())})
            else:
                raise ThyddleRuntimeError("reverse() requires a array or object.")
            
            return ret
        
        def pop_fn(interpreter, arguments):
            if len(arguments) < 1 or len(arguments) > 2:
                raise ThyddleRuntimeError("pop() takes exactly one or two arguments.")
            
            array = arguments[0]
            
            if not isinstance(array, ThyddleArray):
                raise ThyddleRuntimeError("First argument must be an array.")
            
            # Default index is the last element
            index = None
            if len(arguments) == 2:
                index = arguments[1]
                if index is not None:
                    index = int(index)  # Ensure the index is an integer
                    
                    if index < 0 or index >= len(array.elements):
                        raise ThyddleRuntimeError(f"Index {index} is out of range.")
            
            # If no index is provided, pop the last element
            if index is None:
                value = array.elements.pop()
            else:
                value = array.elements.pop(index)
            
            return value

        
        def abs_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.abs() takes in a number value")
            return abs(arguments[0])

        def sqrt_root_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.sqrt() takes in a number value")
            return math.sqrt(arguments[0])

        def sin_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.sin() takes in a number value")
            return math.sin(arguments[0])

        def cos_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.cos() takes in a number value")
            return math.cos(arguments[0])

        def sinh_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.sinh() takes in a number value")
            return math.sinh(arguments[0])

        def cosh_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.cosh() takes in a number value")
            return math.cosh(arguments[0])

        def tan_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.tan() takes in a number value")
            return math.tan(arguments[0])

        def tanh_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.tanh() takes in a number value")
            return math.tanh(arguments[0])

        def asin_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.asin() takes in a number value")
            return math.asin(arguments[0])

        def acos_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.acos() takes in a number value")
            return math.acos(arguments[0])

        def asinh_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.asinh() takes in a number value")
            return math.asinh(arguments[0])

        def acosh_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.acosh() takes in a number value")
            return math.acosh(arguments[0])

        def atan_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.atan() takes in a number value")
            return math.atan(arguments[0])

        def atan2_fn(interpreter, arguments):
            if not (isinstance(arguments[0], (float, int)) and isinstance(arguments[1], (float, int))):
                raise ThyddleRuntimeError("math.atan2() takes two number values")
            return math.atan2(arguments[0], arguments[1])

        def atanh_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.atanh() takes in a number value")
            return math.atanh(arguments[0])

        def floor_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.floor() takes in a number value")
            return math.floor(arguments[0])

        def ceil_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.ceil() takes in a number value")
            return math.ceil(arguments[0])

        def rad_fn(interpreter, arguments):
            if not isinstance(arguments[0], (float, int)):
                raise ThyddleRuntimeError("math.rad() takes in a number value")
            return math.radians(arguments[0])

        def pow_fn(interpreter, arguments):
            if not (isinstance(arguments[0], (float, int)) and isinstance(arguments[1], (float, int))):
                raise ThyddleRuntimeError("math.pow() takes two number values")
            return math.pow(arguments[0], arguments[1])
        
        def uniform_fn(interpreter, arguments):
            if not (isinstance(arguments[0], (float, int)) and isinstance(arguments[1], (float, int))):
                raise ThyddleRuntimeError("math.uniform() takes two number values")
            return random.uniform(arguments[0], arguments[1])
        
        def randint_fn(interpreter, arguments):
            if not (isinstance(arguments[0], (int)) and isinstance(arguments[1], (int))):
                raise ThyddleRuntimeError("math.uniform() takes two integer values")
            return random.randint(arguments[0], arguments[1])
        
        def read_file_fn(interpreter, arguments):
            if not isinstance(arguments[0], str):
                raise ThyddleRuntimeError("file.read() expects a string filename")
            try:
                with open(arguments[0], 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                raise ThyddleRuntimeError(f"file.read() error: {e}")
            
        def write_file_fn(interpreter, arguments):
            if not (isinstance(arguments[0], str) and isinstance(arguments[1], str)):
                raise ThyddleRuntimeError("file.write() expects a filename and string content")
            try:
                with open(arguments[0], 'w', encoding='utf-8') as f:
                    f.write(arguments[1])
                return None  # or maybe return True?
            except Exception as e:
                raise ThyddleRuntimeError(f"file.write() error: {e}")
            
        def append_file_fn(interpreter, arguments):
            if not (isinstance(arguments[0], str) and isinstance(arguments[1], str)):
                raise ThyddleRuntimeError("file.append() expects a filename and string content")
            try:
                with open(arguments[0], 'a', encoding='utf-8') as f:
                    f.write(arguments[1])
                return None
            except Exception as e:
                raise ThyddleRuntimeError(f"file.append() error: {e}")
            
        def string_split_fn(interpreter, arguments):
            if not (isinstance(arguments[0], str) and isinstance(arguments[1], str)):
                raise ThyddleRuntimeError("string.split() expects a string and a separator string")
            
            text = arguments[0]
            sep = arguments[1]
            
            # First split by newline
            parts = []
            for line in text.splitlines():
                # Then split each line by the separator
                parts.extend(line.split(sep))
            
            return parts

        
        self.globals.define("len", NativeFunction("len", len_fn))
        self.globals.define("pyth", NativeFunction("pyth", pyth_fn))
        self.globals.define("eval", NativeFunction("eval", eval_fn))
        self.globals.define("tonum", NativeFunction("tonum", num_fn))
        self.globals.define("tostr", NativeFunction("tostr", str_fn))
        self.globals.define("type", NativeFunction("type", type_fn))
        self.globals.define("reverse", NativeFunction("reverse", revrs_fn))
        self.globals.define("split", NativeFunction("split", string_split_fn))
        self.globals.define("ord", NativeFunction("ord", lambda interpreter, args: ord(args[0])))
        self.globals.define("chr", NativeFunction("chr", lambda interpreter, args: chr(args[0])))
        self.globals.define("array", ThyddleObject({
            "append": NativeFunction("append", appnd_fn),
            "pop": NativeFunction("pop", pop_fn)
        }))
        self.globals.define("console", ThyddleObject({
            "output": ThyddleObject({
                "println": NativeFunction("println", print_fn),
                "print": NativeFunction("print", write_fn)
            }),
            "read": NativeFunction("input", input_fn)
        }))
        self.globals.define("math", ThyddleObject({
            "abs": NativeFunction("abs", abs_fn),
            "sqrt": NativeFunction("sqrt", sqrt_root_fn),
            "sin": NativeFunction("sin", sin_fn),
            "cos": NativeFunction("cos", cos_fn),
            "sinh": NativeFunction("sinh", sinh_fn),
            "cosh": NativeFunction("cosh", cosh_fn),
            "tan": NativeFunction("tan", tan_fn),
            "tanh": NativeFunction("tanh", tanh_fn),
            "asin": NativeFunction("asin", asin_fn),
            "acos": NativeFunction("acos", acos_fn),
            "asinh": NativeFunction("asinh", asinh_fn),
            "acosh": NativeFunction("acosh", acosh_fn),
            "atan": NativeFunction("atan", atan_fn),
            "atan2": NativeFunction("atan2", atan2_fn),
            "atanh": NativeFunction("atanh", atanh_fn),
            "floor": NativeFunction("floor", floor_fn),
            "ceil": NativeFunction("ceil", ceil_fn),
            "rad": NativeFunction("rad", rad_fn),
            "pow": NativeFunction("pow", pow_fn),
            "random": ThyddleObject({
                "randint": NativeFunction("randint", randint_fn),
                "uniform": NativeFunction("uniform", uniform_fn)
            })
        }))
        
        self.globals.define("io", ThyddleObject({
            "file": ThyddleObject({
                "modify": ThyddleObject({
                    "append": NativeFunction("append", append_file_fn),
                    "write": NativeFunction("write", write_file_fn)
                }),
                "read": NativeFunction("read", read_file_fn)
            })
        }))
        self.globals.define("true", True)
        self.globals.define("false", False)
        self.globals.define("nothing", None)
    
    def interpret(self, code):
        lexer = Lexer(code)
        tokens = lexer.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()
        interpreter = Interpreter()
        try:
            ret = None
            for statement in statements:
                ret = interpreter.execute(statement)
            return ret
        except ThyddleRuntimeError as error:
            print(f"Runtime Error: {error.message}")
            return False
    
    def execute(self, stmt):
        if isinstance(stmt, ExpressionStatement):
            return self.evaluate(stmt.expression)
        
        elif isinstance(stmt, VarStatement):
            value = None
            if stmt.initializer is not None:
                value = self.evaluate(stmt.initializer)
            
            if callable(value):
                self.environment.define(stmt.name.lexeme, value, stmt.is_const)
            else:
                self.environment.define(stmt.name.lexeme, value, stmt.is_const)
            
            return value  # ← return the variable's value
        
        elif isinstance(stmt, BlockStatement):
            return self.execute_block(stmt.statements, Environment(self.environment))
        
        elif isinstance(stmt, IfStatement):
            if self.is_truthy(self.evaluate(stmt.condition)):
                return self.execute(stmt.then_branch)
            else:
                executed = False
                for condition, branch in stmt.else_if_branches:
                    if self.is_truthy(self.evaluate(condition)):
                        executed = True
                        return self.execute(branch)
                if not executed and stmt.else_branch is not None:
                    return self.execute(stmt.else_branch)
            return None  # if no branch runs
        
        elif isinstance(stmt, WhileStatement):
            result = None
            while self.is_truthy(self.evaluate(stmt.condition)):
                try:
                    result = self.execute(stmt.body)
                except BreakException:
                    break
                except ContinueException:
                    continue
            return result
        
        elif isinstance(stmt, ForStatement):
            previous_env = self.environment
            result = None
            try:
                self.environment = Environment(self.environment)
                if stmt.initializer is not None:
                    self.execute(stmt.initializer)
                while True:
                    if stmt.condition is not None:
                        if not self.is_truthy(self.evaluate(stmt.condition)):
                            break
                    try:
                        result = self.execute(stmt.body)
                    except BreakException:
                        break
                    except ContinueException:
                        pass
                    if stmt.increment is not None:
                        self.evaluate(stmt.increment)
            finally:
                self.environment = previous_env
            return result
        
        elif isinstance(stmt, FunctionStatement):
            function = ThyddleFunction(stmt, self.environment)
            self.environment.define(stmt.name.lexeme, function)
            return function  # ← returning the function object
        
        elif isinstance(stmt, ReturnStatement):
            value = None
            if stmt.value is not None:
                value = self.evaluate(stmt.value)
            raise ReturnValue(value)
        
        elif isinstance(stmt, BreakStatement):
            raise BreakException()
        
        elif isinstance(stmt, ContinueStatement):
            raise ContinueException()
        
        elif isinstance(stmt, ImportStatement):
            return self.handle_import(stmt.module_name)
        
        return None  # fallback if nothing matches

    
    def handle_import(self, module_name):
        """
        Imports functions and constants (variables with is_const=True) from a module,
        without executing other statements.
        """
        try:
            with open(module_name + ".thy", "r") as f:  # Assumes the module ends with .thy
                module_code = f.read()
                
                # Lex + parse
                lexer = Lexer(module_code)
                tokens = lexer.scan_tokens()
                parser = Parser(tokens)
                statements = parser.parse()
                
                # Module environment (inherits global variables)
                module_env = Environment(self.globals)
                
                # Declare functions and constants
                for stmt in statements:
                    if isinstance(stmt, FunctionStatement):
                        # If the statement is a function definition
                        function = ThyddleFunction(stmt, module_env)
                        module_env.define(stmt.name.lexeme, function)
                    elif isinstance(stmt, VarStatement):
                        # If the statement is a variable declaration (constant or not)
                        is_const = stmt.is_const  # Get if it's marked as a constant
                        if is_const:
                            # If it's a constant, define it as such
                            value = self.evaluate(stmt.initializer)  # Evaluate the initializer
                            module_env.define(stmt.name.lexeme, value, is_const=True)
                
                # Expose functions and constants to the current environment
                for name, value in module_env.values.items():
                    if isinstance(value, ThyddleFunction):
                        # Import function to the global environment
                        self.environment.define(name, value)
                    else:
                        # Import constants (or other values)
                        self.environment.define(name, value)
                
                return True
                                    
        except FileNotFoundError:
            raise ThyddleRuntimeError(f"Could not find module '{module_name}'.")


    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous
    
    def evaluate(self, expr):
        if isinstance(expr, Literal):
            return expr.value
        elif isinstance(expr, Grouping):
            return self.evaluate(expr.expression)
        elif isinstance(expr, LambdaExpression):
            return ThyddleLambda(expr, self.environment)
        elif isinstance(expr, Unary):
            right = self.evaluate(expr.right)
            
            if expr.operator.type == TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -right
            elif expr.operator.type == TokenType.BANG:
                return not self.is_truthy(right)
        elif isinstance(expr, Binary):
            left = self.evaluate(expr.left)
            right = self.evaluate(expr.right)
            
            if expr.operator.type == TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return left - right
            elif expr.operator.type == TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise ThyddleRuntimeError("Division by zero.")
                return left / right
            elif expr.operator.type == TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            elif expr.operator.type == TokenType.PLUS:
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                raise ThyddleRuntimeError("Operands must be numbers or strings.")
            elif expr.operator.type == TokenType.MODULO:
                self.check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise ThyddleRuntimeError("Modulo by zero.")
                return left % right
            elif expr.operator.type == TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            elif expr.operator.type == TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            elif expr.operator.type == TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            elif expr.operator.type == TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right
            elif expr.operator.type == TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            elif expr.operator.type == TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
        elif isinstance(expr, Variable):
            return self.environment.get(expr.name.lexeme)
        elif isinstance(expr, Assign):
            value = self.evaluate(expr.value)
            self.environment.assign(expr.name.lexeme, value)
            return value
        elif isinstance(expr, Logical):
            left = self.evaluate(expr.left)
            
            if expr.operator.type == TokenType.OR:
                if self.is_truthy(left):
                    return left
            else:  # AND
                if not self.is_truthy(left):
                    return left
            
            return self.evaluate(expr.right)
        elif isinstance(expr, Call):
            # Evaluate the callee properly
            callee = expr.callee
            callee = self.evaluate(callee)
            # If the callee is a variable, get its value (which should be a function or callable)
            if isinstance(callee, Variable):
                callee_value = self.evaluate(self.environment.get(callee.name.lexeme))  # Get the value of the variable
                
                # Check if it's a callable function
                
                if not isinstance(callee_value, (ThyddleFunction, NativeFunction)):
                    raise ThyddleRuntimeError(f"Variable '{callee.name.lexeme}' is not a callable function.")
                
                callee = callee_value  # Now we have the callable function
            
            # If it's not a variable, evaluate it as an expression
            
            
            #print(type(self.evaluate(callee)), self.evaluate(expr.callee))
            
            # Evaluate arguments
            arguments = [self.evaluate(arg) for arg in expr.arguments]

            # Check if callee is a function and call it
            if isinstance(callee, (ThyddleFunction, NativeFunction)):
                return callee.call(self, arguments)

            raise ThyddleRuntimeError("Can only call functions or variables that hold functions.")


        elif isinstance(expr, Get):
            obj = self.evaluate(expr.obj)
            
            if isinstance(obj, ThyddleObject):
                return obj.get(expr.name.lexeme)
            
            raise ThyddleRuntimeError("Only objects have properties.")
        elif isinstance(expr, Set):
            obj = self.evaluate(expr.obj)
            
            if not isinstance(obj, ThyddleObject):
                raise ThyddleRuntimeError("Only objects have properties.")
            
            value = self.evaluate(expr.value)
            obj.set(expr.name.lexeme, value)
            return value
        elif isinstance(expr, Index):
            obj = self.evaluate(expr.obj)
            index = self.evaluate(expr.index)
            
            if isinstance(obj, ThyddleArray):
                return obj.get(index)
            elif isinstance(obj, str):
                if not isinstance(index, int):
                    raise ThyddleRuntimeError("String index must be an integer.")
                
                if index < 0 or index >= len(obj):
                    raise ThyddleRuntimeError(f"String index out of bounds: {index}")
                
                return obj[index]
            elif isinstance(obj, ThyddleObject):
                if not isinstance(index, str):
                    raise ThyddleRuntimeError("Object index must be a string key.")
                return obj.get(index)
            else:
                raise ThyddleRuntimeError("Only arrays, strings, and objects can be indexed.")

        elif isinstance(expr, SetIndex):
            obj = self.evaluate(expr.obj)
            index = self.evaluate(expr.index)
            value = self.evaluate(expr.value)
            
            if isinstance(obj, ThyddleArray):
                obj.set(index, value)
                return value
            elif isinstance(obj, ThyddleObject):
                if not isinstance(index, str):
                    raise ThyddleRuntimeError("Object index must be a string key.")
                obj.set(index, value)
                return value
            
            raise ThyddleRuntimeError("Only arrays and objects support indexed assignment.")
        elif isinstance(expr, ArrayLiteral):
            elements = []
            for element in expr.elements:
                elements.append(self.evaluate(element))
            
            return ThyddleArray(elements)
        elif isinstance(expr, ObjectLiteral):
            properties = {}
            for key, value in expr.properties:
                properties[key.lexeme] = self.evaluate(value)
            
            return ThyddleObject(properties)
        
        return None
    
    def is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        return True
    
    def is_equal(self, a, b):
        if a is None and b is None:
            return True
        if a is None:
            return False
        
        return a == b
    
    def check_number_operand(self, operator, operand):
        if isinstance(operand, (int, float)):
            return
        raise ThyddleRuntimeError("Operand must be a number.")
    
    def check_number_operands(self, operator, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return
        raise ThyddleRuntimeError("Operands must be numbers.")

class NativeFunction:
    def __init__(self, name, function):
        self.name = name
        self.function = function
    
    def call(self, interpreter, arguments):
        # Call the function when it's treated like a callable object
        return self.function(interpreter, arguments)
    
    def __str__(self):
        return f"<native fn {self.name}>"

