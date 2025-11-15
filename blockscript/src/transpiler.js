// Transpiler - Convert BlockScript to JavaScript

export class Transpiler {
  constructor(options = {}) {
    this.indentSize = options.indentSize || 2;
    this.useConst = options.useConst !== false;
    this.useArrowFunctions = options.useArrowFunctions !== false;
    this.includeComments = options.includeComments !== false;
  }

  transpile(ast) {
    const code = [];

    // Add header comment
    if (this.includeComments) {
      code.push('// Generated from BlockScript');
      code.push('');
    }

    // Transpile statements
    for (const statement of ast.statements) {
      const js = this.transpileStatement(statement);
      if (js) {
        code.push(js);
      }
    }

    return code.join('\n');
  }

  transpileStatement(node, indent = 0) {
    const indentation = ' '.repeat(this.indentSize * indent);

    switch (node.type) {
      case 'SetStatement':
        return `${indentation}${this.useConst ? 'let' : 'var'} ${node.variable} = ${this.transpileExpression(node.value)};`;

      case 'ChangeStatement':
        return `${indentation}${node.variable} += ${this.transpileExpression(node.value)};`;

      case 'SayStatement':
        return `${indentation}console.log("💬", ${this.transpileExpression(node.value)});`;

      case 'PrintStatement':
        return `${indentation}console.log(${this.transpileExpression(node.value)});`;

      case 'AskStatement':
        return `${indentation}// Ask: ${this.transpileExpression(node.prompt)}`;

      case 'IfStatement':
        return this.transpileIfStatement(node, indent);

      case 'RepeatStatement':
        return this.transpileRepeatStatement(node, indent);

      case 'ForeverStatement':
        return this.transpileForeverStatement(node, indent);

      case 'WhileStatement':
        return this.transpileWhileStatement(node, indent);

      case 'ForStatement':
        return this.transpileForStatement(node, indent);

      case 'CreateListStatement':
        return `${indentation}${this.useConst ? 'let' : 'var'} ${node.name} = [];`;

      case 'AddToListStatement':
        return `${indentation}${node.listName}.push(${this.transpileExpression(node.value)});`;

      case 'DeleteFromListStatement':
        return `${indentation}${node.listName}.splice(${this.transpileExpression(node.index)} - 1, 1);`;

      case 'ListAssignment':
        return `${indentation}${node.listName}[${this.transpileExpression(node.index)} - 1] = ${this.transpileExpression(node.value)};`;

      case 'FunctionDefinition':
        return this.transpileFunctionDefinition(node, indent);

      case 'ReturnStatement':
        return `${indentation}return ${this.transpileExpression(node.value)};`;

      case 'FunctionCall':
        return `${indentation}${this.transpileFunctionCall(node)};`;

      default:
        return `${indentation}// Unknown: ${node.type}`;
    }
  }

  transpileExpression(node) {
    if (!node) return 'null';

    switch (node.type) {
      case 'Literal':
        return typeof node.value === 'string' ? `"${node.value}"` : String(node.value);

      case 'Identifier':
        return node.name;

      case 'BinaryExpression':
        return this.transpileBinaryExpression(node);

      case 'UnaryExpression':
        return this.transpileUnaryExpression(node);

      case 'FunctionCall':
        return this.transpileFunctionCall(node);

      case 'ListAccess':
        return `${node.listName}[${this.transpileExpression(node.index)} - 1]`;

      default:
        return 'null';
    }
  }

  transpileBinaryExpression(node) {
    const left = this.transpileExpression(node.left);
    const right = this.transpileExpression(node.right);

    const operatorMap = {
      '+': '+',
      '-': '-',
      '*': '*',
      '/': '/',
      'mod': '%',
      '^': '**',
      '=': '===',
      '!=': '!==',
      '>': '>',
      '<': '<',
      '>=': '>=',
      '<=': '<=',
      'and': '&&',
      'or': '||',
    };

    const op = operatorMap[node.operator] || node.operator;
    return `(${left} ${op} ${right})`;
  }

  transpileUnaryExpression(node) {
    const operand = this.transpileExpression(node.operand);

    if (node.operator === '-') {
      return `(-${operand})`;
    }

    if (node.operator === 'not') {
      return `(!${operand})`;
    }

    return operand;
  }

