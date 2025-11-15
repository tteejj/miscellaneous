// Parser - Builds AST from tokens

import { TokenType } from './lexer.js';

// AST Node Types
export class ASTNode {
  constructor(type, line, column) {
    this.type = type;
    this.line = line;
    this.column = column;
  }
}

export class Program extends ASTNode {
  constructor(statements) {
    super('Program', 1, 1);
    this.statements = statements;
  }
}

export class SetStatement extends ASTNode {
  constructor(variable, value, line, column) {
    super('SetStatement', line, column);
    this.variable = variable;
    this.value = value;
  }
}

export class ChangeStatement extends ASTNode {
  constructor(variable, value, line, column) {
    super('ChangeStatement', line, column);
    this.variable = variable;
    this.value = value;
  }
}

export class SayStatement extends ASTNode {
  constructor(value, line, column) {
    super('SayStatement', line, column);
    this.value = value;
  }
}

export class PrintStatement extends ASTNode {
  constructor(value, line, column) {
    super('PrintStatement', line, column);
    this.value = value;
  }
}

export class AskStatement extends ASTNode {
  constructor(prompt, line, column) {
    super('AskStatement', line, column);
    this.prompt = prompt;
  }
}

export class IfStatement extends ASTNode {
  constructor(condition, thenBlock, elseBlock, line, column) {
    super('IfStatement', line, column);
    this.condition = condition;
    this.thenBlock = thenBlock;
    this.elseBlock = elseBlock;
  }
}

export class RepeatStatement extends ASTNode {
  constructor(count, body, line, column) {
    super('RepeatStatement', line, column);
    this.count = count;
    this.body = body;
  }
}

export class ForeverStatement extends ASTNode {
  constructor(body, line, column) {
    super('ForeverStatement', line, column);
    this.body = body;
  }
}

export class WhileStatement extends ASTNode {
  constructor(condition, body, line, column) {
    super('WhileStatement', line, column);
    this.condition = condition;
    this.body = body;
  }
}

export class ForStatement extends ASTNode {
  constructor(variable, start, end, body, line, column) {
    super('ForStatement', line, column);
    this.variable = variable;
    this.start = start;
    this.end = end;
    this.body = body;
  }
}

export class CreateListStatement extends ASTNode {
  constructor(name, line, column) {
    super('CreateListStatement', line, column);
    this.name = name;
  }
}

export class AddToListStatement extends ASTNode {
  constructor(value, listName, line, column) {
    super('AddToListStatement', line, column);
    this.value = value;
    this.listName = listName;
  }
}

export class DeleteFromListStatement extends ASTNode {
  constructor(index, listName, line, column) {
    super('DeleteFromListStatement', line, column);
    this.index = index;
    this.listName = listName;
  }
}

export class FunctionDefinition extends ASTNode {
  constructor(name, parameters, body, line, column) {
    super('FunctionDefinition', line, column);
    this.name = name;
    this.parameters = parameters;
    this.body = body;
  }
}

export class ReturnStatement extends ASTNode {
  constructor(value, line, column) {
    super('ReturnStatement', line, column);
    this.value = value;
  }
}

export class WhenStatement extends ASTNode {
  constructor(event, body, line, column) {
    super('WhenStatement', line, column);
    this.event = event;
    this.body = body;
  }
}

export class BinaryExpression extends ASTNode {
  constructor(left, operator, right, line, column) {
    super('BinaryExpression', line, column);
    this.left = left;
    this.operator = operator;
    this.right = right;
  }
}

export class UnaryExpression extends ASTNode {
  constructor(operator, operand, line, column) {
    super('UnaryExpression', line, column);
    this.operator = operator;
    this.operand = operand;
  }
}

export class FunctionCall extends ASTNode {
  constructor(name, args, line, column) {
    super('FunctionCall', line, column);
    this.name = name;
    this.args = args;
  }
}

export class ListAccess extends ASTNode {
  constructor(index, listName, line, column) {
    super('ListAccess', line, column);
    this.index = index;
    this.listName = listName;
  }
}

export class ListAssignment extends ASTNode {
  constructor(index, listName, value, line, column) {
    super('ListAssignment', line, column);
    this.index = index;
    this.listName = listName;
    this.value = value;
  }
}

