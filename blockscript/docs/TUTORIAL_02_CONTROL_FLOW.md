# Tutorial 2: Control Flow

Learn how to make decisions and repeat actions in your programs.

## Part 1: If Statements

If statements let your program make decisions:

```blockscript
set age to 18

if age >= 18 then
  say "You can vote!"
end
```

### If-Else

Handle both cases:

```blockscript
set temperature to 75

if temperature > 80 then
  say "It's hot!"
else
  say "It's not that hot."
end
```

### Multiple Conditions

```blockscript
set score to 85

if score >= 90 then
  say "Grade: A"
else
  if score >= 80 then
    say "Grade: B"
  else
    if score >= 70 then
      say "Grade: C"
    else
      say "Grade: F"
    end
  end
end
```

## Part 2: Comparison Operators

Use these to compare values:

```blockscript
x = y     # Equal to
x != y    # Not equal to
x > y     # Greater than
x < y     # Less than
x >= y    # Greater than or equal to
x <= y    # Less than or equal to
```

### Example: Number Comparison

```blockscript
ask "Enter first number:"
set a to answer

ask "Enter second number:"
set b to answer

if a > b then
  say join a and " is greater"
else
  if a < b then
    say join b and " is greater"
  else
    say "They are equal!"
  end
end
```

## Part 3: Logical Operators

Combine multiple conditions:

### AND - Both must be true

```blockscript
set age to 25
set hasLicense to true

if (age >= 16) and hasLicense then
  say "You can drive!"
end
```

### OR - At least one must be true

```blockscript
set day to "Saturday"

if (day = "Saturday") or (day = "Sunday") then
  say "It's the weekend!"
end
```

### NOT - Reverse a condition

```blockscript
set raining to false

if not raining then
  say "Let's go outside!"
end
```

## Part 4: Repeat Loops

Repeat actions a specific number of times:

```blockscript
repeat 5 times
  say "Hello!"
end
```

Output:
```
💬 Hello!
💬 Hello!
💬 Hello!
💬 Hello!
💬 Hello!
```

### Countdown Example

```blockscript
set count to 10

repeat 10 times
  print count
  change count by -1
end

say "Blast off!"
```

## Part 5: While Loops

Repeat while a condition is true:

```blockscript
set x to 1

while x <= 5 then
  print x
  change x by 1
end
```

Output:
```
1
2
3
4
5
```

### Be Careful!

Make sure your loop ends:

```blockscript
# ❌ WRONG - Infinite loop!
set x to 1
while x > 0 then
  print x
  # Forgot to change x!
end

# ✅ CORRECT
set x to 5
while x > 0 then
  print x
  change x by -1
end
```

## Part 6: For Loops

Loop through a range of numbers:

```blockscript
for i from 1 to 10
  print i
end
```

### Count by Steps

```blockscript
# Even numbers
for i from 0 to 20
  if (i mod 2) = 0 then
    print i
  end
end
```

### Sum Numbers

```blockscript
set sum to 0

for i from 1 to 100
  change sum by i
end

say join "Sum: " and sum  # 5050
```

## Practice Exercises

### Exercise 1: Even or Odd

```blockscript
ask "Enter a number:"
set num to answer

if (num mod 2) = 0 then
  say join num and " is even"
else
  say join num and " is odd"
end
```

### Exercise 2: Multiplication Table

```blockscript
ask "Which multiplication table?"
set num to answer

for i from 1 to 10
  set result to num * i
  print join num and join " × " and join i and join " = " and result
end
```

### Exercise 3: Password Checker

```blockscript
set password to "secret123"
set attempts to 3

while attempts > 0 then
  ask "Enter password:"

  if answer = password then
    say "Access granted!"
    set attempts to 0  # Exit loop
  else
    change attempts by -1

    if attempts > 0 then
      say join "Wrong! " and join attempts and " attempts left"
    else
      say "Access denied!"
    end
  end
end
```

### Exercise 4: Leap Year Checker

```blockscript
ask "Enter a year:"
set year to answer

set isLeap to false

if (year mod 4) = 0 then
  if (year mod 100) = 0 then
    if (year mod 400) = 0 then
      set isLeap to true
    end
  else
    set isLeap to true
  end
end

if isLeap then
  say join year and " is a leap year!"
else
  say join year and " is not a leap year."
end
```

### Exercise 5: FizzBuzz

```blockscript
for i from 1 to 30
  set output to ""

  if (i mod 3) = 0 then
    set output to "Fizz"
  end

  if (i mod 5) = 0 then
    set output to join output and "Buzz"
  end

  if output = "" then
    print i
  else
    print output
  end
end
```

## Part 7: Forever Loops

Loop indefinitely (use with caution!):

```blockscript
# ⚠️ This will run forever!
set count to 0

forever
  change count by 1
  print count

  # Usually you'd have some way to exit
  if count > 100 then
    # In a real program, you'd break here
  end
end
```

## Review

You've learned:
- ✅ If statements for decisions
- ✅ Comparison operators (=, !=, >, <, >=, <=)
- ✅ Logical operators (and, or, not)
- ✅ Repeat loops for fixed iterations
- ✅ While loops for conditional repetition
- ✅ For loops for counting
- ✅ Forever loops for infinite repetition

## Next Steps

Continue to [Tutorial 3: Lists and Data](TUTORIAL_03_LISTS.md) to learn about:
- Creating lists
- Adding and removing items
- Processing collections

---

## Quick Reference

### If Statement
```blockscript
if condition then
  # code
else
  # code
end
```

### Loops
```blockscript
repeat 10 times
  # code
end

while condition then
  # code
end

for i from 1 to 10
  # code
end

forever
  # code
end
```

### Comparisons
```blockscript
=    # Equal
!=   # Not equal
>    # Greater than
<    # Less than
>=   # Greater or equal
<=   # Less or equal
```

### Logic
```blockscript
and  # Both true
or   # At least one true
not  # Reverse
```
