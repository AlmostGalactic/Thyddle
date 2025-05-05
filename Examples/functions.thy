func person(name, age) {
    return {
        name: name,
        age: age,
        greet: (person2) -> {
            console.output.println("Hey, "+person2.name+"!");
        }
    };
}

var person1 = person("John", 12);
var person2 = person("Peter", 13);
person1.greet(person2);
person2.greet(person1);