export class Literal extends ASTNode {
  constructor(value, line, column) {
    super('Literal', line, column);
    this.value = value;
  }
}

export class Identifier extends ASTNode {
  constructor(name, line, column) {
    super('Identifier', line, column);
    this.name = name;
  }
}

export class Parser {
  constructor(tokens) {
    this.tokens = tokens.filter(t => t.type !== TokenType.NEWLINE);
    this.pos = 0;
  }

  peek(offset = 0) {
    return this.tokens[this.pos + offset] || this.tokens[this.tokens.length - 1];
  }

  advance() {
    return this.tokens[this.pos++];
  }

  expect(type) {
    const token = this.peek();
    if (token.type !== type) {
      throw new Error(
        `Expected ${type} but got ${token.type} at line ${token.line}, column ${token.column}`
      );
    }
    return this.advance();
  }

  match(...types) {
    for (const type of types) {
      if (this.peek().type === type) {
        return this.advance();
      }
    }
    return null;
  }

  isAtEnd() {
    return this.peek().type === TokenType.EOF;
  }

  parse() {
    const statements = [];
    while (!this.isAtEnd()) {
      const stmt = this.parseStatement();
      if (stmt) statements.push(stmt);
    }
    return new Program(statements);
  }

  parseStatement() {
    const token = this.peek();

    switch (token.type) {
      case TokenType.SET:
        return this.parseSetStatement();
      case TokenType.CHANGE:
        return this.parseChangeStatement();
      case TokenType.SAY:
        return this.parseSayStatement();
      case TokenType.PRINT:
        return this.parsePrintStatement();
      case TokenType.ASK:
        return this.parseAskStatement();
      case TokenType.IF:
        return this.parseIfStatement();
      case TokenType.REPEAT:
        return this.parseRepeatStatement();
      case TokenType.FOREVER:
        return this.parseForeverStatement();
      case TokenType.WHILE:
        return this.parseWhileStatement();
      case TokenType.FOR:
        return this.parseForStatement();
      case TokenType.CREATE:
        return this.parseCreateListStatement();
      case TokenType.ADD:
        return this.parseAddToListStatement();
      case TokenType.DELETE:
        return this.parseDeleteFromListStatement();
      case TokenType.DEFINE:
        return this.parseFunctionDefinition();
      case TokenType.RETURN:
        return this.parseReturnStatement();
      case TokenType.WHEN:
        return this.parseWhenStatement();
      case TokenType.CALL:
        return this.parseFunctionCall();
      default:
        throw new Error(
          `Unexpected token ${token.type} at line ${token.line}, column ${token.column}`
        );
    }
  }

  parseSetStatement() {
    const token = this.advance(); // consume 'set'

    // Check for list item assignment: set item X of LIST to VALUE
    if (this.peek().type === TokenType.ITEM) {
      this.advance(); // consume 'item'
      const index = this.parseExpression();
      this.expect(TokenType.OF);
      const listName = this.expect(TokenType.IDENTIFIER).value;
      this.expect(TokenType.TO);
      const value = this.parseExpression();
      return new ListAssignment(index, listName, value, token.line, token.column);
    }

    const variable = this.expect(TokenType.IDENTIFIER).value;
    this.expect(TokenType.TO);
    const value = this.parseExpression();
    return new SetStatement(variable, value, token.line, token.column);
  }

  parseChangeStatement() {
    const token = this.advance(); // consume 'change'
    const variable = this.expect(TokenType.IDENTIFIER).value;
    this.expect(TokenType.BY);
    const value = this.parseExpression();
    return new ChangeStatement(variable, value, token.line, token.column);
  }

  parseSayStatement() {
    const token = this.advance(); // consume 'say'
    const value = this.parseExpression();
    return new SayStatement(value, token.line, token.column);
  }

  parsePrintStatement() {
    const token = this.advance(); // consume 'print'
    const value = this.parseExpression();
    return new PrintStatement(value, token.line, token.column);
  }

  parseAskStatement() {
    const token = this.advance(); // consume 'ask'
    const prompt = this.parseExpression();
    return new AskStatement(prompt, token.line, token.column);
  }

