// Code Formatter - Beautify BlockScript code

export class Formatter {
  constructor(options = {}) {
    this.indentSize = options.indentSize || 2;
    this.indentChar = options.indentChar || ' ';
    this.maxLineLength = options.maxLineLength || 80;
    this.insertFinalNewline = options.insertFinalNewline !== false;
  }

  format(source) {
    const lines = source.split('\n');
    const formatted = [];
    let indentLevel = 0;
    let inComment = false;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i].trim();

      // Skip empty lines
      if (!line) {
        formatted.push('');
        continue;
      }

      // Preserve comments
      if (line.startsWith('#')) {
        formatted.push(this.getIndent(indentLevel) + line);
        continue;
      }

      // Check for block end first
      if (line === 'end') {
        indentLevel = Math.max(0, indentLevel - 1);
        formatted.push(this.getIndent(indentLevel) + line);
        continue;
      }

      // Format the line
      formatted.push(this.getIndent(indentLevel) + line);

      // Check for block start
      if (this.startsBlock(line)) {
        indentLevel++;
      }

      // Check for else/elsif
      if (line.startsWith('else')) {
        // Don't change indent level
      }
    }

    let result = formatted.join('\n');

    if (this.insertFinalNewline && !result.endsWith('\n')) {
      result += '\n';
    }

    return result;
  }

  getIndent(level) {
    return this.indentChar.repeat(this.indentSize * level);
  }

  startsBlock(line) {
    const blockKeywords = [
      'if ', 'while ', 'for ', 'repeat ', 'forever', 'define ', 'when ',
    ];

    return blockKeywords.some(keyword => line.startsWith(keyword));
  }

  // Format specific constructs
  formatExpression(expr) {
    // Add spacing around operators
    expr = expr.replace(/([+\-*\/=<>!])/g, ' $1 ');
    // Remove double spaces
    expr = expr.replace(/\s+/g, ' ');
    // Trim
    return expr.trim();
  }

  // Minify code (remove unnecessary whitespace)
  minify(source) {
    const lines = source.split('\n');
    const minified = [];

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#')) {
        minified.push(trimmed);
      }
    }

    return minified.join('\n');
  }

  // Format with line length limit
  formatWithWrap(source) {
    const lines = this.format(source).split('\n');
    const wrapped = [];

    for (const line of lines) {
      if (line.length <= this.maxLineLength) {
        wrapped.push(line);
      } else {
        // Try to wrap long lines
        const indent = line.match(/^\s*/)[0];
        const content = line.trim();

        if (content.startsWith('#')) {
          // Don't wrap comments
          wrapped.push(line);
        } else {
          // Smart wrapping at commas or operators
          if (line.length <= maxLength) {
            wrapped.push(line);
          } else {
            // Find good break points (commas, operators)
            const indent = line.match(/^(\s*)/)[1];
            let remaining = line;

            while (remaining.length > maxLength) {
              let breakPoint = maxLength;

              // Look for comma or operator before maxLength
              for (let i = maxLength; i > maxLength * 0.7; i--) {
                const char = remaining[i];
                if (char === ',' || char === '+' || char === '-' || char === '*' || char === '/') {
                  breakPoint = i + 1;
                  break;
                }
              }

              wrapped.push(remaining.substring(0, breakPoint).trimEnd());
              remaining = indent + '  ' + remaining.substring(breakPoint).trimStart();
            }

            if (remaining.trim().length > 0) {
              wrapped.push(remaining);
            }
          }
        }
      }
    }

    return wrapped.join('\n');
  }

  // Add or remove trailing whitespace
  trimTrailingWhitespace(source) {
    return source.split('\n')
      .map(line => line.trimEnd())
      .join('\n');
  }

  // Normalize line endings
  normalizeLineEndings(source, ending = '\n') {
    return source.replace(/\r\n|\r/g, '\n').replace(/\n/g, ending);
  }

  // Sort imports/exports
  sortImports(source) {
    const lines = source.split('\n');
    const imports = [];
    const rest = [];
    let inImports = true;

    for (const line of lines) {
      if (line.trim().startsWith('import ')) {
        imports.push(line);
      } else if (line.trim()) {
        inImports = false;
        rest.push(line);
      } else if (!inImports) {
        rest.push(line);
      }
    }

    imports.sort();

    return [...imports, '', ...rest].join('\n');
  }

  // Add spacing between logical blocks
  addSpacing(source) {
    const lines = source.split('\n');
    const spaced = [];
    let prevLineType = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      if (!line) {
        spaced.push('');
        prevLineType = 'empty';
        continue;
      }

      const currentType = this.getLineType(line);

      // Add blank line between different block types
      if (prevLineType && currentType !== prevLineType && currentType !== 'comment' && prevLineType !== 'empty') {
        if (currentType === 'function' || currentType === 'when') {
          spaced.push('');
        }
      }

      spaced.push(lines[i]);
      prevLineType = currentType;
    }

    return spaced.join('\n');
  }

  getLineType(line) {
    if (line.startsWith('#')) return 'comment';
    if (line.startsWith('define ')) return 'function';
    if (line.startsWith('when ')) return 'when';
    if (line.startsWith('create list')) return 'declaration';
    if (line.startsWith('set ') || line.startsWith('change ')) return 'assignment';
    if (line.startsWith('if ') || line.startsWith('while ') || line.startsWith('for ')) return 'control';
    if (line === 'end') return 'end';
    return 'statement';
  }

  // Full format with all options
  formatFull(source, options = {}) {
    let result = source;

    if (options.trimWhitespace !== false) {
      result = this.trimTrailingWhitespace(result);
    }

    if (options.normalizeEndings !== false) {
      result = this.normalizeLineEndings(result);
    }

    if (options.sortImports) {
      result = this.sortImports(result);
    }

    if (options.addSpacing !== false) {
      result = this.addSpacing(result);
    }

    result = this.format(result);

    return result;
  }
}

