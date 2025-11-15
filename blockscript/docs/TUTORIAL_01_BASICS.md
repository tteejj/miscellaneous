# Tutorial 1: The Basics

Welcome to BlockScript! This tutorial will teach you the fundamentals of programming.

## Part 1: Your First Program

Let's start with the classic "Hello, World!" program:

```blockscript
say "Hello, World!"
```

That's it! When you run this program, it will output:
```
💬 Hello, World!
```

The `say` command displays a message.

### Try It Yourself

1. Open the BlockScript IDE (in `ide/index.html`)
2. Type the code above
3. Click **Run**
4. See the output!

## Part 2: Variables

Variables store values for later use. Think of them as labeled boxes.

```blockscript
set age to 25
set name to "Alice"

print age
print name
```

Output:
```
25
Alice
```

### Variable Rules

- Use `set` to create or update a variable
- Variable names can contain letters, numbers, and underscores
- They must start with a letter

## Part 3: Math

BlockScript can do calculations:

```blockscript
set x to 10
set y to 5

set sum to x + y
set difference to x - y
set product to x * y
set quotient to x / y

print sum          # 15
print difference   # 5
print product      # 50
print quotient     # 2
```

### Math Operators

- `+` Addition
- `-` Subtraction
- `*` Multiplication
- `/` Division
- `mod` Modulo (remainder)
- `^` Power

### Example: Calculate Circle Area

```blockscript
set radius to 5
set pi to 3.14159
set area to pi * (radius ^ 2)

say join "Area: " and area
```

## Part 4: Getting Input

Use `ask` to get input from the user:

```blockscript
ask "What's your name?"
set name to answer

ask "How old are you?"
set age to answer

say join "Hello, " and join name and "!"
say join "You are " and join age and " years old."
```

The `answer` variable automatically stores the user's input.

## Part 5: Changing Variables

Use `change` to modify a variable by adding or subtracting:

```blockscript
set score to 0

say "You found a coin!"
change score by 10

say "You found another coin!"
change score by 10

say "You lost some coins!"
change score by -5

say join "Final score: " and score  # 15
```

## Part 6: Comments

Comments are notes in your code that don't run:

```blockscript
# This is a comment
say "This runs"  # This is also a comment
```

Use comments to:
- Explain what your code does
- Add reminders
- Temporarily disable code

## Practice Exercises

### Exercise 1: Temperature Converter
Write a program that converts Celsius to Fahrenheit.
Formula: F = C * 9/5 + 32

```blockscript
ask "Enter temperature in Celsius:"
set celsius to answer

set fahrenheit to celsius * 9 / 5 + 32

say join celsius and join "°C = " and join fahrenheit and "°F"
```

### Exercise 2: Simple Calculator
Create a calculator that adds two numbers:

```blockscript
ask "Enter first number:"
set num1 to answer

ask "Enter second number:"
set num2 to answer

set result to num1 + num2

say join num1 and join " + " and join num2 and join " = " and result
```

### Exercise 3: Tip Calculator
Calculate the tip for a restaurant bill:

```blockscript
ask "Enter bill amount:"
set bill to answer

ask "Enter tip percentage (15, 18, or 20):"
set tipPercent to answer

set tipAmount to bill * tipPercent / 100
set total to bill + tipAmount

say join "Tip: $" and tipAmount
say join "Total: $" and total
```

## Review

You've learned:
- ✅ How to display output with `say` and `print`
- ✅ How to create variables with `set`
- ✅ How to do math operations
- ✅ How to get user input with `ask`
- ✅ How to modify variables with `change`
- ✅ How to write comments with `#`

## Next Steps

Continue to [Tutorial 2: Control Flow](TUTORIAL_02_CONTROL_FLOW.md) to learn about:
- If statements
- Loops
- Making decisions

---

## Quick Reference

### Output
```blockscript
say "Message"      # With speech bubble
print value        # Plain output
```

### Variables
```blockscript
set name to value  # Create/update variable
change x by 5      # Add to variable
change x by -3     # Subtract from variable
```

### Math
```blockscript
x + y    # Addition
x - y    # Subtraction
x * y    # Multiplication
x / y    # Division
x mod y  # Remainder
x ^ y    # Power
```

### Input
```blockscript
ask "Question?"    # Ask user
answer             # User's response
```
