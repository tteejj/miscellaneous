# Tutorial 3: Lists and Collections

Learn to work with collections of data.

## Part 1: Creating Lists

Lists store multiple values:

```blockscript
create list fruits

add "apple" to fruits
add "banana" to fruits
add "cherry" to fruits
```

## Part 2: Accessing List Items

Lists use 1-based indexing (first item is 1, not 0):

```blockscript
create list colors
add "red" to colors
add "green" to colors
add "blue" to colors

set first to (item 1 of colors)
set second to (item 2 of colors)

print first   # red
print second  # green
```

## Part 3: Modifying Lists

```blockscript
create list numbers
add 10 to numbers
add 20 to numbers
add 30 to numbers

# Change an item
set item 2 of numbers to 25

# Delete an item
delete item 1 of numbers

# Now numbers contains: [25, 30]
```

## Part 4: List Length

```blockscript
create list items
add "a" to items
add "b" to items
add "c" to items

set count to (length of items)
print count  # 3
```

## Part 5: Looping Through Lists

```blockscript
create list names
add "Alice" to names
add "Bob" to names
add "Charlie" to names

for i from 1 to (length of names)
  set name to (item i of names)
  say join "Hello, " and name
end
```

## Practice: Shopping List

```blockscript
create list shopping
set running to true

say "Shopping List Manager"
say "Commands: add, show, remove, quit"

while running then
  ask "Command:"
  set cmd to answer

  if cmd = "add" then
    ask "Item to add:"
    add answer to shopping
    say "Added!"
  end

  if cmd = "show" then
    if (length of shopping) = 0 then
      say "List is empty"
    else
      for i from 1 to (length of shopping)
        set item_name to (item i of shopping)
        print join i and join ". " and item_name
      end
    end
  end

  if cmd = "remove" then
    ask "Item number to remove:"
    set num to answer
    delete item num of shopping
    say "Removed!"
  end

  if cmd = "quit" then
    set running to false
  end
end
```

## Review

- ✅ Creating lists
- ✅ Adding items
- ✅ Accessing items by index
- ✅ Modifying items
- ✅ Deleting items
- ✅ Getting list length
- ✅ Looping through lists

## Next: [Tutorial 4: Functions](TUTORIAL_04_FUNCTIONS.md)
