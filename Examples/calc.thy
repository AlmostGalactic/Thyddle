import "lib/standard";

while (true) {
    var in = input("TCI: ");

    if (in == "quit") {
        break;
    }

    println(eval(in + ";"));
}

println("Thanks!");