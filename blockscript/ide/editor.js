// BlockScript IDE - Editor Logic

import { Lexer } from '../src/lexer.js';
import { Parser } from '../src/parser.js';
import { Interpreter } from '../src/interpreter.js';
import { Linter } from '../src/linter.js';

// Examples
const examples = {
  hello: `# Hello World
say "Hello, World!"
say "Welcome to BlockScript!"`,

  countdown: `# Countdown from 10
set count to 10

while count > 0 then
  say count
  change count by -1
end

say "Blast off!"`,

  fizzbuzz: `# FizzBuzz from 1 to 20
for i from 1 to 20
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
end`,

  guess: `# Guessing Game
set secret to (random from 1 to 10)
set guesses to 0
set found to false

say "I'm thinking of a number between 1 and 10!"

while not found then
  ask "What's your guess?"
  change guesses by 1

  if answer = secret then
    say join "Correct! It took you " and join guesses and " guesses!"
    set found to true
  else
    if answer < secret then
      say "Too low!"
    else
      say "Too high!"
    end
  end
end`,

  list: `# List Operations
create list fruits

add "apple" to fruits
add "banana" to fruits
add "cherry" to fruits

say "My favorite fruits:"
print item 1 of fruits
print item 2 of fruits
print item 3 of fruits

set item 2 of fruits to "blueberry"
say "I changed my mind about bananas!"

print item 2 of fruits`,

  function: `# Function Demo
define greet with name
  say join "Hello, " and join name and "!"
end

define add with a, b
  return a + b
end

call greet with "Alice"
call greet with "Bob"

set sum to (call add with 5, 10)
say join "5 + 10 = " and sum`
};

// DOM Elements
const editor = document.getElementById('editor');
const output = document.getElementById('output');
const runBtn = document.getElementById('runBtn');
const stopBtn = document.getElementById('stopBtn');
const lintBtn = document.getElementById('lintBtn');
const clearBtn = document.getElementById('clearBtn');
const exampleSelect = document.getElementById('exampleSelect');
const editorInfo = document.getElementById('editorInfo');
const statusInfo = document.getElementById('statusInfo');
const lintPanel = document.getElementById('lintPanel');
const lintResults = document.getElementById('lintResults');
const closeLintBtn = document.getElementById('closeLintBtn');

// State
let interpreter = null;
let inputResolver = null;

// Initialize with example
editor.value = examples.hello;

// Update editor info
editor.addEventListener('input', updateEditorInfo);
editor.addEventListener('click', updateEditorInfo);
editor.addEventListener('keyup', updateEditorInfo);

function updateEditorInfo() {
  const text = editor.value;
  const cursorPos = editor.selectionStart;
  const lines = text.substring(0, cursorPos).split('\n');
  const line = lines.length;
  const col = lines[lines.length - 1].length + 1;
  editorInfo.textContent = `Line ${line}, Col ${col}`;
}

// Clear output
function clearOutput() {
  output.innerHTML = '';
}

// Add output line
function addOutput(text, type = 'print') {
  const line = document.createElement('div');
  line.className = `output-line output-${type}`;
  line.textContent = text;
  output.appendChild(line);
  output.scrollTop = output.scrollHeight;
}

// Input callback
function inputCallback(prompt) {
  return new Promise((resolve) => {
    inputResolver = resolve;

    // Create input overlay
    const overlay = document.createElement('div');
    overlay.className = 'input-overlay';
    overlay.id = 'inputOverlay';

    const dialog = document.createElement('div');
    dialog.className = 'input-dialog';

    const title = document.createElement('h3');
    title.textContent = prompt || 'Enter value:';

    const input = document.createElement('input');
    input.type = 'text';
    input.id = 'userInput';

    const btn = document.createElement('button');
    btn.className = 'btn btn-primary';
    btn.textContent = 'Submit';

    btn.onclick = () => {
      const value = input.value;
      document.body.removeChild(overlay);
      resolve(value);
      addOutput(`> ${value}`, 'print');
    };

    input.onkeypress = (e) => {
      if (e.key === 'Enter') {
        btn.click();
      }
    };

    dialog.appendChild(title);
    dialog.appendChild(input);
    dialog.appendChild(btn);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);

    setTimeout(() => input.focus(), 100);
  });
}

// Output callback
function outputCallback(text) {
  if (text.startsWith('💬')) {
    addOutput(text, 'say');
  } else if (text.startsWith('❓')) {
    addOutput(text, 'ask');
  } else {
    addOutput(text, 'print');
  }
}

