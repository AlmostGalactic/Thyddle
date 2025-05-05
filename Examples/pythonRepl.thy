func repl() {
    var running = true;

    while (running) {
        var in = console.read(">> ");

        if (in == "exit()") {
            break;
        } else {
            pyth(in);
        }
    }
}

repl();