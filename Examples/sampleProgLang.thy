import "lib/standard";

var commands = [];
var code = [];
var variables = {};

func eval_command(arg) {
    func add_command(cmd) {
        if (type(cmd) == "array" and cmd[0] == "arg") {
            array.append(commands, tostr(cmd[1]));
        } else {
            array.append(commands, tostr(cmd));
        }
    }

    if (arg == "Print") {
        array.append(commands, arg);
        var argu = eval_command(input(arr.combine(commands, " ") + ": "));
        return ["print", argu];
    } elseif (arg == "Input") {
        array.append(commands, arg);
        var prompt = eval_command(input(arr.combine(commands, " ") + ": "));
        return ["in", prompt];
    } elseif (arg == "Add") {
        add_command(arg);
        var left = eval_command(input(arr.combine(commands, " ") + ": "));
        add_command(left);
        var right = eval_command(input(arr.combine(commands, " ") + ": "));
        return ["add", left, right];
    } elseif (arg == "Subtract") {
        add_command(arg);
        var left = eval_command(input(arr.combine(commands, " ") + ": "));
        add_command(left);
        var right = eval_command(input(arr.combine(commands, " ") + ": "));
        return ["sub", left, right];
    } elseif (arg == "Multiply") {
        add_command(arg);
        var left = eval_command(input(arr.combine(commands, " ") + ": "));
        add_command(left);
        var right = eval_command(input(arr.combine(commands, " ") + ": "));
        return ["mul", left, right];
    } elseif (arg == "Divide") {
        add_command(arg);
        var left = eval_command(input(arr.combine(commands, " ") + ": "));
        add_command(left);
        var right = eval_command(input(arr.combine(commands, " ") + ": "));
        return ["div", left, right];
    } elseif (arg == "Declare Variable") {
        array.append(commands, arg);
        var name = ["arg", input(arr.combine(commands, " ") + ": ")];
        add_command(name);
        var val = eval_command(input(arr.combine(commands, " ") + ": "));
        return ["dec", name, val];
    } else {
        var val = tonum(arg);
        if (type(val) == "num") {
            return ["arg", val];
        } else {
            return ["arg", arg];
        }
    }
}

func eval_code(code_piece) {
    if (code_piece[0] == "print") {
        var out = eval_code(code_piece[1]);
        println(out);
        return nothing;
    } elseif (code_piece[0] == "in") {
        var prompt = eval_code(code_piece[1]);
        return input(prompt);
    } elseif (code_piece[0] == "add") {
        var left = eval_code(code_piece[1]);
        var right = eval_code(code_piece[2]);
        return left + right;
    } elseif (code_piece[0] == "sub") {
        var left = eval_code(code_piece[1]);
        var right = eval_code(code_piece[2]);
        return left - right;
    } elseif (code_piece[0] == "mul") {
        var left = eval_code(code_piece[1]);
        var right = eval_code(code_piece[2]);
        return left * right;
    } elseif (code_piece[0] == "div") {
        var left = eval_code(code_piece[1]);
        var right = eval_code(code_piece[2]);
        return left / right;
    } elseif (code_piece[0] == "dec") {
        var var_name = eval_code(code_piece[1]);
        var var_value = eval_code(code_piece[2]);
        variables[var_name] = var_value;
        return nothing;
    } elseif (code_piece[0] == "arg") {
        if (type(code_piece[1]) == "str") {
            if (variables[code_piece[1]] != nothing) {
                return variables[code_piece[1]];
            } else {
                return code_piece[1];
            }
        } else {
            return code_piece[1];
        }
    }
}

func run_code() {
    var indx = 0;
    while (indx < len(code)) {
        eval_code(code[indx]);
        indx = indx + 1;
    }
}

func run() {
    var running = true;
    while (running) {
        var inp = input(arr.combine(commands, " ") + ": ");
        if (inp == "run") {
            running = false;
        } else {
            array.append(code, eval_command(inp));
            commands = [];
        }
    }

    println("\nOUTPUT:\n");
    run_code();
}

run();