// Style guide checker
export class StyleChecker {
  constructor() {
    this.rules = {
      maxLineLength: 80,
      indentSize: 2,
      requireFinalNewline: true,
      noTrailingWhitespace: true,
      preferSingleQuotes: false,
      requireSpaceAfterKeywords: true,
      requireSpaceAroundOperators: true,
    };
  }

  check(source) {
    const issues = [];
    const lines = source.split('\n');

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const lineNum = i + 1;

      // Check line length
      if (line.length > this.rules.maxLineLength) {
        issues.push({
          line: lineNum,
          column: this.rules.maxLineLength,
          message: `Line exceeds maximum length of ${this.rules.maxLineLength}`,
          severity: 'warning',
          rule: 'max-line-length',
        });
      }

      // Check trailing whitespace
      if (this.rules.noTrailingWhitespace && line.endsWith(' ')) {
        issues.push({
          line: lineNum,
          column: line.length,
          message: 'Trailing whitespace',
          severity: 'info',
          rule: 'no-trailing-whitespace',
        });
      }

      // Check indentation
      const indent = line.match(/^\s*/)[0].length;
      if (indent % this.rules.indentSize !== 0) {
        issues.push({
          line: lineNum,
          column: 1,
          message: `Indentation should be a multiple of ${this.rules.indentSize}`,
          severity: 'warning',
          rule: 'indent',
        });
      }

      // Check spacing after keywords
      if (this.rules.requireSpaceAfterKeywords) {
        const keywords = ['if', 'while', 'for', 'set', 'define'];
        keywords.forEach(keyword => {
          const pattern = new RegExp(`\\b${keyword}\\S`);
          if (pattern.test(line)) {
            issues.push({
              line: lineNum,
              column: line.indexOf(keyword),
              message: `Missing space after keyword '${keyword}'`,
              severity: 'warning',
              rule: 'space-after-keyword',
            });
          }
        });
      }
    }

    // Check final newline
    if (this.rules.requireFinalNewline && !source.endsWith('\n')) {
      issues.push({
        line: lines.length,
        column: lines[lines.length - 1].length,
        message: 'Missing final newline',
        severity: 'info',
        rule: 'final-newline',
      });
    }

    return issues;
  }

  setRule(name, value) {
    if (this.rules.hasOwnProperty(name)) {
      this.rules[name] = value;
    }
  }

  getRule(name) {
    return this.rules[name];
  }
}
