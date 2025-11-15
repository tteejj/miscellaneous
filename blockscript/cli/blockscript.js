#!/usr/bin/env node

import { readFileSync, writeFileSync } from 'fs';
import { createInterface } from 'readline';
import { BlockScript } from '../src/index.js';
import { Formatter } from '../src/formatter.js';
import { Transpiler } from '../src/transpiler.js';
import { Debugger } from '../src/debugger.js';
import { Lexer } from '../src/lexer.js';
import { Parser } from '../src/parser.js';

const VERSION = '1.0.0';

function showHelp() {
  console.log(`
BlockScript v${VERSION}
A text-based programming language inspired by Scratch

Usage:
  blockscript <file>              Run a BlockScript file
  blockscript lint <file>         Lint a BlockScript file
  blockscript format <file>       Format a BlockScript file
  blockscript transpile <file>    Transpile to JavaScript
  blockscript debug <file>        Run with debugger
  blockscript profile <file>      Profile performance
  blockscript --help              Show this help message
  blockscript --version           Show version

Examples:
  blockscript program.bs          Run program.bs
  blockscript lint program.bs     Lint program.bs
  blockscript format program.bs   Format program.bs
  blockscript transpile program.bs Convert to JavaScript
`);
}

function showVersion() {
  console.log(`BlockScript v${VERSION}`);
}

async function runFile(filename) {
  try {
    const source = readFileSync(filename, 'utf-8');
    const bs = new BlockScript();

    // Setup input callback
    const rl = createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    const inputCallback = (prompt) => {
      return new Promise((resolve) => {
        rl.question('', (answer) => {
          resolve(answer);
        });
      });
    };

    const outputCallback = (msg) => {
      console.log(msg);
    };

    // Run with lint
    const result = await bs.run(source, {
      inputCallback,
      outputCallback,
      lint: true,
      onLint: (messages) => {
        const errors = messages.filter(m => m.type === 'error');
        const warnings = messages.filter(m => m.type === 'warning');
        const info = messages.filter(m => m.type === 'info');

        if (errors.length > 0) {
          console.error('\n❌ Errors:');
          errors.forEach(m => {
            console.error(`  Line ${m.line}:${m.column} - ${m.message}`);
          });
        }

        if (warnings.length > 0) {
          console.warn('\n⚠️  Warnings:');
          warnings.forEach(m => {
            console.warn(`  Line ${m.line}:${m.column} - ${m.message}`);
          });
        }

        if (info.length > 0 && process.env.VERBOSE) {
          console.info('\nℹ️  Info:');
          info.forEach(m => {
            console.info(`  ${m.message}`);
          });
        }
      },
    });

    rl.close();

    if (!result.success) {
      console.error(`\n❌ Error: ${result.error}`);
      process.exit(1);
    }

    console.log('\n✅ Program completed successfully');
  } catch (error) {
    console.error(`\n❌ Error reading file: ${error.message}`);
    process.exit(1);
  }
}