  parseIfStatement() {
    const token = this.advance(); // consume 'if'
    const condition = this.parseExpression();
    this.expect(TokenType.THEN);

    const thenBlock = [];
    while (!this.isAtEnd() && this.peek().type !== TokenType.ELSE && this.peek().type !== TokenType.END) {
      thenBlock.push(this.parseStatement());
    }

    let elseBlock = [];
    if (this.match(TokenType.ELSE)) {
      while (!this.isAtEnd() && this.peek().type !== TokenType.END) {
        elseBlock.push(this.parseStatement());
      }
    }

    this.expect(TokenType.END);
    return new IfStatement(condition, thenBlock, elseBlock, token.line, token.column);
  }

  parseRepeatStatement() {
    const token = this.advance(); // consume 'repeat'
    const count = this.parseExpression();
    this.expect(TokenType.TIMES);

    const body = [];
    while (!this.isAtEnd() && this.peek().type !== TokenType.END) {
      body.push(this.parseStatement());
    }

    this.expect(TokenType.END);
    return new RepeatStatement(count, body, token.line, token.column);
  }

  parseForeverStatement() {
    const token = this.advance(); // consume 'forever'

    const body = [];
    while (!this.isAtEnd() && this.peek().type !== TokenType.END) {
      body.push(this.parseStatement());
    }

    this.expect(TokenType.END);
    return new ForeverStatement(body, token.line, token.column);
  }

  parseWhileStatement() {
    const token = this.advance(); // consume 'while'
    const condition = this.parseExpression();
    this.expect(TokenType.THEN);

    const body = [];
    while (!this.isAtEnd() && this.peek().type !== TokenType.END) {
      body.push(this.parseStatement());
    }

    this.expect(TokenType.END);
    return new WhileStatement(condition, body, token.line, token.column);
  }

  parseForStatement() {
    const token = this.advance(); // consume 'for'
    const variable = this.expect(TokenType.IDENTIFIER).value;
    this.expect(TokenType.FROM);
    const start = this.parseExpression();
    this.expect(TokenType.TO);
    const end = this.parseExpression();

    const body = [];
    while (!this.isAtEnd() && this.peek().type !== TokenType.END) {
      body.push(this.parseStatement());
    }

    this.expect(TokenType.END);
    return new ForStatement(variable, start, end, body, token.line, token.column);
  }

  parseCreateListStatement() {
    const token = this.advance(); // consume 'create'
    this.expect(TokenType.LIST);
    const name = this.expect(TokenType.IDENTIFIER).value;
    return new CreateListStatement(name, token.line, token.column);
  }

  parseAddToListStatement() {
    const token = this.advance(); // consume 'add'
    const value = this.parseExpression();
    this.expect(TokenType.TO);
    const listName = this.expect(TokenType.IDENTIFIER).value;
    return new AddToListStatement(value, listName, token.line, token.column);
  }

  parseDeleteFromListStatement() {
    const token = this.advance(); // consume 'delete'
    this.expect(TokenType.ITEM);
    const index = this.parseExpression();
    this.expect(TokenType.OF);
    const listName = this.expect(TokenType.IDENTIFIER).value;
    return new DeleteFromListStatement(index, listName, token.line, token.column);
  }

  parseFunctionDefinition() {
    const token = this.advance(); // consume 'define'
    // Allow keywords as function names
    const nameToken = this.advance();
    const name = nameToken.value;

    const parameters = [];
    if (this.match(TokenType.WITH)) {
      // Allow keywords as parameter names
      const paramToken = this.advance();
      parameters.push(paramToken.value);
      while (this.match(TokenType.COMMA)) {
        const nextParam = this.advance();
        parameters.push(nextParam.value);
      }
    }

    const body = [];
    while (!this.isAtEnd() && this.peek().type !== TokenType.END) {
      body.push(this.parseStatement());
    }

    this.expect(TokenType.END);
    return new FunctionDefinition(name, parameters, body, token.line, token.column);
  }

  parseReturnStatement() {
    const token = this.advance(); // consume 'return'
    const value = this.parseExpression();
    return new ReturnStatement(value, token.line, token.column);
  }

