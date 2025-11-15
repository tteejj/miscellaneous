// Linter - Static code analysis for BlockScript

export class LintMessage {
  constructor(type, message, line, column, rule) {
    this.type = type; // 'error', 'warning', 'info'
    this.message = message;
    this.line = line;
    this.column = column;
    this.rule = rule;
  }
}

export class Linter {
  constructor() {
    this.messages = [];
    this.variables = new Set();
    this.lists = new Set();
    this.functions = new Set();
    this.usedVariables = new Set();
    this.usedLists = new Set();
    this.usedFunctions = new Set();
  }

  lint(ast) {
    this.messages = [];
    this.variables = new Set();
    this.lists = new Set();
    this.functions = new Set();
    this.usedVariables = new Set();
    this.usedLists = new Set();
    this.usedFunctions = new Set();

    // First pass: collect declarations
    this.collectDeclarations(ast);

    // Second pass: check usage
    this.checkProgram(ast);

    // Check for unused variables
    this.checkUnused();

    return this.messages;
  }

  collectDeclarations(node) {
    if (!node) return;

    switch (node.type) {
      case 'Program':
        node.statements.forEach(stmt => this.collectDeclarations(stmt));
        break;

      case 'SetStatement':
        this.variables.add(node.variable);
        this.collectDeclarations(node.value);
        break;

      case 'ChangeStatement':
        this.variables.add(node.variable);
        this.collectDeclarations(node.value);
        break;

      case 'CreateListStatement':
        this.lists.add(node.name);
        break;

      case 'FunctionDefinition':
        this.functions.add(node.name);
        node.body.forEach(stmt => this.collectDeclarations(stmt));
        break;

      case 'IfStatement':
        this.collectDeclarations(node.condition);
        node.thenBlock.forEach(stmt => this.collectDeclarations(stmt));
        node.elseBlock.forEach(stmt => this.collectDeclarations(stmt));
        break;

      case 'RepeatStatement':
      case 'ForeverStatement':
      case 'WhileStatement':
        if (node.condition) this.collectDeclarations(node.condition);
        if (node.count) this.collectDeclarations(node.count);
        node.body.forEach(stmt => this.collectDeclarations(stmt));
        break;

      case 'ForStatement':
        this.variables.add(node.variable);
        this.collectDeclarations(node.start);
        this.collectDeclarations(node.end);
        node.body.forEach(stmt => this.collectDeclarations(stmt));
        break;

      case 'WhenStatement':
        node.body.forEach(stmt => this.collectDeclarations(stmt));
        break;

      case 'SayStatement':
      case 'PrintStatement':
      case 'AskStatement':
      case 'ReturnStatement':
        this.collectDeclarations(node.value || node.prompt);
        break;

      case 'AddToListStatement':
      case 'DeleteFromListStatement':
        this.collectDeclarations(node.value);
        break;

      case 'ListAssignment':
        this.collectDeclarations(node.index);
        this.collectDeclarations(node.value);
        break;

      case 'BinaryExpression':
        this.collectDeclarations(node.left);
        this.collectDeclarations(node.right);
        break;

      case 'UnaryExpression':
        this.collectDeclarations(node.operand);
        break;

      case 'FunctionCall':
        node.args.forEach(arg => this.collectDeclarations(arg));
        break;

      case 'ListAccess':
        this.collectDeclarations(node.index);
        break;
    }
  }

  checkProgram(node) {
    if (node.type === 'Program') {
      node.statements.forEach(stmt => this.checkStatement(stmt));
    }
  }

