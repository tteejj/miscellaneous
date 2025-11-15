// Module System - Import/Export functionality

import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { Lexer } from './lexer.js';
import { Parser } from './parser.js';

export class ModuleLoader {
  constructor() {
    this.loadedModules = new Map();
    this.moduleCache = new Map();
  }

  async loadModule(modulePath, currentFile) {
    // Resolve relative path
    const absolutePath = resolve(dirname(currentFile), modulePath);

    // Check cache
    if (this.moduleCache.has(absolutePath)) {
      return this.moduleCache.get(absolutePath);
    }

    // Load and parse module
    const source = readFileSync(absolutePath, 'utf-8');
    const lexer = new Lexer(source);
    const tokens = lexer.tokenize();
    const parser = new Parser(tokens);
    const ast = parser.parse();

    // Extract exports
    const exports = {
      functions: new Map(),
      variables: new Map(),
      lists: new Map(),
    };

    // Cache and return
    this.moduleCache.set(absolutePath, { ast, exports, path: absolutePath });
    return this.moduleCache.get(absolutePath);
  }

  clearCache() {
    this.moduleCache.clear();
  }
}

// AST Nodes for modules
export class ImportStatement {
  constructor(modulePath, imports, line, column) {
    this.type = 'ImportStatement';
    this.modulePath = modulePath;
    this.imports = imports; // ['*'] or ['func1', 'func2']
    this.line = line;
    this.column = column;
  }
}

export class ExportStatement {
  constructor(name, type, line, column) {
    this.type = 'ExportStatement';
    this.name = name;
    this.exportType = type; // 'function', 'variable', 'list'
    this.line = line;
    this.column = column;
  }
}
