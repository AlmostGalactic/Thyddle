import "lib/standard";
import "lib/fileio";

var name = input("What is your name? ");
var age = input("How old are you? ");

var text = [
    "var NAME = " + '"' + name + '"' + ";",
    "var AGE = " + age + ";",
    "\n"
];

fileio.write("DATA.thy", multi_line(text));

var extra = [
    "console.output.println('Hello, ' + NAME + '!');\n",
    "if (AGE < 13) {",
    "\tconsole.output.println('You are young!');",
    "} else {",
    "\tconsole.output.println('Nice!');",
    "}"
];

fileio.append("DATA.thy", multi_line(extra));