  checkStatement(node) {
    if (!node) return;

    switch (node.type) {
      case 'SetStatement':
        this.checkExpression(node.value);
        break;

      case 'ChangeStatement':
        if (!this.variables.has(node.variable)) {
          this.addWarning(
            `Variable '${node.variable}' used before declaration`,
            node.line,
            node.column,
            'undefined-variable'
          );
        }
        this.usedVariables.add(node.variable);
        this.checkExpression(node.value);
        break;

      case 'SayStatement':
      case 'PrintStatement':
        this.checkExpression(node.value);
        break;

      case 'AskStatement':
        this.checkExpression(node.prompt);
        break;

      case 'IfStatement':
        this.checkExpression(node.condition);
        node.thenBlock.forEach(stmt => this.checkStatement(stmt));
        node.elseBlock.forEach(stmt => this.checkStatement(stmt));

        // Check for empty blocks
        if (node.thenBlock.length === 0) {
          this.addWarning(
            'Empty if block',
            node.line,
            node.column,
            'empty-block'
          );
        }
        break;

      case 'RepeatStatement':
        this.checkExpression(node.count);
        node.body.forEach(stmt => this.checkStatement(stmt));

        if (node.body.length === 0) {
          this.addWarning(
            'Empty repeat block',
            node.line,
            node.column,
            'empty-block'
          );
        }
        break;

      case 'ForeverStatement':
        node.body.forEach(stmt => this.checkStatement(stmt));

        if (node.body.length === 0) {
          this.addWarning(
            'Empty forever block',
            node.line,
            node.column,
            'empty-block'
          );
        }

        // Warn about potential infinite loop
        this.addInfo(
          'Forever loop detected - ensure you have a break condition',
          node.line,
          node.column,
          'infinite-loop'
        );
        break;

      case 'WhileStatement':
        this.checkExpression(node.condition);
        node.body.forEach(stmt => this.checkStatement(stmt));

        if (node.body.length === 0) {
          this.addWarning(
            'Empty while block',
            node.line,
            node.column,
            'empty-block'
          );
        }
        break;

      case 'ForStatement':
        this.checkExpression(node.start);
        this.checkExpression(node.end);
        node.body.forEach(stmt => this.checkStatement(stmt));

        if (node.body.length === 0) {
          this.addWarning(
            'Empty for block',
            node.line,
            node.column,
            'empty-block'
          );
        }
        break;

      case 'AddToListStatement':
        if (!this.lists.has(node.listName)) {
          this.addWarning(
            `List '${node.listName}' not declared`,
            node.line,
            node.column,
            'undefined-list'
          );
        }
        this.usedLists.add(node.listName);
        this.checkExpression(node.value);
        break;

      case 'DeleteFromListStatement':
        if (!this.lists.has(node.listName)) {
          this.addWarning(
            `List '${node.listName}' not declared`,
            node.line,
            node.column,
            'undefined-list'
          );
        }
        this.usedLists.add(node.listName);
        this.checkExpression(node.index);
        break;

      case 'ListAssignment':
        if (!this.lists.has(node.listName)) {
          this.addWarning(
            `List '${node.listName}' not declared`,
            node.line,
            node.column,
            'undefined-list'
          );
        }
        this.usedLists.add(node.listName);
        this.checkExpression(node.index);
        this.checkExpression(node.value);
        break;

      case 'FunctionDefinition':
        node.body.forEach(stmt => this.checkStatement(stmt));
        break;

      case 'ReturnStatement':
        this.checkExpression(node.value);
        break;

      case 'WhenStatement':
        node.body.forEach(stmt => this.checkStatement(stmt));
        break;

      case 'FunctionCall':
        this.checkExpression(node);
        break;
    }
  }

  checkExpression(node) {
    if (!node) return;

    switch (node.type) {
      case 'Identifier':
        this.usedVariables.add(node.name);
        if (!this.variables.has(node.name)) {
          // Check if it's a built-in variable
          const builtins = ['answer', 'timer', 'mouse_x', 'mouse_y', 'key_pressed'];
          if (!builtins.includes(node.name)) {
            this.addWarning(
              `Variable '${node.name}' used before declaration`,
              node.line,
              node.column,
              'undefined-variable'
            );
          }
        }
        break;

      case 'BinaryExpression':
        this.checkExpression(node.left);
        this.checkExpression(node.right);

        // Check for division by zero
        if (node.operator === '/' && node.right.type === 'Literal' && node.right.value === 0) {
          this.addError(
            'Division by zero',
            node.line,
            node.column,
            'division-by-zero'
          );
        }
        break;

      case 'UnaryExpression':
        this.checkExpression(node.operand);
        break;

      case 'FunctionCall':
        this.usedFunctions.add(node.name);

        // Check built-in functions
        const builtins = ['join', 'length', 'letter', 'random', 'abs', 'round', 'floor', 'ceil', 'sqrt', 'pow', 'min', 'max', 'sin', 'cos', 'tan'];
        if (!builtins.includes(node.name) && !this.functions.has(node.name)) {
          this.addWarning(
            `Function '${node.name}' not defined`,
            node.line,
            node.column,
            'undefined-function'
          );
        }

        node.args.forEach(arg => this.checkExpression(arg));
        break;

      case 'ListAccess':
        if (!this.lists.has(node.listName)) {
          this.addWarning(
            `List '${node.listName}' not declared`,
            node.line,
            node.column,
            'undefined-list'
          );
        }
        this.usedLists.add(node.listName);
        this.checkExpression(node.index);
        break;
    }
  }

  checkUnused() {
    // Check unused variables
    for (const variable of this.variables) {
      if (!this.usedVariables.has(variable)) {
        this.addInfo(
          `Variable '${variable}' declared but never used`,
          0,
          0,
          'unused-variable'
        );
      }
    }

    // Check unused lists
    for (const list of this.lists) {
      if (!this.usedLists.has(list)) {
        this.addInfo(
          `List '${list}' declared but never used`,
          0,
          0,
          'unused-list'
        );
      }
    }

    // Check unused functions
    for (const func of this.functions) {
      if (!this.usedFunctions.has(func)) {
        this.addInfo(
          `Function '${func}' defined but never called`,
          0,
          0,
          'unused-function'
        );
      }
    }
  }

  addError(message, line, column, rule) {
    this.messages.push(new LintMessage('error', message, line, column, rule));
  }

  addWarning(message, line, column, rule) {
    this.messages.push(new LintMessage('warning', message, line, column, rule));
  }

  addInfo(message, line, column, rule) {
    this.messages.push(new LintMessage('info', message, line, column, rule));
  }
}
