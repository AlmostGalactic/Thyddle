import "lib/standard";

println("THYDDLE REPL v3");
println("enter 'exit()' to quit");

while (true) {
    var in = input(">> ");
    

    if (in == "exit()") {
        break;
    }
    var ret = eval(in);

    if (ret != nothing) {
        println(ret);
    } else {
        //Do nothing
    }

}

println("Bye!");
