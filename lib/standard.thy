// lib/standard

const println = console.output.println;
const print = console.output.print;
const input = console.read;

const arr = {
    combine: (a, sep) -> {
        var ret = "";
        var indx = 0;

        while (indx < len(a)) {
            ret = ret + a[indx] + tostr(sep);
            indx = indx + 1;
        }

        return ret;
    },
    map: (a, fn) -> {
        var ret = [];
        var indx = 0;

        while (indx < len(a)) {
            array.append(ret, fn(a[indx], indx));
            indx = indx + 1;
        }

        return ret;
    }
};

const string = {
    split: (text) -> {
        var ret = [];
        var indx = 0;

        while (indx < len(text)) {
            array.append(ret, text[indx]);
            indx = indx + 1;
        }

        return ret;
    },
    reverse: (text) -> {
        var ret = string.split(text);
        ret = reverse(ret);
        ret = arr.combine(ret, "");

        return ret;
    }
};