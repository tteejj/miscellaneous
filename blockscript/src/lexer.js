// Lexer - Tokenizes BlockScript source code

export const TokenType = {
  // Keywords
  SET: 'SET',
  TO: 'TO',
  CHANGE: 'CHANGE',
  BY: 'BY',
  SAY: 'SAY',
  PRINT: 'PRINT',
  ASK: 'ASK',
  IF: 'IF',
  THEN: 'THEN',
  ELSE: 'ELSE',
  END: 'END',
  REPEAT: 'REPEAT',
  TIMES: 'TIMES',
  FOREVER: 'FOREVER',
  WHILE: 'WHILE',
  FOR: 'FOR',
  FROM: 'FROM',
  CREATE: 'CREATE',
  LIST: 'LIST',
  ADD: 'ADD',
  DELETE: 'DELETE',
  ITEM: 'ITEM',
  OF: 'OF',
  DEFINE: 'DEFINE',
  WITH: 'WITH',
  CALL: 'CALL',
  RETURN: 'RETURN',
  WHEN: 'WHEN',
  PROGRAM: 'PROGRAM',
  STARTS: 'STARTS',
  KEY: 'KEY',
  PRESSED: 'PRESSED',

  // Operators
  PLUS: 'PLUS',
  MINUS: 'MINUS',
  MULTIPLY: 'MULTIPLY',
  DIVIDE: 'DIVIDE',
  MOD: 'MOD',
  POWER: 'POWER',

  // Comparison
  EQUAL: 'EQUAL',
  NOT_EQUAL: 'NOT_EQUAL',
  GREATER: 'GREATER',
  LESS: 'LESS',
  GREATER_EQUAL: 'GREATER_EQUAL',
  LESS_EQUAL: 'LESS_EQUAL',

  // Logical
  AND: 'AND',
  OR: 'OR',
  NOT: 'NOT',

  // Built-ins
  JOIN: 'JOIN',
  LENGTH: 'LENGTH',
  LETTER: 'LETTER',
  RANDOM: 'RANDOM',
  ABS: 'ABS',
  ROUND: 'ROUND',
  SQRT: 'SQRT',
  SIN: 'SIN',
  COS: 'COS',
  TAN: 'TAN',

  // Literals
  NUMBER: 'NUMBER',
  STRING: 'STRING',
  IDENTIFIER: 'IDENTIFIER',
  TRUE: 'TRUE',
  FALSE: 'FALSE',

  // Punctuation
  LPAREN: 'LPAREN',
  RPAREN: 'RPAREN',
  LBRACKET: 'LBRACKET',
  RBRACKET: 'RBRACKET',
  COMMA: 'COMMA',

  // Special
  NEWLINE: 'NEWLINE',
  EOF: 'EOF',
};

const KEYWORDS = {
  'set': TokenType.SET,
  'to': TokenType.TO,
  'change': TokenType.CHANGE,
  'by': TokenType.BY,
  'say': TokenType.SAY,
  'print': TokenType.PRINT,
  'ask': TokenType.ASK,
  'if': TokenType.IF,
  'then': TokenType.THEN,
  'else': TokenType.ELSE,
  'end': TokenType.END,
  'repeat': TokenType.REPEAT,
  'times': TokenType.TIMES,
  'forever': TokenType.FOREVER,
  'while': TokenType.WHILE,
  'for': TokenType.FOR,
  'from': TokenType.FROM,
  'create': TokenType.CREATE,
  'list': TokenType.LIST,
  'add': TokenType.ADD,
  'delete': TokenType.DELETE,
  'item': TokenType.ITEM,
  'of': TokenType.OF,
  'define': TokenType.DEFINE,
  'with': TokenType.WITH,
  'call': TokenType.CALL,
  'return': TokenType.RETURN,
  'when': TokenType.WHEN,
  'program': TokenType.PROGRAM,
  'starts': TokenType.STARTS,
  'key': TokenType.KEY,
  'pressed': TokenType.PRESSED,
  'mod': TokenType.MOD,
  'and': TokenType.AND,
  'or': TokenType.OR,
  'not': TokenType.NOT,
  'join': TokenType.JOIN,
  'length': TokenType.LENGTH,
  'letter': TokenType.LETTER,
  'random': TokenType.RANDOM,
  'abs': TokenType.ABS,
  'round': TokenType.ROUND,
  'sqrt': TokenType.SQRT,
  'sin': TokenType.SIN,
  'cos': TokenType.COS,
  'tan': TokenType.TAN,
  'true': TokenType.TRUE,
  'false': TokenType.FALSE,
};

export class Token {
  constructor(type, value, line, column) {
    this.type = type;
    this.value = value;
    this.line = line;
    this.column = column;
  }
}

export class Lexer {
  constructor(source) {
    this.source = source;
    this.pos = 0;
    this.line = 1;
    this.column = 1;
    this.tokens = [];
  }

  peek(offset = 0) {
    return this.source[this.pos + offset];
  }

  advance() {
    const ch = this.source[this.pos];
    this.pos++;
    if (ch === '\n') {
      this.line++;
      this.column = 1;
    } else {
      this.column++;
    }
    return ch;
  }

