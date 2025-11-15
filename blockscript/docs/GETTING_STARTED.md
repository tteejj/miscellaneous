# Getting Started with BlockScript

Welcome to BlockScript! This guide will help you write your first programs.

## Table of Contents

1. [Installation](#installation)
2. [Your First Program](#your-first-program)
3. [Basic Concepts](#basic-concepts)
4. [Common Patterns](#common-patterns)
5. [Next Steps](#next-steps)

## Installation

### Using the Web IDE (Easiest)

1. Navigate to the `blockscript/ide/` directory
2. Open `index.html` in your web browser
3. Start coding!

No installation required!

### Using the CLI

1. Ensure you have Node.js installed (v14 or higher)
2. Navigate to the `blockscript/` directory
3. Run programs with:

```bash
node cli/blockscript.js examples/hello.bs
```

## Your First Program

Let's create a simple greeting program:

```blockscript
# My First Program
say "Hello, World!"
say "Welcome to BlockScript!"

ask "What's your name?"
set name to answer

say join "Nice to meet you, " and join name and "!"
```

### What's happening?

1. `say` displays a message (like a speech bubble in Scratch)
2. `ask` prompts the user for input
3. `set name to answer` stores the input in a variable
4. `join` combines strings together

## Basic Concepts

### 1. Variables

Variables store values for later use:

```blockscript
# Create a variable
set score to 0

# Change its value
set score to 100

# Modify by an amount
change score by 10
```

### 2. Output

Two ways to show output:

```blockscript
say "This is like a speech bubble"
print "This is plain text"
```

### 3. Input

Get user input:

```blockscript
ask "How old are you?"
set age to answer
print age
```

### 4. Math

Perform calculations:

```blockscript
set x to 10
set y to 5

set sum to x + y          # Addition: 15
set diff to x - y         # Subtraction: 5
set product to x * y      # Multiplication: 50
set quotient to x / y     # Division: 2
set remainder to x mod y  # Modulo: 0
set power to 2 ^ 3        # Power: 8
```

### 5. Comparisons

Compare values:

```blockscript
if x > 5 then
  say "x is greater than 5"
end

if y = 10 then
  say "y equals 10"
end

if x != y then
  say "x and y are different"
end
```

Available operators:
- `=` equal
- `!=` not equal
- `>` greater than
- `<` less than
- `>=` greater than or equal
- `<=` less than or equal

### 6. Logic

Combine conditions:

```blockscript
if (age >= 13) and (age < 20) then
  say "You're a teenager!"
end

if (day = "Saturday") or (day = "Sunday") then
  say "It's the weekend!"
end

if not (raining) then
  say "Let's go outside!"
end
```

## Common Patterns

### Counting

```blockscript
set count to 0

repeat 10 times
  change count by 1
  print count
end
```

### Countdown

```blockscript
set timer to 10

while timer > 0 then
  print timer
  change timer by -1
end

say "Blast off!"
```

### Sum Numbers

```blockscript
set sum to 0

for i from 1 to 100
  change sum by i
end

say join "Sum: " and sum
```

### Find Maximum

```blockscript
create list numbers
add 5 to numbers
add 12 to numbers
add 8 to numbers
add 23 to numbers
add 3 to numbers

set max to (item 1 of numbers)

for i from 2 to (length of numbers)
  set current to (item i of numbers)
  if current > max then
    set max to current
  end
end

say join "Maximum: " and max
```

### Simple Game

```blockscript
say "Guess the number game!"

set secret to (random from 1 to 10)
set found to false

while not found then
  ask "Guess a number (1-10):"

  if answer = secret then
    say "Correct! You win!"
    set found to true
  else
    if answer < secret then
      say "Too low!"
    else
      say "Too high!"
    end
  end
end
```

### Functions

Create reusable code:

```blockscript
# Define a function
define greet with name
  say join "Hello, " and join name and "!"
end

# Call the function
call greet with "Alice"
call greet with "Bob"

# Function with return value
define square with n
  return n * n
end

set result to (call square with 5)
print result  # 25
```

### Lists

Work with collections:

```blockscript
# Create a list
create list fruits

# Add items
add "apple" to fruits
add "banana" to fruits
add "cherry" to fruits

# Access items (1-based indexing)
print item 1 of fruits  # apple

# Modify items
set item 2 of fruits to "blueberry"

# Get length
set count to (length of fruits)
print count  # 3

# Loop through list
for i from 1 to (length of fruits)
  print item i of fruits
end

# Delete item
delete item 1 of fruits
```

## Common Mistakes

### 1. Forgetting `end`

❌ Wrong:
```blockscript
if x > 5 then
  say "Big number"
```

✅ Correct:
```blockscript
if x > 5 then
  say "Big number"
end
```

### 2. Using 0-based indexing

❌ Wrong:
```blockscript
create list items
add "first" to items
print item 0 of items  # Won't work!
```

✅ Correct:
```blockscript
create list items
add "first" to items
print item 1 of items  # Lists start at 1
```

### 3. Forgetting parentheses for function calls

❌ Wrong:
```blockscript
set r to random from 1 to 10  # Error!
```

✅ Correct:
```blockscript
set r to (random from 1 to 10)
```

### 4. Using variables before setting them

❌ Wrong:
```blockscript
change score by 10  # score doesn't exist yet!
```

✅ Correct:
```blockscript
set score to 0
change score by 10
```

## Tips and Tricks

1. **Use comments** - Start lines with `#` to add notes
2. **Indent your code** - Makes it easier to read
3. **Use the linter** - Run `lint` to check for issues
4. **Start simple** - Break complex problems into small steps
5. **Test often** - Run your code frequently to catch errors early
6. **Use descriptive names** - `playerScore` is better than `x`

## Next Steps

Now that you know the basics, try:

1. **Explore examples** - Look at the programs in `examples/`
2. **Modify examples** - Change them to see what happens
3. **Build projects**:
   - Calculator
   - Quiz game
   - Number guessing game
   - Text adventure
   - Simple chatbot

4. **Read the full spec** - See [LANGUAGE_SPEC.md](LANGUAGE_SPEC.md)

## Getting Help

- Check the examples in the `examples/` directory
- Read error messages carefully - they tell you what's wrong
- Use the linter to find issues before running
- Look at the language specification for detailed syntax

## Practice Challenges

### Challenge 1: Temperature Converter

Create a program that converts Celsius to Fahrenheit.

Formula: F = (C × 9/5) + 32

### Challenge 2: Grade Calculator

Ask for test scores and calculate the average and letter grade.

### Challenge 3: Palindrome Checker

Check if a word reads the same forwards and backwards.

### Challenge 4: Times Table

Print the multiplication table for a number the user enters.

### Challenge 5: Rock, Paper, Scissors

Create a game where the user plays against the computer.

---

Happy coding! 🎉
