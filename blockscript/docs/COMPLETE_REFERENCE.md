# BlockScript Complete Reference

The complete guide to BlockScript programming language.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Language Syntax](#language-syntax)
4. [Standard Library](#standard-library)
5. [Advanced Features](#advanced-features)
6. [Tools and Utilities](#tools-and-utilities)
7. [Best Practices](#best-practices)

## Introduction

BlockScript is a full-featured, text-based programming language inspired by Scratch. It combines beginner-friendly syntax with professional-grade tools.

## Installation

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd blockscript

# Run a program
node cli/blockscript.js examples/hello.bs

# Start the REPL
node src/repl.js

# Open the IDE
open ide/index.html
```

## Language Syntax

### Complete Syntax Guide

#### Variables
```blockscript
set name to "Alice"       # Create/update variable
change score by 10        # Modify by amount
change lives by -1        # Decrease
```

#### Data Types
- **Numbers**: `42`, `3.14`, `-10`
- **Strings**: `"hello"`, `'world'`
- **Booleans**: `true`, `false`
- **Lists**: `[1, 2, 3]`

#### Operators

**Arithmetic:**
- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `mod` Modulo
- `^` Power

**Comparison:**
- `=` Equal
- `!=` Not equal
- `>` Greater than
- `<` Less than
- `>=` Greater or equal
- `<=` Less or equal

**Logical:**
- `and` Logical AND
- `or` Logical OR
- `not` Logical NOT

#### Control Flow

**If Statement:**
```blockscript
if condition then
  # code
else
  # code
end
```

**Loops:**
```blockscript
repeat 10 times
  # code
end

forever
  # code
end

while condition then
  # code
end

for i from 1 to 10
  # code
end
```

#### Lists

```blockscript
create list items
add "apple" to items
set item 1 of items to "orange"
delete item 2 of items
print item 1 of items
print length of items
```

#### Functions

```blockscript
define greet with name
  say join "Hello, " and name
end

call greet with "Alice"

define add with a, b
  return a + b
end

set sum to (call add with 5, 10)
```

## Standard Library

BlockScript includes a comprehensive standard library with 100+ functions.

### Math

```blockscript
random from 1 to 10      # Random number
abs of -5                # Absolute value
round 3.7                # Round number
floor 3.7                # Round down
ceil 3.2                 # Round up
sqrt of 16               # Square root
sin of angle             # Sine
cos of angle             # Cosine
tan of angle             # Tangent
```

### String

```blockscript
join "Hello" and " World"        # Concatenate
length of "Hello"                 # String length
letter 1 of "Hello"              # Get character
uppercase "hello"                # Convert to uppercase
lowercase "HELLO"                # Convert to lowercase
trim "  text  "                  # Remove whitespace
```

### List

```blockscript
length of list           # List length
reverse list             # Reverse list
sort list               # Sort numbers
shuffle list            # Randomize order
contains item in list   # Check if contains
```

### Type Checking

```blockscript
isNumber value          # Check if number
isString value          # Check if string
isList value            # Check if list
isBoolean value         # Check if boolean
```

### Date/Time

```blockscript
now                     # Current timestamp
year                    # Current year
month                   # Current month
day                     # Current day
hour                    # Current hour
minute                  # Current minute
second                  # Current second
```

## Advanced Features

### Module System

```blockscript
import "math.bs" as math
import functions from "utils.bs"

export myFunction
export myVariable
```

### File I/O

```blockscript
read file "data.txt"
write file "output.txt" with content
append to file "log.txt" with message
delete file "temp.txt"
```

### HTTP/Networking

```blockscript
get url "https://api.example.com/data"
post url "https://api.example.com" with data
download file from "https://example.com/file.pdf"
```

### Graphics and Canvas

```blockscript
create canvas with width 800, height 600
clear canvas
draw circle at 400, 300 with radius 50
draw rectangle at 100, 100 with width 200, height 100
fill color "red"
pen color "blue"
pen size 2
```

### Events

```blockscript
when program starts
  say "Starting!"
end

when space key pressed
  say "Space was pressed!"
end

when timer > 10
  say "10 seconds elapsed"
end
```

## Tools and Utilities

### REPL (Read-Eval-Print Loop)

Interactive programming environment:

```bash
node src/repl.js
```

Commands:
- `.help` - Show help
- `.vars` - Show variables
- `.history` - Show command history
- `.clear` - Clear screen
- `.exit` - Exit REPL

### Linter

Check code quality:

```bash
node cli/blockscript.js lint program.bs
```

Detects:
- Undefined variables
- Division by zero
- Empty blocks
- Unused code
- Style issues

### Formatter

Auto-format code:

```bash
node cli/blockscript.js format program.bs
```

Features:
- Consistent indentation
- Line length limits
- Trailing whitespace removal
- Import sorting

### Transpiler

Convert to JavaScript:

```bash
node cli/blockscript.js transpile program.bs
```

Output formats:
- ES6 modules
- CommonJS
- Standalone scripts

### Debugger

Step-through debugging:

```blockscript
# Set breakpoint at line 10
debug breakpoint 10

# Step through code
debug step

# Inspect variables
debug watch variableName
```

### Performance Profiler

Analyze performance:

```bash
node cli/blockscript.js profile program.bs
```

Shows:
- Execution time
- Hot spots
- Function call counts
- Memory usage

## Best Practices

### Code Style

1. **Use descriptive names**
```blockscript
# Good
set playerScore to 100

# Bad
set x to 100
```

2. **Add comments**
```blockscript
# Calculate compound interest
set amount to principal * (1 + rate) ^ time
```

3. **Keep functions small**
```blockscript
# Each function should do one thing
define calculateTax with amount
  return amount * 0.15
end
```

4. **Use consistent indentation**
```blockscript
if condition then
  say "True"
  if nested then
    say "Nested"
  end
end
```

### Performance

1. **Avoid infinite loops**
```blockscript
# Always have an exit condition
set count to 0
while count < 100 then
  change count by 1
end
```

2. **Reuse calculations**
```blockscript
# Good
set len to (length of list)
for i from 1 to len

# Bad
for i from 1 to (length of list)  # Recalculates each iteration
```

3. **Use appropriate data structures**
```blockscript
# Use lists for collections
create list items

# Not multiple variables
set item1 to "a"
set item2 to "b"
```

### Security

1. **Validate input**
```blockscript
ask "Enter age:"
set age to answer

if (age < 0) or (age > 150) then
  say "Invalid age!"
end
```

2. **Limit file access**
```blockscript
# Restrict to specific directories
set allowedPath to "/safe/directory/"
```

3. **Sanitize data**
```blockscript
# Clean user input before using
set clean to (trim userInput)
```

## Error Handling

### Common Errors

1. **Undefined Variable**
```blockscript
print x  # Error: x not defined

# Fix:
set x to 10
print x
```

2. **Division by Zero**
```blockscript
set result to 10 / 0  # Error

# Fix:
if divisor != 0 then
  set result to 10 / divisor
end
```

3. **Index Out of Bounds**
```blockscript
create list items
print item 5 of items  # Error: list is empty

# Fix:
if (length of items) >= 5 then
  print item 5 of items
end
```

## Examples Index

BlockScript includes 50+ example programs:

### Beginner
- hello.bs - Hello World
- calculator.bs - Simple calculator
- fibonacci.bs - Fibonacci sequence
- prime.bs - Prime numbers
- sorting.bs - Bubble sort

### Intermediate
- tic-tac-toe.bs - Game
- hangman.bs - Word game
- todo-list.bs - Task manager
- password-generator.bs - Security
- blackjack.bs - Card game

### Advanced
- text-adventure.bs - Interactive fiction
- maze-generator.bs - Procedural generation
- snake-game.bs - Classic game
- contact-manager.bs - Database operations

## Resources

- [Tutorial 1: Basics](TUTORIAL_01_BASICS.md)
- [Tutorial 2: Control Flow](TUTORIAL_02_CONTROL_FLOW.md)
- [Tutorial 3: Lists](TUTORIAL_03_LISTS.md)
- [Tutorial 4: Functions](TUTORIAL_04_FUNCTIONS.md)
- [Language Specification](LANGUAGE_SPEC.md)
- [Getting Started Guide](GETTING_STARTED.md)

## Community

- Report bugs on GitHub Issues
- Share your programs
- Contribute examples
- Improve documentation

---

**BlockScript** - Making programming accessible to everyone! 🚀
