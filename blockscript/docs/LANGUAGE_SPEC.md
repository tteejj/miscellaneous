# BlockScript Language Specification

BlockScript is a text-based programming language inspired by Scratch, designed for beginners.

## Syntax Overview

### Variables
```
set myVar to 10
change myVar by 5
set name to "Alice"
```

### Output
```
say "Hello World"
print myVar
```

### Input
```
ask "What's your name?"
set name to answer
```

### Control Flow

**If Statements:**
```
if myVar > 5 then
  say "Big number!"
end

if age >= 18 then
  say "Adult"
else
  say "Minor"
end
```

**Loops:**
```
repeat 10 times
  say "Hello"
end

forever
  change x by 1
end

while x < 100 then
  change x by 1
end

for i from 1 to 10
  print i
end
```

### Math Operations
```
set result to 10 + 5
set result to (10 + 5) * 2
set result to x / y
set result to x mod 10
```

Operators: `+`, `-`, `*`, `/`, `mod`, `^` (power)

### Comparison & Logic
```
if x > 5 then
if x < 5 then
if x = 5 then
if x >= 5 then
if x <= 5 then
if x != 5 then

if (x > 5) and (y < 10) then
if (x > 5) or (y < 10) then
if not (x > 5) then
```

### Lists
```
create list fruits
add "apple" to fruits
add "banana" to fruits
set item 1 of fruits to "orange"
delete item 2 of fruits
print item 1 of fruits
print length of fruits
```

### Functions
```
define greet with name
  say join "Hello, " and name
end

call greet with "Alice"

define add with a, b
  return a + b
end

set sum to (call add with 5, 10)
```

### String Operations
```
set message to join "Hello " and "World"
set length to length of "Hello"
set letter to letter 1 of "Hello"
```

### Events
```
when program starts
  say "Starting!"
end

when space key pressed
  say "Space pressed!"
end

when timer > 10
  say "10 seconds elapsed"
end
```

### Comments
```
# This is a comment
say "Hello"  # Inline comment
```

## Built-in Variables
- `answer` - stores the last input from `ask`
- `timer` - elapsed time since program start
- `mouse_x`, `mouse_y` - mouse position (in IDE)
- `key_pressed` - last key pressed

## Data Types
- Numbers: `42`, `3.14`, `-10`
- Strings: `"hello"`, `"world"`
- Booleans: `true`, `false`
- Lists: `[1, 2, 3]`

## Standard Library Functions
- `random from a to b` - random number
- `abs of x` - absolute value
- `round x` - round number
- `sqrt of x` - square root
- `sin of x`, `cos of x`, `tan of x` - trigonometry
