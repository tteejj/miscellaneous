#!/usr/bin/env node

// REPL - Read-Eval-Print Loop for BlockScript

import { createInterface } from 'readline';
import { BlockScript } from './index.js';
import { getStdlibFunctions } from './stdlib.js';

const VERSION = '1.0.0';

class REPL {
  constructor() {
    this.bs = new BlockScript();
    this.history = [];
    this.globals = {};
    this.multilineBuffer = [];
    this.inMultiline = false;
    this.blockDepth = 0;

    this.rl = createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '>>> ',
      terminal: true,
    });

    this.setupCommands();
    this.setupAutoComplete();
  }

  setupCommands() {
    this.commands = {
      '.help': () => this.showHelp(),
      '.exit': () => this.exit(),
      '.clear': () => this.clearHistory(),
      '.vars': () => this.showVariables(),
      '.functions': () => this.showFunctions(),
      '.stdlib': () => this.showStdlib(),
      '.history': () => this.showHistory(),
      '.reset': () => this.reset(),
      '.save': (filename) => this.saveHistory(filename),
      '.load': (filename) => this.loadFile(filename),
      '.multiline': () => this.toggleMultiline(),
    };
  }

  setupAutoComplete() {
    const keywords = [
      'set', 'to', 'change', 'by', 'say', 'print', 'ask',
      'if', 'then', 'else', 'end',
      'repeat', 'times', 'forever', 'while', 'for', 'from',
      'create', 'list', 'add', 'delete', 'item', 'of',
      'define', 'with', 'call', 'return',
      'when', 'program', 'starts', 'key', 'pressed',
      'and', 'or', 'not',
      'join', 'length', 'letter', 'random', 'abs', 'round', 'sqrt',
      'sin', 'cos', 'tan', 'mod',
      'true', 'false',
    ];

    const commands = Object.keys(this.commands);

    this.rl.on('line', () => {});

    // Simple autocomplete
    this.completer = (line) => {
      const hits = [...keywords, ...commands].filter((c) => c.startsWith(line));
      return [hits.length ? hits : keywords, line];
    };
  }

  showBanner() {
    console.log(`
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎨 BlockScript REPL v${VERSION}                           ║
║   A text-based programming language inspired by Scratch  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Type .help for commands, .exit to quit
`);
  }

  showHelp() {
    console.log(`
📚 REPL Commands:

  .help          Show this help message
  .exit          Exit the REPL
  .clear         Clear screen and history
  .vars          Show all variables
  .functions     Show defined functions
  .stdlib        Show standard library functions
  .history       Show command history
  .reset         Reset the environment
  .save <file>   Save history to file
  .load <file>   Load and execute a file
  .multiline     Toggle multiline mode

💡 Tips:
  - Use up/down arrows to navigate history
  - Type expressions to evaluate them immediately
  - Define functions and they'll persist in the session
  - Variables are preserved between commands

📖 Examples:
  >>> set x to 42
  >>> print x
  >>> for i from 1 to 5
  ...   print i
  ... end
`);
  }

  showVariables() {
    if (Object.keys(this.globals).length === 0) {
      console.log('No variables defined');
      return;
    }

    console.log('\n📦 Variables:');
    for (const [name, value] of Object.entries(this.globals)) {
      const type = Array.isArray(value) ? 'list' : typeof value;
      const display = Array.isArray(value)
        ? `[${value.slice(0, 5).join(', ')}${value.length > 5 ? '...' : ''}]`
        : JSON.stringify(value);
      console.log(`  ${name} (${type}): ${display}`);
    }
    console.log();
  }

  showFunctions() {
    // This would track user-defined functions
    console.log('\n🔧 User-defined functions:');
    console.log('  (tracking not yet implemented)');
    console.log();
  }

  showStdlib() {
    console.log('\n📚 Standard Library:');
    const functions = getStdlibFunctions();
    const grouped = {};

    functions.forEach(fn => {
      const [namespace, name] = fn.split('.');
      if (!grouped[namespace]) grouped[namespace] = [];
      grouped[namespace].push(name);
    });

    for (const [namespace, fns] of Object.entries(grouped)) {
      console.log(`\n  ${namespace}:`);
      const columns = 3;
      for (let i = 0; i < fns.length; i += columns) {
        const row = fns.slice(i, i + columns);
        console.log('    ' + row.map(f => f.padEnd(20)).join(''));
      }
    }
    console.log();
  }

  showHistory() {
    console.log('\n📜 History:');
    this.history.forEach((cmd, i) => {
      console.log(`  ${(i + 1).toString().padStart(3)}: ${cmd}`);
    });
    console.log();
  }

  clearHistory() {
    console.clear();
    this.history = [];
    this.showBanner();
  }

  reset() {
    this.globals = {};
    this.bs = new BlockScript();
    console.log('✨ Environment reset');
  }

  exit() {
    console.log('\n👋 Goodbye!\n');
    process.exit(0);
  }

  saveHistory(filename) {
    if (!filename) {
      console.log('❌ Usage: .save <filename>');
      return;
    }

    import('fs').then(fs => {
      fs.writeFileSync(filename, this.history.join('\n'));
      console.log(`✅ History saved to ${filename}`);
    });
  }

  loadFile(filename) {
    if (!filename) {
      console.log('❌ Usage: .load <filename>');
      return;
    }

    import('fs').then(async fs => {
      try {
        const content = fs.readFileSync(filename, 'utf-8');
        await this.execute(content);
        console.log(`✅ Loaded ${filename}`);
      } catch (error) {
        console.log(`❌ Error loading file: ${error.message}`);
      }
    });
  }

  toggleMultiline() {
    this.inMultiline = !this.inMultiline;
    console.log(this.inMultiline ? '📝 Multiline mode ON' : '📝 Multiline mode OFF');
  }

  async execute(code) {
    try {
      const result = await this.bs.run(code, {
        inputCallback: (prompt) => {
          return new Promise((resolve) => {
            this.rl.question(`${prompt} `, resolve);
          });
        },
        outputCallback: (msg) => {
          console.log(msg);
        },
        lint: false,
      });

      if (result.success) {
        // Update globals
        this.globals = { ...this.globals, ...result.globals };

        // If it's an expression, show the result
        if (result.output.length === 0 && result.globals) {
          const lastVar = Object.keys(result.globals).pop();
          if (lastVar) {
            const value = result.globals[lastVar];
            if (value !== undefined && value !== null) {
              console.log(`→ ${JSON.stringify(value)}`);
            }
          }
        }
      } else {
        console.log(`❌ ${result.error}`);
      }
    } catch (error) {
      console.log(`❌ ${error.message}`);
    }
  }

  async handleLine(line) {
    line = line.trim();

    // Handle empty lines
    if (!line) {
      if (this.inMultiline && this.multilineBuffer.length > 0) {
        // Execute multiline buffer
        const code = this.multilineBuffer.join('\n');
        this.multilineBuffer = [];
        this.blockDepth = 0;
        this.inMultiline = false;
        this.rl.setPrompt('>>> ');
        await this.execute(code);
      }
      return;
    }

    // Handle REPL commands
    if (line.startsWith('.')) {
      const [cmd, ...args] = line.split(/\s+/);
      if (this.commands[cmd]) {
        this.commands[cmd](...args);
      } else {
        console.log(`Unknown command: ${cmd}`);
        console.log('Type .help for available commands');
      }
      return;
    }

    // Add to history
    this.history.push(line);

    // Check for block keywords
    const blockStart = /\b(if|while|for|repeat|forever|define|when)\b/.test(line);
    const blockEnd = line === 'end';

    if (blockStart) {
      this.blockDepth++;
      this.inMultiline = true;
    }

    if (blockEnd) {
      this.blockDepth--;
    }

    // Multiline handling
    if (this.inMultiline || this.blockDepth > 0) {
      this.multilineBuffer.push(line);
      this.rl.setPrompt('... ');

      if (this.blockDepth === 0) {
        // Execute the complete block
        const code = this.multilineBuffer.join('\n');
        this.multilineBuffer = [];
        this.inMultiline = false;
        this.rl.setPrompt('>>> ');
        await this.execute(code);
      }
    } else {
      // Execute immediately
      await this.execute(line);
    }
  }

  start() {
    this.showBanner();

    this.rl.on('line', async (line) => {
      await this.handleLine(line);
      this.rl.prompt();
    });

    this.rl.on('close', () => {
      this.exit();
    });

    // Handle Ctrl+C
    this.rl.on('SIGINT', () => {
      if (this.multilineBuffer.length > 0) {
        this.multilineBuffer = [];
        this.blockDepth = 0;
        this.inMultiline = false;
        this.rl.setPrompt('>>> ');
        console.log('\n^C');
        this.rl.prompt();
      } else {
        console.log('\nUse .exit or press Ctrl+C again to quit');
        setTimeout(() => {
          this.rl.prompt();
        }, 100);
      }
    });

    this.rl.prompt();
  }
}

// Start REPL if run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const repl = new REPL();
  repl.start();
}

export { REPL };