function lintFile(filename) {
  try {
    const source = readFileSync(filename, 'utf-8');
    const bs = new BlockScript();

    const messages = bs.lint(source);

    const errors = messages.filter(m => m.type === 'error');
    const warnings = messages.filter(m => m.type === 'warning');
    const info = messages.filter(m => m.type === 'info');

    console.log(`\nLinting ${filename}...\n`);

    if (errors.length > 0) {
      console.error('❌ Errors:');
      errors.forEach(m => {
        console.error(`  Line ${m.line}:${m.column} - ${m.message} [${m.rule}]`);
      });
    }

    if (warnings.length > 0) {
      console.warn('\n⚠️  Warnings:');
      warnings.forEach(m => {
        console.warn(`  Line ${m.line}:${m.column} - ${m.message} [${m.rule}]`);
      });
    }

    if (info.length > 0) {
      console.info('\nℹ️  Info:');
      info.forEach(m => {
        console.info(`  ${m.message} [${m.rule}]`);
      });
    }

    if (errors.length === 0 && warnings.length === 0 && info.length === 0) {
      console.log('✅ No issues found!');
    }

    console.log(`\nSummary: ${errors.length} errors, ${warnings.length} warnings, ${info.length} info`);

    if (errors.length > 0) {
      process.exit(1);
    }
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
}

function formatFile(filename) {
  try {
    const source = readFileSync(filename, 'utf-8');
    const formatter = new Formatter();
    const formatted = formatter.format(source);

    writeFileSync(filename, formatted, 'utf-8');
    console.log(`✅ Formatted ${filename}`);
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
}

function transpileFile(filename) {
  try {
    const source = readFileSync(filename, 'utf-8');
    const lexer = new Lexer(source);
    const tokens = lexer.tokenize();
    const parser = new Parser(tokens);
    const ast = parser.parse();

    const transpiler = new Transpiler();
    const jsCode = transpiler.transpile(ast);

    const outFile = filename.replace(/\.bs$/, '.js');
    writeFileSync(outFile, jsCode, 'utf-8');
    console.log(`✅ Transpiled to ${outFile}`);
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
}

async function debugFile(filename) {
  try {
    const source = readFileSync(filename, 'utf-8');
    const lexer = new Lexer(source);
    const tokens = lexer.tokenize();
    const parser = new Parser(tokens);
    const ast = parser.parse();

    const dbg = new Debugger();
    console.log('🐛 Starting debugger...');
    console.log('Commands: step, continue, breakpoint <line>, watch <var>, vars, quit');

    await dbg.debug(ast);
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
}

async function profileFile(filename) {
  try {
    const source = readFileSync(filename, 'utf-8');
    const bs = new BlockScript();

    console.log(`\n⏱️  Profiling ${filename}...\n`);

    const startTime = Date.now();
    const startMem = process.memoryUsage();

    const result = await bs.run(source, { lint: false });

    const endTime = Date.now();
    const endMem = process.memoryUsage();

    if (result.success) {
      console.log('\n📊 Performance Profile:');
      console.log(`  Execution time: ${endTime - startTime}ms`);
      console.log(`  Memory used: ${((endMem.heapUsed - startMem.heapUsed) / 1024 / 1024).toFixed(2)} MB`);
      console.log(`  Peak memory: ${(endMem.heapUsed / 1024 / 1024).toFixed(2)} MB`);
    } else {
      console.error(`\n❌ Error: ${result.error}`);
      process.exit(1);
    }
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}`);
    process.exit(1);
  }
}

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  showHelp();
  process.exit(0);
}

if (args[0] === '--version' || args[0] === '-v') {
  showVersion();
  process.exit(0);
}

if (args[0] === 'lint') {
  if (args.length < 2) {
    console.error('Error: Missing filename');
    console.error('Usage: blockscript lint <file>');
    process.exit(1);
  }
  lintFile(args[1]);
} else if (args[0] === 'format') {
  if (args.length < 2) {
    console.error('Error: Missing filename');
    console.error('Usage: blockscript format <file>');
    process.exit(1);
  }
  formatFile(args[1]);
} else if (args[0] === 'transpile') {
  if (args.length < 2) {
    console.error('Error: Missing filename');
    console.error('Usage: blockscript transpile <file>');
    process.exit(1);
  }
  transpileFile(args[1]);
} else if (args[0] === 'debug') {
  if (args.length < 2) {
    console.error('Error: Missing filename');
    console.error('Usage: blockscript debug <file>');
    process.exit(1);
  }
  debugFile(args[1]);
} else if (args[0] === 'profile') {
  if (args.length < 2) {
    console.error('Error: Missing filename');
    console.error('Usage: blockscript profile <file>');
    process.exit(1);
  }
  profileFile(args[1]);
} else {
  runFile(args[0]);
}