  parseWhenStatement() {
    const token = this.advance(); // consume 'when'

    // Parse event description
    let event = '';
    while (!this.isAtEnd() && this.peek().type !== TokenType.THEN && this.peek().type !== TokenType.END) {
      const t = this.advance();
      event += t.value + ' ';
    }
    event = event.trim();

    const body = [];
    while (!this.isAtEnd() && this.peek().type !== TokenType.END) {
      body.push(this.parseStatement());
    }

    this.expect(TokenType.END);
    return new WhenStatement(event, body, token.line, token.column);
  }

  parseFunctionCall() {
    const token = this.advance(); // consume 'call'
    // Allow keywords as function names
    const nameToken = this.advance();
    const name = nameToken.value;

    const args = [];
    if (this.match(TokenType.WITH)) {
      args.push(this.parseExpression());
      while (this.match(TokenType.COMMA)) {
        args.push(this.parseExpression());
      }
    }

    return new FunctionCall(name, args, token.line, token.column);
  }

  parseExpression() {
    return this.parseLogicalOr();
  }

  parseLogicalOr() {
    let left = this.parseLogicalAnd();

    while (this.match(TokenType.OR)) {
      const operator = 'or';
      const right = this.parseLogicalAnd();
      left = new BinaryExpression(left, operator, right, left.line, left.column);
    }

    return left;
  }

  parseLogicalAnd() {
    let left = this.parseLogicalNot();

    while (this.match(TokenType.AND)) {
      const operator = 'and';
      const right = this.parseLogicalNot();
      left = new BinaryExpression(left, operator, right, left.line, left.column);
    }

    return left;
  }

  parseLogicalNot() {
    if (this.match(TokenType.NOT)) {
      const operand = this.parseLogicalNot();
      return new UnaryExpression('not', operand, operand.line, operand.column);
    }

    return this.parseComparison();
  }

  parseComparison() {
    let left = this.parseAdditive();

    const token = this.peek();
    if (this.match(TokenType.EQUAL)) {
      const right = this.parseAdditive();
      return new BinaryExpression(left, '=', right, token.line, token.column);
    } else if (this.match(TokenType.NOT_EQUAL)) {
      const right = this.parseAdditive();
      return new BinaryExpression(left, '!=', right, token.line, token.column);
    } else if (this.match(TokenType.GREATER)) {
      const right = this.parseAdditive();
      return new BinaryExpression(left, '>', right, token.line, token.column);
    } else if (this.match(TokenType.LESS)) {
      const right = this.parseAdditive();
      return new BinaryExpression(left, '<', right, token.line, token.column);
    } else if (this.match(TokenType.GREATER_EQUAL)) {
      const right = this.parseAdditive();
      return new BinaryExpression(left, '>=', right, token.line, token.column);
    } else if (this.match(TokenType.LESS_EQUAL)) {
      const right = this.parseAdditive();
      return new BinaryExpression(left, '<=', right, token.line, token.column);
    }

    return left;
  }

  parseAdditive() {
    let left = this.parseMultiplicative();

    while (true) {
      const token = this.peek();
      if (this.match(TokenType.PLUS)) {
        const right = this.parseMultiplicative();
        left = new BinaryExpression(left, '+', right, token.line, token.column);
      } else if (this.match(TokenType.MINUS)) {
        const right = this.parseMultiplicative();
        left = new BinaryExpression(left, '-', right, token.line, token.column);
      } else {
        break;
      }
    }

    return left;
  }

  parseMultiplicative() {
    let left = this.parsePower();

    while (true) {
      const token = this.peek();
      if (this.match(TokenType.MULTIPLY)) {
        const right = this.parsePower();
        left = new BinaryExpression(left, '*', right, token.line, token.column);
      } else if (this.match(TokenType.DIVIDE)) {
        const right = this.parsePower();
        left = new BinaryExpression(left, '/', right, token.line, token.column);
      } else if (this.match(TokenType.MOD)) {
        const right = this.parsePower();
        left = new BinaryExpression(left, 'mod', right, token.line, token.column);
      } else {
        break;
      }
    }

    return left;
  }

