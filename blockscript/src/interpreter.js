// Interpreter - Executes the AST

export class RuntimeError extends Error {
  constructor(message, line, column) {
    super(`Runtime Error at line ${line}, column ${column}: ${message}`);
    this.line = line;
    this.column = column;
  }
}

class ReturnValue {
  constructor(value) {
    this.value = value;
  }
}

class BreakLoop extends Error {}

export class Interpreter {
  constructor(options = {}) {
    this.globals = new Map();
    this.locals = new Map();
    this.functions = new Map();
    this.eventHandlers = new Map();
    this.output = [];
    this.inputCallback = options.inputCallback || (() => Promise.resolve(''));
    this.outputCallback = options.outputCallback || ((msg) => console.log(msg));
    this.maxIterations = options.maxIterations || 100000;
    this.iterationCount = 0;
    this.startTime = Date.now();
    this.breakRequested = false;
  }

  async execute(ast) {
    this.output = [];
    this.iterationCount = 0;
    this.startTime = Date.now();
    this.breakRequested = false;

    try {
      await this.executeProgram(ast);
      return {
        success: true,
        output: this.output,
        globals: Object.fromEntries(this.globals),
      };
    } catch (error) {
      if (error instanceof RuntimeError) {
        return {
          success: false,
          error: error.message,
          output: this.output,
        };
      }
      throw error;
    }
  }

  async executeProgram(program) {
    // Execute all statements
    for (const statement of program.statements) {
      if (this.breakRequested) break;
      await this.executeStatement(statement);
    }

    // Execute event handlers if any
    if (this.eventHandlers.has('program starts')) {
      await this.executeBlock(this.eventHandlers.get('program starts'));
    }
  }

  async executeStatement(node) {
    this.iterationCount++;
    if (this.iterationCount > this.maxIterations) {
      throw new RuntimeError(
        'Maximum iteration count exceeded (possible infinite loop)',
        node.line,
        node.column
      );
    }

    switch (node.type) {
      case 'SetStatement':
        return await this.executeSetStatement(node);
      case 'ChangeStatement':
        return await this.executeChangeStatement(node);
      case 'SayStatement':
        return await this.executeSayStatement(node);
      case 'PrintStatement':
        return await this.executePrintStatement(node);
      case 'AskStatement':
        return await this.executeAskStatement(node);
      case 'IfStatement':
        return await this.executeIfStatement(node);
      case 'RepeatStatement':
        return await this.executeRepeatStatement(node);
      case 'ForeverStatement':
        return await this.executeForeverStatement(node);
      case 'WhileStatement':
        return await this.executeWhileStatement(node);
      case 'ForStatement':
        return await this.executeForStatement(node);
      case 'CreateListStatement':
        return await this.executeCreateListStatement(node);
      case 'AddToListStatement':
        return await this.executeAddToListStatement(node);
      case 'DeleteFromListStatement':
        return await this.executeDeleteFromListStatement(node);
      case 'ListAssignment':
        return await this.executeListAssignment(node);
      case 'FunctionDefinition':
        return await this.executeFunctionDefinition(node);
      case 'ReturnStatement':
        return await this.executeReturnStatement(node);
      case 'WhenStatement':
        return await this.executeWhenStatement(node);
      case 'FunctionCall':
        await this.evaluateExpression(node);
        return;
      default:
        throw new RuntimeError(`Unknown statement type: ${node.type}`, node.line, node.column);
    }
  }

  async executeSetStatement(node) {
    const value = await this.evaluateExpression(node.value);
    this.setVariable(node.variable, value);
  }

  async executeChangeStatement(node) {
    const current = this.getVariable(node.variable) || 0;
    const change = await this.evaluateExpression(node.value);
    this.setVariable(node.variable, current + change);
  }

  async executeSayStatement(node) {
    const value = await this.evaluateExpression(node.value);
    const message = `💬 ${this.stringify(value)}`;
    this.output.push(message);
    this.outputCallback(message);
  }

  async executePrintStatement(node) {
    const value = await this.evaluateExpression(node.value);
    const message = this.stringify(value);
    this.output.push(message);
    this.outputCallback(message);
  }

  async executeAskStatement(node) {
    const prompt = await this.evaluateExpression(node.prompt);
    const message = `❓ ${this.stringify(prompt)}`;
    this.output.push(message);
    this.outputCallback(message);
    const answer = await this.inputCallback(this.stringify(prompt));
    this.setVariable('answer', answer);
  }

  async executeIfStatement(node) {
    const condition = await this.evaluateExpression(node.condition);
    if (this.isTruthy(condition)) {
      await this.executeBlock(node.thenBlock);
    } else if (node.elseBlock.length > 0) {
      await this.executeBlock(node.elseBlock);
    }
  }

