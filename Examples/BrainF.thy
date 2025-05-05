import "lib/standard";

func brainf(code) {
    var tape = [];
    var i = 0;

    // Initialize tape with 30000 zeros
    while (i < 30000) {
        array.append(tape, 0);
        i = i + 1;
    }

    var ptr = 0;
    var indx = 0;

    while (indx < len(code)) {
        var cmd = code[indx];

        if (cmd == ">") {
            ptr = ptr + 1;
        } elseif (cmd == "<") {
            ptr = ptr - 1;
        } elseif (cmd == "+") {
            tape[ptr] = (tape[ptr] + 1) % 256;
        } elseif (cmd == "-") {
            tape[ptr] = (tape[ptr] - 1) % 256;
        } elseif (cmd == ".") {
            print(chr(tape[ptr]));
        } elseif (cmd == ",") {
            var inp = input("");
            if (len(inp) > 0) {
                tape[ptr] = ord(inp[0]);
            }
        } elseif (cmd == "[") {
            if (tape[ptr] == 0) {
                var loop = 1;
                while (loop > 0) {
                    indx = indx + 1;
                    if (code[indx] == "[") {
                        loop = loop + 1;
                    } elseif (code[indx] == "]") {
                        loop = loop - 1;
                    }
                }
            }
        } elseif (cmd == "]") {
            if (tape[ptr] != 0) {
                var loop = 1;
                while (loop > 0) {
                    indx = indx - 1;
                    if (code[indx] == "]") {
                        loop = loop + 1;
                    } elseif (code[indx] == "[") {
                        loop = loop - 1;
                    }
                }
            }
        }

        indx = indx + 1;
    }
}

var program = input("Enter BrainF code: ");
brainf(program);
