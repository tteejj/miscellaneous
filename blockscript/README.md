# BlockScript

> A text-based programming language inspired by Scratch, designed for beginners

BlockScript combines the simplicity of Scratch with the power of text-based programming. It features an easy-to-learn syntax, built-in linter, and a beautiful web-based IDE.

## Features

- **Simple, readable syntax** - No complex symbols or confusing operators
- **Built-in linter** - Catch errors before runtime
- **Web-based IDE** - Write and run code in your browser
- **CLI tool** - Run programs from the command line
- **Interactive input** - Get user input with the `ask` statement
- **Lists and functions** - Build complex programs with ease
- **Zero dependencies** - Pure JavaScript implementation

## Quick Start

### Using the Web IDE

1. Open `ide/index.html` in a web browser
2. Write your code in the editor
3. Click "Run" to execute
4. Try the example programs from the dropdown

### Using the CLI

```bash
# Run a program
node blockscript/cli/blockscript.js examples/hello.bs

# Lint a program
node blockscript/cli/blockscript.js lint examples/hello.bs
```

## Hello World

```blockscript
say "Hello, World!"

ask "What's your name?"
set name to answer

say join "Nice to meet you, " and name
```

## Language Features

### Variables

```blockscript
set myVar to 10
change myVar by 5
```

### Output

```blockscript
say "This appears in a speech bubble"
print "This prints directly"
```

### Input

```blockscript
ask "What's your favorite color?"
set color to answer
say join "I like " and join color and " too!"
```

### Control Flow

```blockscript
# If statement
if score > 100 then
  say "High score!"
else
  say "Keep trying!"
end

# Loops
repeat 5 times
  say "Hello!"
end

for i from 1 to 10
  print i
end

while x < 100 then
  change x by 1
end
```

### Lists

```blockscript
create list fruits
add "apple" to fruits
add "banana" to fruits

print item 1 of fruits
set item 2 of fruits to "cherry"
```

### Functions

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

### Math Operations

```blockscript
set result to 10 + 5
set result to (10 + 5) * 2
set result to x mod 10
set result to 2 ^ 8  # Power: 256

# Built-in functions
set r to (random from 1 to 10)
set a to (abs of -5)
set s to (sqrt of 16)
```

### String Operations

```blockscript
set message to join "Hello " and "World"
set len to (length of "Hello")
set first to (letter 1 of "Hello")
```

## Project Structure

```
blockscript/
├── src/
│   ├── lexer.js         # Tokenization
│   ├── parser.js        # AST generation
│   ├── interpreter.js   # Execution engine
│   ├── linter.js        # Static analysis
│   └── index.js         # Main API
├── ide/
│   ├── index.html       # Web IDE
│   ├── styles.css       # Styling
│   └── editor.js        # IDE logic
├── cli/
│   └── blockscript.js   # Command-line tool
├── examples/
│   ├── hello.bs         # Hello World
│   ├── fibonacci.bs     # Fibonacci sequence
│   ├── calculator.bs    # Calculator
│   ├── prime.bs         # Prime numbers
│   ├── sorting.bs       # Bubble sort
│   └── math_quiz.bs     # Math quiz game
├── docs/
│   └── LANGUAGE_SPEC.md # Language specification
└── tests/               # Test files
```

## Examples

See the `examples/` directory for complete programs:

- **hello.bs** - Hello World with user input
- **fibonacci.bs** - Calculate Fibonacci sequence
- **calculator.bs** - Interactive calculator
- **prime.bs** - Find prime numbers
- **sorting.bs** - Bubble sort algorithm
- **math_quiz.bs** - Interactive math quiz

## API Usage

```javascript
import { BlockScript } from './src/index.js';

const bs = new BlockScript();

const result = await bs.run(`
  say "Hello from BlockScript!"
  set x to 42
  print x
`);

if (result.success) {
  console.log('Output:', result.output);
  console.log('Variables:', result.globals);
} else {
  console.error('Error:', result.error);
}
```

## Linting

```javascript
const messages = bs.lint(sourceCode);

messages.forEach(msg => {
  console.log(`${msg.type}: ${msg.message} at line ${msg.line}`);
});
```

## Development

### Running Tests

```bash
node tests/run-tests.js
```

### Starting the IDE

```bash
# Install http-server if needed
npm install -g http-server

# Start the server
http-server ide -p 8080

# Open http://localhost:8080
```

## Language Syntax

For complete language documentation, see [LANGUAGE_SPEC.md](docs/LANGUAGE_SPEC.md)

## Why BlockScript?

BlockScript bridges the gap between visual programming (Scratch) and traditional text-based languages. It's perfect for:

- **Beginners** learning programming concepts
- **Educators** teaching coding fundamentals
- **Quick prototypes** testing logic and algorithms
- **Fun projects** making interactive programs

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

MIT License - see LICENSE file for details

## Acknowledgments

Inspired by Scratch (MIT Media Lab), designed to make programming accessible to everyone.

---

Made with ❤️ for learners everywhere