  transpileFunctionCall(node) {
    // Built-in functions
    const builtins = {
      'join': (args) => `String(${args[0]}) + String(${args[1]})`,
      'length': (args) => `(Array.isArray(${args[0]}) ? ${args[0]}.length : String(${args[0]}).length)`,
      'letter': (args) => `String(${args[1]})[${args[0]} - 1]`,
      'random': (args) => `(Math.floor(Math.random() * (${args[1]} - ${args[0]} + 1)) + ${args[0]})`,
      'abs': (args) => `Math.abs(${args[0]})`,
      'round': (args) => `Math.round(${args[0]})`,
      'sqrt': (args) => `Math.sqrt(${args[0]})`,
      'sin': (args) => `Math.sin(${args[0]})`,
      'cos': (args) => `Math.cos(${args[0]})`,
      'tan': (args) => `Math.tan(${args[0]})`,
    };

    const args = node.args.map(arg => this.transpileExpression(arg));

    if (builtins[node.name]) {
      return builtins[node.name](args);
    }

    return `${node.name}(${args.join(', ')})`;
  }

  transpileIfStatement(node, indent) {
    const indentation = ' '.repeat(this.indentSize * indent);
    const condition = this.transpileExpression(node.condition);

    let code = `${indentation}if (${condition}) {\n`;

    for (const stmt of node.thenBlock) {
      code += this.transpileStatement(stmt, indent + 1) + '\n';
    }

    if (node.elseBlock.length > 0) {
      code += `${indentation}} else {\n`;

      for (const stmt of node.elseBlock) {
        code += this.transpileStatement(stmt, indent + 1) + '\n';
      }
    }

    code += `${indentation}}`;

    return code;
  }

  transpileRepeatStatement(node, indent) {
    const indentation = ' '.repeat(this.indentSize * indent);
    const count = this.transpileExpression(node.count);

    let code = `${indentation}for (let __i = 0; __i < ${count}; __i++) {\n`;

    for (const stmt of node.body) {
      code += this.transpileStatement(stmt, indent + 1) + '\n';
    }

    code += `${indentation}}`;

    return code;
  }

  transpileForeverStatement(node, indent) {
    const indentation = ' '.repeat(this.indentSize * indent);

    let code = `${indentation}while (true) {\n`;

    for (const stmt of node.body) {
      code += this.transpileStatement(stmt, indent + 1) + '\n';
    }

    code += `${indentation}}`;

    return code;
  }

  transpileWhileStatement(node, indent) {
    const indentation = ' '.repeat(this.indentSize * indent);
    const condition = this.transpileExpression(node.condition);

    let code = `${indentation}while (${condition}) {\n`;

    for (const stmt of node.body) {
      code += this.transpileStatement(stmt, indent + 1) + '\n';
    }

    code += `${indentation}}`;

    return code;
  }

  transpileForStatement(node, indent) {
    const indentation = ' '.repeat(this.indentSize * indent);
    const start = this.transpileExpression(node.start);
    const end = this.transpileExpression(node.end);

    let code = `${indentation}for (let ${node.variable} = ${start}; ${node.variable} <= ${end}; ${node.variable}++) {\n`;

    for (const stmt of node.body) {
      code += this.transpileStatement(stmt, indent + 1) + '\n';
    }

    code += `${indentation}}`;

    return code;
  }

  transpileFunctionDefinition(node, indent) {
    const indentation = ' '.repeat(this.indentSize * indent);
    const params = node.parameters.join(', ');

    let code;
    if (this.useArrowFunctions) {
      code = `${indentation}const ${node.name} = (${params}) => {\n`;
    } else {
      code = `${indentation}function ${node.name}(${params}) {\n`;
    }

    for (const stmt of node.body) {
      code += this.transpileStatement(stmt, indent + 1) + '\n';
    }

    code += `${indentation}}`;

    return code;
  }

  // Transpile to module format
  transpileToModule(ast) {
    const code = this.transpile(ast);

    return `// ES6 Module\n\n${code}\n\n// Export main function\nexport { main };`;
  }

  // Transpile to CommonJS
  transpileToCommonJS(ast) {
    const code = this.transpile(ast);

    return `// CommonJS Module\n\n${code}\n\n// Export\nmodule.exports = { main };`;
  }

  // Generate source map
  generateSourceMap(ast, blockscriptSource, jsSource) {
    // Simplified source map
    return {
      version: 3,
      file: 'output.js',
      sourceRoot: '',
      sources: ['input.bs'],
      names: [],
      mappings: '', // Would need to implement proper mapping
      sourcesContent: [blockscriptSource],
    };
  }
}

// Helper to transpile source code directly
export function transpile(source, options = {}) {
  import('./lexer.js').then(({ Lexer }) => {
    import('./parser.js').then(({ Parser }) => {
      const lexer = new Lexer(source);
      const tokens = lexer.tokenize();
      const parser = new Parser(tokens);
      const ast = parser.parse();

      const transpiler = new Transpiler(options);
      return transpiler.transpile(ast);
    });
  });
}