  async executeRepeatStatement(node) {
    const count = await this.evaluateExpression(node.count);
    for (let i = 0; i < count; i++) {
      if (this.breakRequested) break;
      try {
        await this.executeBlock(node.body);
      } catch (e) {
        if (e instanceof BreakLoop) break;
        throw e;
      }
    }
  }

  async executeForeverStatement(node) {
    const maxForeverIterations = 10000;
    let count = 0;
    while (!this.breakRequested) {
      if (count++ > maxForeverIterations) {
        throw new RuntimeError(
          'Forever loop exceeded maximum iterations (10000). Use break or limit loop.',
          node.line,
          node.column
        );
      }
      try {
        await this.executeBlock(node.body);
      } catch (e) {
        if (e instanceof BreakLoop) break;
        throw e;
      }
    }
  }

  async executeWhileStatement(node) {
    while (!this.breakRequested && this.isTruthy(await this.evaluateExpression(node.condition))) {
      try {
        await this.executeBlock(node.body);
      } catch (e) {
        if (e instanceof BreakLoop) break;
        throw e;
      }
    }
  }

  async executeForStatement(node) {
    const start = await this.evaluateExpression(node.start);
    const end = await this.evaluateExpression(node.end);

    for (let i = start; i <= end; i++) {
      if (this.breakRequested) break;
      this.setVariable(node.variable, i);
      try {
        await this.executeBlock(node.body);
      } catch (e) {
        if (e instanceof BreakLoop) break;
        throw e;
      }
    }
  }

  async executeCreateListStatement(node) {
    this.setVariable(node.name, []);
  }

  async executeAddToListStatement(node) {
    const value = await this.evaluateExpression(node.value);
    const list = this.getVariable(node.listName);
    if (!Array.isArray(list)) {
      throw new RuntimeError(
        `${node.listName} is not a list`,
        node.line,
        node.column
      );
    }
    list.push(value);
  }

  async executeDeleteFromListStatement(node) {
    const index = await this.evaluateExpression(node.index);
    const list = this.getVariable(node.listName);
    if (!Array.isArray(list)) {
      throw new RuntimeError(
        `${node.listName} is not a list`,
        node.line,
        node.column
      );
    }
    list.splice(index - 1, 1); // 1-based indexing
  }

  async executeListAssignment(node) {
    const index = await this.evaluateExpression(node.index);
    const value = await this.evaluateExpression(node.value);
    const list = this.getVariable(node.listName);
    if (!Array.isArray(list)) {
      throw new RuntimeError(
        `${node.listName} is not a list`,
        node.line,
        node.column
      );
    }
    list[index - 1] = value; // 1-based indexing
  }

  async executeFunctionDefinition(node) {
    this.functions.set(node.name, {
      parameters: node.parameters,
      body: node.body,
    });
  }

  async executeReturnStatement(node) {
    const value = await this.evaluateExpression(node.value);
    throw new ReturnValue(value);
  }

  async executeWhenStatement(node) {
    this.eventHandlers.set(node.event, node.body);
  }

  async executeBlock(statements) {
    for (const statement of statements) {
      if (this.breakRequested) break;
      await this.executeStatement(statement);
    }
  }

  async evaluateExpression(node) {
    switch (node.type) {
      case 'Literal':
        return node.value;

      case 'Identifier':
        return this.getVariable(node.name);

      case 'BinaryExpression':
        return await this.evaluateBinaryExpression(node);

      case 'UnaryExpression':
        return await this.evaluateUnaryExpression(node);

      case 'FunctionCall':
        return await this.evaluateFunctionCall(node);

      case 'ListAccess':
        return await this.evaluateListAccess(node);

      default:
        throw new RuntimeError(
          `Unknown expression type: ${node.type}`,
          node.line,
          node.column
        );
    }
  }

  async evaluateBinaryExpression(node) {
    const left = await this.evaluateExpression(node.left);
    const right = await this.evaluateExpression(node.right);

    switch (node.operator) {
      case '+':
        return left + right;
      case '-':
        return left - right;
      case '*':
        return left * right;
      case '/':
        if (right === 0) {
          throw new RuntimeError('Division by zero', node.line, node.column);
        }
        return left / right;
      case 'mod':
        return left % right;
      case '^':
        return Math.pow(left, right);
      case '=':
        return left === right;
      case '!=':
        return left !== right;
      case '>':
        return left > right;
      case '<':
        return left < right;
      case '>=':
        return left >= right;
      case '<=':
        return left <= right;
      case 'and':
        return this.isTruthy(left) && this.isTruthy(right);
      case 'or':
        return this.isTruthy(left) || this.isTruthy(right);
      default:
        throw new RuntimeError(
          `Unknown operator: ${node.operator}`,
          node.line,
          node.column
        );
    }
  }

  async evaluateUnaryExpression(node) {
    const operand = await this.evaluateExpression(node.operand);

    switch (node.operator) {
      case '-':
        return -operand;
      case 'not':
        return !this.isTruthy(operand);
      default:
        throw new RuntimeError(
          `Unknown unary operator: ${node.operator}`,
          node.line,
          node.column
        );
    }
  }

