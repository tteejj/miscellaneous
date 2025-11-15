// BlockScript - Main entry point

import { Lexer } from './lexer.js';
import { Parser } from './parser.js';
import { Interpreter } from './interpreter.js';
import { Linter } from './linter.js';

export class BlockScript {
  constructor(options = {}) {
    this.options = options;
  }

  async run(source, options = {}) {
    try {
      // Tokenize
      const lexer = new Lexer(source);
      const tokens = lexer.tokenize();

      // Parse
      const parser = new Parser(tokens);
      const ast = parser.parse();

      // Lint (optional)
      if (options.lint !== false) {
        const linter = new Linter();
        const lintMessages = linter.lint(ast);

        if (options.onLint) {
          options.onLint(lintMessages);
        }

        // Stop on errors
        const errors = lintMessages.filter(m => m.type === 'error');
        if (errors.length > 0) {
          return {
            success: false,
            errors: errors,
            lintMessages: lintMessages,
          };
        }
      }

      // Execute
      const interpreter = new Interpreter({
        inputCallback: options.inputCallback,
        outputCallback: options.outputCallback,
        maxIterations: options.maxIterations,
      });

      const result = await interpreter.execute(ast);

      return {
        ...result,
        tokens: options.includeTokens ? tokens : undefined,
        ast: options.includeAST ? ast : undefined,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        stack: error.stack,
      };
    }
  }

  tokenize(source) {
    const lexer = new Lexer(source);
    return lexer.tokenize();
  }

  parse(source) {
    const lexer = new Lexer(source);
    const tokens = lexer.tokenize();
    const parser = new Parser(tokens);
    return parser.parse();
  }

  lint(source) {
    const lexer = new Lexer(source);
    const tokens = lexer.tokenize();
    const parser = new Parser(tokens);
    const ast = parser.parse();
    const linter = new Linter();
    return linter.lint(ast);
  }
}

export { Lexer, Parser, Interpreter, Linter };