  isAtEnd() {
    return this.pos >= this.source.length;
  }

  skipWhitespace() {
    while (!this.isAtEnd() && /[ \t\r]/.test(this.peek())) {
      this.advance();
    }
  }

  skipComment() {
    if (this.peek() === '#') {
      while (!this.isAtEnd() && this.peek() !== '\n') {
        this.advance();
      }
    }
  }

  readNumber() {
    const startLine = this.line;
    const startCol = this.column;
    let num = '';

    while (!this.isAtEnd() && /[0-9.]/.test(this.peek())) {
      num += this.advance();
    }

    return new Token(TokenType.NUMBER, parseFloat(num), startLine, startCol);
  }

  readString() {
    const startLine = this.line;
    const startCol = this.column;
    const quote = this.advance(); // consume opening quote
    let str = '';

    while (!this.isAtEnd() && this.peek() !== quote) {
      if (this.peek() === '\\') {
        this.advance();
        const next = this.advance();
        switch (next) {
          case 'n': str += '\n'; break;
          case 't': str += '\t'; break;
          case 'r': str += '\r'; break;
          case '\\': str += '\\'; break;
          case '"': str += '"'; break;
          case "'": str += "'"; break;
          default: str += next;
        }
      } else {
        str += this.advance();
      }
    }

    if (!this.isAtEnd()) {
      this.advance(); // consume closing quote
    }

    return new Token(TokenType.STRING, str, startLine, startCol);
  }

  readIdentifier() {
    const startLine = this.line;
    const startCol = this.column;
    let id = '';

    while (!this.isAtEnd() && /[a-zA-Z0-9_]/.test(this.peek())) {
      id += this.advance();
    }

    const type = KEYWORDS[id.toLowerCase()] || TokenType.IDENTIFIER;
    return new Token(type, id, startLine, startCol);
  }

  tokenize() {
    while (!this.isAtEnd()) {
      this.skipWhitespace();

      if (this.isAtEnd()) break;

      // Skip comments
      if (this.peek() === '#') {
        this.skipComment();
        continue;
      }

      const startLine = this.line;
      const startCol = this.column;
      const ch = this.peek();

      // Newlines
      if (ch === '\n') {
        this.advance();
        this.tokens.push(new Token(TokenType.NEWLINE, '\\n', startLine, startCol));
        continue;
      }

      // Numbers
      if (/[0-9]/.test(ch)) {
        this.tokens.push(this.readNumber());
        continue;
      }

      // Strings
      if (ch === '"' || ch === "'") {
        this.tokens.push(this.readString());
        continue;
      }

      // Identifiers and keywords
      if (/[a-zA-Z_]/.test(ch)) {
        this.tokens.push(this.readIdentifier());
        continue;
      }

      // Operators and punctuation
      switch (ch) {
        case '+':
          this.advance();
          this.tokens.push(new Token(TokenType.PLUS, '+', startLine, startCol));
          break;
        case '-':
          this.advance();
          this.tokens.push(new Token(TokenType.MINUS, '-', startLine, startCol));
          break;
        case '*':
          this.advance();
          this.tokens.push(new Token(TokenType.MULTIPLY, '*', startLine, startCol));
          break;
        case '/':
          this.advance();
          this.tokens.push(new Token(TokenType.DIVIDE, '/', startLine, startCol));
          break;
        case '^':
          this.advance();
          this.tokens.push(new Token(TokenType.POWER, '^', startLine, startCol));
          break;
        case '(':
          this.advance();
          this.tokens.push(new Token(TokenType.LPAREN, '(', startLine, startCol));
          break;
        case ')':
          this.advance();
          this.tokens.push(new Token(TokenType.RPAREN, ')', startLine, startCol));
          break;
        case '[':
          this.advance();
          this.tokens.push(new Token(TokenType.LBRACKET, '[', startLine, startCol));
          break;
        case ']':
          this.advance();
          this.tokens.push(new Token(TokenType.RBRACKET, ']', startLine, startCol));
          break;
        case ',':
          this.advance();
          this.tokens.push(new Token(TokenType.COMMA, ',', startLine, startCol));
          break;
        case '=':
          this.advance();
          this.tokens.push(new Token(TokenType.EQUAL, '=', startLine, startCol));
          break;
        case '>':
          this.advance();
          if (this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.GREATER_EQUAL, '>=', startLine, startCol));
          } else {
            this.tokens.push(new Token(TokenType.GREATER, '>', startLine, startCol));
          }
          break;
        case '<':
          this.advance();
          if (this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.LESS_EQUAL, '<=', startLine, startCol));
          } else {
            this.tokens.push(new Token(TokenType.LESS, '<', startLine, startCol));
          }
          break;
        case '!':
          this.advance();
          if (this.peek() === '=') {
            this.advance();
            this.tokens.push(new Token(TokenType.NOT_EQUAL, '!=', startLine, startCol));
          }
          break;
        default:
          throw new Error(`Unexpected character '${ch}' at line ${startLine}, column ${startCol}`);
      }
    }

    this.tokens.push(new Token(TokenType.EOF, null, this.line, this.column));
    return this.tokens;
  }
}