  async evaluateFunctionCall(node) {
    // Built-in functions
    const builtins = {
      join: async (args) => {
        if (args.length !== 2) {
          throw new RuntimeError('join requires 2 arguments', node.line, node.column);
        }
        return this.stringify(args[0]) + this.stringify(args[1]);
      },
      length: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('length requires 1 argument', node.line, node.column);
        }
        const value = args[0];
        if (typeof value === 'string') return value.length;
        if (Array.isArray(value)) return value.length;
        return 0;
      },
      letter: async (args) => {
        if (args.length !== 2) {
          throw new RuntimeError('letter requires 2 arguments', node.line, node.column);
        }
        const index = args[0];
        const str = this.stringify(args[1]);
        return str[index - 1] || ''; // 1-based indexing
      },
      random: async (args) => {
        if (args.length !== 2) {
          throw new RuntimeError('random requires 2 arguments', node.line, node.column);
        }
        const from = args[0];
        const to = args[1];
        return Math.floor(Math.random() * (to - from + 1)) + from;
      },
      abs: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('abs requires 1 argument', node.line, node.column);
        }
        return Math.abs(args[0]);
      },
      round: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('round requires 1 argument', node.line, node.column);
        }
        return Math.round(args[0]);
      },
      sqrt: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('sqrt requires 1 argument', node.line, node.column);
        }
        return Math.sqrt(args[0]);
      },
      sin: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('sin requires 1 argument', node.line, node.column);
        }
        return Math.sin(args[0]);
      },
      cos: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('cos requires 1 argument', node.line, node.column);
        }
        return Math.cos(args[0]);
      },
      tan: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('tan requires 1 argument', node.line, node.column);
        }
        return Math.tan(args[0]);
      },
      floor: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('floor requires 1 argument', node.line, node.column);
        }
        return Math.floor(args[0]);
      },
      ceil: async (args) => {
        if (args.length !== 1) {
          throw new RuntimeError('ceil requires 1 argument', node.line, node.column);
        }
        return Math.ceil(args[0]);
      },
      pow: async (args) => {
        if (args.length !== 2) {
          throw new RuntimeError('pow requires 2 arguments', node.line, node.column);
        }
        return Math.pow(args[0], args[1]);
      },
      min: async (args) => {
        if (args.length < 1) {
          throw new RuntimeError('min requires at least 1 argument', node.line, node.column);
        }
        return Math.min(...args);
      },
      max: async (args) => {
        if (args.length < 1) {
          throw new RuntimeError('max requires at least 1 argument', node.line, node.column);
        }
        return Math.max(...args);
      },
    };

    const args = [];
    for (const arg of node.args) {
      args.push(await this.evaluateExpression(arg));
    }

    // Check built-ins first
    if (builtins[node.name]) {
      return await builtins[node.name](args);
    }

    // User-defined function
    if (this.functions.has(node.name)) {
      const func = this.functions.get(node.name);

      if (args.length !== func.parameters.length) {
        throw new RuntimeError(
          `Function ${node.name} expects ${func.parameters.length} arguments but got ${args.length}`,
          node.line,
          node.column
        );
      }

      // Save current locals
      const savedLocals = new Map(this.locals);

      // Set parameters
      for (let i = 0; i < func.parameters.length; i++) {
        this.locals.set(func.parameters[i], args[i]);
      }

      let returnValue = null;
      try {
        await this.executeBlock(func.body);
      } catch (e) {
        if (e instanceof ReturnValue) {
          returnValue = e.value;
        } else {
          throw e;
        }
      }

      // Restore locals
      this.locals = savedLocals;

      return returnValue;
    }

    throw new RuntimeError(
      `Unknown function: ${node.name}`,
      node.line,
      node.column
    );
  }

  async evaluateListAccess(node) {
    const index = await this.evaluateExpression(node.index);
    const list = this.getVariable(node.listName);
    if (!Array.isArray(list)) {
      throw new RuntimeError(
        `${node.listName} is not a list`,
        node.line,
        node.column
      );
    }
    return list[index - 1]; // 1-based indexing
  }

  setVariable(name, value) {
    if (this.locals.size > 0) {
      this.locals.set(name, value);
    } else {
      this.globals.set(name, value);
    }
  }

  getVariable(name) {
    if (this.locals.has(name)) {
      return this.locals.get(name);
    }
    if (this.globals.has(name)) {
      return this.globals.get(name);
    }
    return null;
  }

  isTruthy(value) {
    if (value === null || value === undefined || value === false) return false;
    if (value === 0 || value === '') return false;
    return true;
  }

  stringify(value) {
    if (value === null || value === undefined) return '';
    if (Array.isArray(value)) return `[${value.join(', ')}]`;
    return String(value);
  }

  requestBreak() {
    this.breakRequested = true;
  }
}
