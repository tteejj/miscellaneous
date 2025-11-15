# Tutorial 4: Functions

Create reusable code with functions.

## Part 1: Defining Functions

```blockscript
define greet with name
  say join "Hello, " and name
end

call greet with "Alice"
call greet with "Bob"
```

## Part 2: Functions with Returns

```blockscript
define add with a, b
  return a + b
end

set result to (call add with 5, 10)
print result  # 15
```

## Part 3: Multiple Parameters

```blockscript
define calculateArea with width, height
  return width * height
end

set area to (call calculateArea with 10, 5)
say join "Area: " and area
```

## Part 4: Functions for Organization

```blockscript
define showMenu
  say "=== Main Menu ==="
  say "1. Start Game"
  say "2. Options"
  say "3. Quit"
end

define processChoice with choice
  if choice = 1 then
    say "Starting game..."
  end

  if choice = 2 then
    say "Opening options..."
  end

  if choice = 3 then
    say "Quitting..."
  end
end

call showMenu
ask "Your choice:"
call processChoice with answer
```

## Practice: Temperature Converter

```blockscript
define celsiusToFahrenheit with celsius
  set fahrenheit to celsius * 9 / 5 + 32
  return fahrenheit
end

define fahrenheitToCelsius with fahrenheit
  set celsius to (fahrenheit - 32) * 5 / 9
  return celsius
end

say "Temperature Converter"
say "1. C to F"
say "2. F to C"

ask "Choice:"
set choice to answer

if choice = 1 then
  ask "Celsius:"
  set c to answer
  set f to (call celsiusToFahrenheit with c)
  say join c and join "°C = " and join f and "°F"
end

if choice = 2 then
  ask "Fahrenheit:"
  set f to answer
  set c to (call fahrenheitToCelsius with f)
  say join f and join "°F = " and join c and "°C"
end
```

## Review

- ✅ Defining functions
- ✅ Function parameters
- ✅ Returning values
- ✅ Organizing code

## Next: [Tutorial 5: Projects](TUTORIAL_05_PROJECTS.md)
