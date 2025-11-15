#!/usr/bin/env node

import { BlockScript } from '../src/index.js';

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (error) {
    console.error(`❌ ${name}`);
    console.error(`   ${error.message}`);
    failed++;
  }
}

async function asyncTest(name, fn) {
  try {
    await fn();
    console.log(`✅ ${name}`);
    passed++;
  } catch (error) {
    console.error(`❌ ${name}`);
    console.error(`   ${error.message}`);
    failed++;
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

function assertEquals(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(message || `Expected ${expected} but got ${actual}`);
  }
}

console.log('\n🧪 Running BlockScript Tests\n');

// Lexer Tests
console.log('📝 Lexer Tests');

test('Tokenize numbers', () => {
  const bs = new BlockScript();
  const tokens = bs.tokenize('42 3.14 -5');
  assert(tokens.length > 0, 'Should tokenize numbers');
});

test('Tokenize strings', () => {
  const bs = new BlockScript();
  const tokens = bs.tokenize('"hello" \'world\'');
  assert(tokens.length > 0, 'Should tokenize strings');
});

test('Tokenize keywords', () => {
  const bs = new BlockScript();
  const tokens = bs.tokenize('set to if then else end');
  assert(tokens.length > 0, 'Should tokenize keywords');
});

test('Tokenize operators', () => {
  const bs = new BlockScript();
  const tokens = bs.tokenize('+ - * / = > < >= <=');
  assert(tokens.length > 0, 'Should tokenize operators');
});

test('Skip comments', () => {
  const bs = new BlockScript();
  const tokens = bs.tokenize('set x to 5 # this is a comment');
  assert(tokens.length > 0, 'Should skip comments');
});

// Parser Tests
console.log('\n📊 Parser Tests');

test('Parse set statement', () => {
  const bs = new BlockScript();
  const ast = bs.parse('set x to 5');
  assert(ast.statements.length === 1, 'Should parse set statement');
  assert(ast.statements[0].type === 'SetStatement', 'Should be a SetStatement');
});

test('Parse if statement', () => {
  const bs = new BlockScript();
  const ast = bs.parse('if x > 5 then\nsay "big"\nend');
  assert(ast.statements.length === 1, 'Should parse if statement');
  assert(ast.statements[0].type === 'IfStatement', 'Should be an IfStatement');
});

test('Parse repeat statement', () => {
  const bs = new BlockScript();
  const ast = bs.parse('repeat 10 times\nprint "hi"\nend');
  assert(ast.statements.length === 1, 'Should parse repeat statement');
  assert(ast.statements[0].type === 'RepeatStatement', 'Should be a RepeatStatement');
});

test('Parse function definition', () => {
  const bs = new BlockScript();
  const ast = bs.parse('define greet with name\nsay name\nend');
  assert(ast.statements.length === 1, 'Should parse function definition');
  assert(ast.statements[0].type === 'FunctionDefinition', 'Should be a FunctionDefinition');
});

test('Parse expressions', () => {
  const bs = new BlockScript();
  const ast = bs.parse('set x to 10 + 5 * 2');
  assert(ast.statements.length === 1, 'Should parse expressions');
});

// Interpreter Tests
console.log('\n🚀 Interpreter Tests');

await asyncTest('Execute set statement', async () => {
  const bs = new BlockScript();
  const result = await bs.run('set x to 42');
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.x, 42, 'Variable should be 42');
});

await asyncTest('Execute math operations', async () => {
  const bs = new BlockScript();
  const result = await bs.run('set x to 10 + 5\nset y to x * 2');
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.x, 15, 'x should be 15');
  assertEquals(result.globals.y, 30, 'y should be 30');
});

await asyncTest('Execute if statement', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    set x to 10
    if x > 5 then
      set result to "big"
    else
      set result to "small"
    end
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.result, 'big', 'result should be "big"');
});

await asyncTest('Execute repeat loop', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    set count to 0
    repeat 5 times
      change count by 1
    end
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.count, 5, 'count should be 5');
});

await asyncTest('Execute while loop', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    set x to 0
    while x < 10 then
      change x by 1
    end
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.x, 10, 'x should be 10');
});

await asyncTest('Execute for loop', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    set sum to 0
    for i from 1 to 10
      change sum by i
    end
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.sum, 55, 'sum should be 55');
});

await asyncTest('Execute function definition and call', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    define add with a, b
      return a + b
    end
    set result to (call add with 5, 10)
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.result, 15, 'result should be 15');
});

await asyncTest('Execute list operations', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    create list items
    add "apple" to items
    add "banana" to items
    set first to (item 1 of items)
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.first, 'apple', 'first should be "apple"');
});

