# BlockScript Quick Start

Get started with BlockScript in 5 minutes!

## Option 1: Web IDE (No Installation)

1. Open `ide/index.html` in your browser
2. The editor loads with a "Hello World" example
3. Click the **Run** button
4. See the output appear in the right panel!

Try the other examples from the dropdown menu.

## Option 2: Command Line

### Run a Program

```bash
node cli/blockscript.js examples/hello.bs
```

### Check Your Code

```bash
node cli/blockscript.js lint examples/hello.bs
```

## Your First Program

Create a file called `first.bs`:

```blockscript
say "Hello, BlockScript!"

ask "What's your name?"
set name to answer

say join "Nice to meet you, " and join name and "!"

ask "Pick a number from 1 to 10:"
set guess to answer

set secret to (random from 1 to 10)

if guess = secret then
  say "Wow! You guessed it!"
else
  say join "Nope! It was " and secret
end
```

Run it:

```bash
node cli/blockscript.js first.bs
```

## Next Steps

- 📖 Read the [Language Specification](docs/LANGUAGE_SPEC.md)
- 🎓 Follow the [Getting Started Guide](docs/GETTING_STARTED.md)
- 💡 Explore the [Examples](examples/)
- 🔨 Build your own programs!

## Common Commands

```bash
# Run a program
node cli/blockscript.js program.bs

# Lint/check a program
node cli/blockscript.js lint program.bs

# Run tests
node tests/run-tests.js

# Start web IDE server
npx http-server ide -p 8080
```

## Learn by Example

Check out these programs in the `examples/` folder:

- **hello.bs** - Interactive greeting
- **fibonacci.bs** - Generate Fibonacci numbers
- **calculator.bs** - Simple calculator
- **prime.bs** - Find prime numbers
- **sorting.bs** - Sort a list of numbers
- **math_quiz.bs** - Interactive math quiz

## Get Help

- Check the error messages - they tell you what's wrong
- Use the linter before running: `blockscript lint program.bs`
- Read the [Getting Started Guide](docs/GETTING_STARTED.md)
- Look at working examples in the `examples/` folder

---

Happy coding! 🚀