// Run code
async function runCode() {
  const source = editor.value;

  clearOutput();
  lintPanel.style.display = 'none';

  runBtn.disabled = true;
  stopBtn.disabled = false;
  statusInfo.textContent = 'Running...';

  try {
    const lexer = new Lexer(source);
    const tokens = lexer.tokenize();

    const parser = new Parser(tokens);
    const ast = parser.parse();

    interpreter = new Interpreter({
      inputCallback,
      outputCallback,
    });

    const result = await interpreter.execute(ast);

    if (result.success) {
      addOutput('✅ Program completed successfully', 'success');
      statusInfo.textContent = 'Completed';
    } else {
      addOutput(`❌ ${result.error}`, 'error');
      statusInfo.textContent = 'Error';
    }
  } catch (error) {
    addOutput(`❌ ${error.message}`, 'error');
    statusInfo.textContent = 'Error';
  }

  runBtn.disabled = false;
  stopBtn.disabled = true;
}

// Stop execution
function stopExecution() {
  if (interpreter) {
    interpreter.requestBreak();
    addOutput('⏹️ Execution stopped', 'error');
    statusInfo.textContent = 'Stopped';
  }

  // Close any input dialogs
  const overlay = document.getElementById('inputOverlay');
  if (overlay) {
    document.body.removeChild(overlay);
    if (inputResolver) {
      inputResolver('');
    }
  }

  runBtn.disabled = false;
  stopBtn.disabled = true;
}

// Lint code
function lintCode() {
  const source = editor.value;

  try {
    const lexer = new Lexer(source);
    const tokens = lexer.tokenize();

    const parser = new Parser(tokens);
    const ast = parser.parse();

    const linter = new Linter();
    const messages = linter.lint(ast);

    // Display results
    lintResults.innerHTML = '';

    if (messages.length === 0) {
      lintResults.innerHTML = '<div style="color: #28a745; font-weight: 600;">✅ No issues found!</div>';
    } else {
      const errors = messages.filter(m => m.type === 'error');
      const warnings = messages.filter(m => m.type === 'warning');
      const info = messages.filter(m => m.type === 'info');

      messages.forEach(msg => {
        const div = document.createElement('div');
        div.className = `lint-message lint-${msg.type}`;

        const icon = msg.type === 'error' ? '❌' : msg.type === 'warning' ? '⚠️' : 'ℹ️';
        const location = msg.line > 0 ? `Line ${msg.line}:${msg.column}` : 'General';

        div.innerHTML = `
          <strong>${icon} ${location}</strong>
          ${msg.message}
          <div class="rule">[${msg.rule}]</div>
        `;

        lintResults.appendChild(div);
      });

      // Add summary
      const summary = document.createElement('div');
      summary.style.marginTop = '15px';
      summary.style.fontWeight = '600';
      summary.textContent = `Summary: ${errors.length} errors, ${warnings.length} warnings, ${info.length} info`;
      lintResults.appendChild(summary);
    }

    lintPanel.style.display = 'block';
    statusInfo.textContent = 'Linted';
  } catch (error) {
    lintResults.innerHTML = `<div class="lint-message lint-error"><strong>❌ Parse Error</strong>${error.message}</div>`;
    lintPanel.style.display = 'block';
    statusInfo.textContent = 'Error';
  }
}

// Load example
exampleSelect.addEventListener('change', (e) => {
  const example = e.target.value;
  if (example && examples[example]) {
    editor.value = examples[example];
    clearOutput();
    lintPanel.style.display = 'none';
    statusInfo.textContent = 'Ready';
    updateEditorInfo();
  }
  e.target.value = '';
});

// Event listeners
runBtn.addEventListener('click', runCode);
stopBtn.addEventListener('click', stopExecution);
lintBtn.addEventListener('click', lintCode);
clearBtn.addEventListener('click', () => {
  clearOutput();
  statusInfo.textContent = 'Ready';
});
closeLintBtn.addEventListener('click', () => {
  lintPanel.style.display = 'none';
});

// Keyboard shortcuts
editor.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + Enter to run
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    runCode();
  }

  // Tab key for indentation
  if (e.key === 'Tab') {
    e.preventDefault();
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(end);
    editor.selectionStart = editor.selectionEnd = start + 2;
  }
});

// Initial update
updateEditorInfo();
statusInfo.textContent = 'Ready';