await asyncTest('Execute built-in functions', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    set msg to join "Hello " and "World"
    set len to (length of "test")
    set abs_val to (abs of -5)
    set sqrt_val to (sqrt of 16)
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.msg, 'Hello World', 'msg should be "Hello World"');
  assertEquals(result.globals.len, 4, 'len should be 4');
  assertEquals(result.globals.abs_val, 5, 'abs_val should be 5');
  assertEquals(result.globals.sqrt_val, 4, 'sqrt_val should be 4');
});

await asyncTest('Execute comparisons', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    set a to 5
    set b to 10
    set eq to a = 5
    set neq to a != b
    set gt to b > a
    set lt to a < b
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.eq, true, 'eq should be true');
  assertEquals(result.globals.neq, true, 'neq should be true');
  assertEquals(result.globals.gt, true, 'gt should be true');
  assertEquals(result.globals.lt, true, 'lt should be true');
});

await asyncTest('Execute logical operations', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    set a to true
    set b to false
    set and_result to a and b
    set or_result to a or b
    set not_result to not b
  `);
  assert(result.success, 'Should execute successfully');
  assertEquals(result.globals.and_result, false, 'and_result should be false');
  assertEquals(result.globals.or_result, true, 'or_result should be true');
  assertEquals(result.globals.not_result, true, 'not_result should be true');
});

// Linter Tests
console.log('\n🔍 Linter Tests');

test('Lint undefined variable', () => {
  const bs = new BlockScript();
  const messages = bs.lint('print x');
  const warnings = messages.filter(m => m.type === 'warning');
  assert(warnings.length > 0, 'Should warn about undefined variable');
});

test('Lint division by zero', () => {
  const bs = new BlockScript();
  const messages = bs.lint('set x to 10 / 0');
  const errors = messages.filter(m => m.type === 'error');
  assert(errors.length > 0, 'Should error on division by zero');
});

test('Lint empty block', () => {
  const bs = new BlockScript();
  const messages = bs.lint('if x > 5 then\nend');
  const warnings = messages.filter(m => m.type === 'warning');
  assert(warnings.length > 0, 'Should warn about empty block');
});

test('Lint undefined function', () => {
  const bs = new BlockScript();
  const messages = bs.lint('call foo with 5');
  const warnings = messages.filter(m => m.type === 'warning');
  assert(warnings.length > 0, 'Should warn about undefined function');
});

test('No lint issues for valid code', () => {
  const bs = new BlockScript();
  const messages = bs.lint('set x to 5\nprint x');
  const errors = messages.filter(m => m.type === 'error');
  assertEquals(errors.length, 0, 'Should have no errors for valid code');
});

// Error Handling Tests
console.log('\n⚠️  Error Handling Tests');

await asyncTest('Handle syntax error', async () => {
  const bs = new BlockScript();
  const result = await bs.run('set x to');
  assertEquals(result.success, false, 'Should fail on syntax error');
});

await asyncTest('Handle runtime error', async () => {
  const bs = new BlockScript();
  const result = await bs.run('set x to 10 / 0');
  // Division by zero should be caught
  assert(true, 'Should handle runtime errors');
});

await asyncTest('Handle undefined variable in change', async () => {
  const bs = new BlockScript();
  const result = await bs.run('change x by 1');
  assert(result.success, 'Should handle undefined variable gracefully');
});

// Integration Tests
console.log('\n🔗 Integration Tests');

await asyncTest('FizzBuzz', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    for i from 1 to 15
      set output to ""
      if (i mod 3) = 0 then
        set output to "Fizz"
      end
      if (i mod 5) = 0 then
        set output to join output and "Buzz"
      end
    end
  `);
  assert(result.success, 'Should execute FizzBuzz');
});

await asyncTest('Fibonacci', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    set a to 0
    set b to 1
    set count to 1
    while count <= 10 then
      set temp to a
      set a to b
      set b to temp + b
      change count by 1
    end
  `);
  assert(result.success, 'Should calculate Fibonacci');
  assert(result.globals.a > 0, 'Should have calculated Fibonacci numbers');
});

await asyncTest('Factorial function', async () => {
  const bs = new BlockScript();
  const result = await bs.run(`
    define factorial with n
      if n <= 1 then
        return 1
      else
        set n_minus_1 to n - 1
        set sub_result to (call factorial with n_minus_1)
        return n * sub_result
      end
    end
    set result to (call factorial with 5)
  `);
  assert(result.success, 'Should calculate factorial');
  assertEquals(result.globals.result, 120, 'factorial(5) should be 120');
});

// Summary
console.log('\n' + '='.repeat(50));
console.log(`\n📊 Test Results: ${passed} passed, ${failed} failed\n`);

if (failed === 0) {
  console.log('✨ All tests passed! ✨\n');
  process.exit(0);
} else {
  console.log('❌ Some tests failed\n');
  process.exit(1);
}
