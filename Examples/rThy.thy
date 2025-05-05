import "lib/standard";

func repl() {
    var running = true;

    while (running) {
        var in = console.read(">> ");
        var spl = string.split(in);

        if (in == "exit()") {
            break;
        } else {
            var rev = string.reverse(arr.combine(spl, ""));

            eval(rev);
        }
    }
}

repl();