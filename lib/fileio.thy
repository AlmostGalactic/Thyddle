// lib/fileio

const fileio = {
    write: io.file.modify.write,
    append: io.file.modify.append,

    read: io.file.read
};

func multi_line(lines) {
    // this takes in an array and returns a string with newlines
    var final = "";
    var indx = 0;

    if (type(lines) == "array") {
        while (indx < len(lines)) {
            if (indx == (len(lines)-1)) {
                final = final + lines[indx];
            } else {
                final = final + lines[indx] + "\n";
            }

            indx = indx + 1;
        }
        return final;
    }
    return false;
}