  parsePower() {
    let left = this.parseUnary();

    if (this.match(TokenType.POWER)) {
      const token = this.tokens[this.pos - 1];
      const right = this.parsePower(); // right associative
      return new BinaryExpression(left, '^', right, token.line, token.column);
    }

    return left;
  }

  parseUnary() {
    if (this.match(TokenType.MINUS)) {
      const token = this.tokens[this.pos - 1];
      const operand = this.parseUnary();
      return new UnaryExpression('-', operand, token.line, token.column);
    }

    return this.parseBuiltInFunction();
  }

  parseBuiltInFunction() {
    const token = this.peek();

    // Handle built-in functions
    if (this.match(TokenType.JOIN)) {
      // Use parseComparison to avoid consuming 'and' as a logical operator
      const left = this.parseComparison();
      this.expect(TokenType.AND);
      const right = this.parseComparison();
      return new FunctionCall('join', [left, right], token.line, token.column);
    }

    if (this.match(TokenType.LENGTH)) {
      this.expect(TokenType.OF);
      const value = this.parseExpression();
      return new FunctionCall('length', [value], token.line, token.column);
    }

    if (this.match(TokenType.LETTER)) {
      const index = this.parseExpression();
      this.expect(TokenType.OF);
      const str = this.parseExpression();
      return new FunctionCall('letter', [index, str], token.line, token.column);
    }

    if (this.match(TokenType.RANDOM)) {
      this.expect(TokenType.FROM);
      const from = this.parseExpression();
      this.expect(TokenType.TO);
      const to = this.parseExpression();
      return new FunctionCall('random', [from, to], token.line, token.column);
    }

    if (this.match(TokenType.ABS, TokenType.ROUND, TokenType.FLOOR, TokenType.CEIL, TokenType.SQRT, TokenType.SIN, TokenType.COS, TokenType.TAN)) {
      const funcName = this.tokens[this.pos - 1].value;
      this.expect(TokenType.OF);
      const value = this.parseExpression();
      return new FunctionCall(funcName, [value], token.line, token.column);
    }

    if (this.match(TokenType.POW, TokenType.MIN, TokenType.MAX)) {
      const funcName = this.tokens[this.pos - 1].value;
      this.expect(TokenType.OF);
      const arg1 = this.parseExpression();
      const args = [arg1];
      while (this.match(TokenType.COMMA)) {
        args.push(this.parseExpression());
      }
      return new FunctionCall(funcName, args, token.line, token.column);
    }

    // Check for "item X of LIST"
    if (this.match(TokenType.ITEM)) {
      const index = this.parseExpression();
      this.expect(TokenType.OF);
      const listName = this.expect(TokenType.IDENTIFIER).value;
      return new ListAccess(index, listName, token.line, token.column);
    }

    // Check for "call FUNC with args"
    if (this.match(TokenType.CALL)) {
      // Allow keywords as function names
      const nameToken = this.advance();
      const name = nameToken.value;
      const args = [];
      if (this.match(TokenType.WITH)) {
        args.push(this.parseExpression());
        while (this.match(TokenType.COMMA)) {
          args.push(this.parseExpression());
        }
      }
      return new FunctionCall(name, args, token.line, token.column);
    }

    return this.parsePrimary();
  }

  parsePrimary() {
    const token = this.peek();

    if (this.match(TokenType.NUMBER)) {
      return new Literal(this.tokens[this.pos - 1].value, token.line, token.column);
    }

    if (this.match(TokenType.STRING)) {
      return new Literal(this.tokens[this.pos - 1].value, token.line, token.column);
    }

    if (this.match(TokenType.TRUE)) {
      return new Literal(true, token.line, token.column);
    }

    if (this.match(TokenType.FALSE)) {
      return new Literal(false, token.line, token.column);
    }

    if (this.match(TokenType.IDENTIFIER)) {
      return new Identifier(this.tokens[this.pos - 1].value, token.line, token.column);
    }

    if (this.match(TokenType.LPAREN)) {
      const expr = this.parseExpression();
      this.expect(TokenType.RPAREN);
      return expr;
    }

    throw new Error(
      `Unexpected token ${token.type} at line ${token.line}, column ${token.column}`
    );
  }
}
