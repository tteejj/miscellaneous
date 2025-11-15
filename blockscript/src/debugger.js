// Debugger - Step-through debugging with breakpoints

export class Debugger {
  constructor(interpreter) {
    this.interpreter = interpreter;
    this.breakpoints = new Set();
    this.watches = new Map();
    this.callStack = [];
    this.stepMode = false;
    this.stepOver = false;
    this.stepOut = false;
    this.paused = false;
    this.currentLine = null;
    this.history = [];
    this.callbacks = {
      onBreakpoint: null,
      onStep: null,
      onVariableChange: null,
      onError: null,
    };
  }

  // Breakpoint management
  addBreakpoint(line, condition = null) {
    this.breakpoints.add({ line, condition });
  }

  removeBreakpoint(line) {
    this.breakpoints = new Set([...this.breakpoints].filter(bp => bp.line !== line));
  }

  clearBreakpoints() {
    this.breakpoints.clear();
  }

  listBreakpoints() {
    return [...this.breakpoints];
  }

  hasBreakpoint(line) {
    return [...this.breakpoints].some(bp => bp.line === line);
  }

  // Watch expressions
  addWatch(name, expression) {
    this.watches.set(name, expression);
  }

  removeWatch(name) {
    this.watches.delete(name);
  }

  getWatches() {
    return new Map(this.watches);
  }

  evaluateWatches() {
    const results = {};
    for (const [name, expression] of this.watches) {
      try {
        // Evaluate watch expression
        results[name] = this.interpreter.evaluateExpression(expression);
      } catch (error) {
        results[name] = `<error: ${error.message}>`;
      }
    }
    return results;
  }

  // Stepping controls
  stepInto() {
    this.stepMode = true;
    this.stepOver = false;
    this.stepOut = false;
    this.resume();
  }

  stepOver() {
    this.stepMode = true;
    this.stepOver = true;
    this.stepOut = false;
    this.resume();
  }

  stepOut() {
    this.stepMode = true;
    this.stepOver = false;
    this.stepOut = true;
    this.resume();
  }

  continue() {
    this.stepMode = false;
    this.resume();
  }

  pause() {
    this.paused = true;
  }

  resume() {
    this.paused = false;
  }

  // Call stack management
  pushCall(functionName, line, args) {
    this.callStack.push({
      function: functionName,
      line,
      args,
      timestamp: Date.now(),
    });

    if (this.callStack.length > 1000) {
      throw new Error('Stack overflow: Maximum call stack size exceeded');
    }
  }

  popCall() {
    return this.callStack.pop();
  }

  getCallStack() {
    return [...this.callStack];
  }

  // Execution tracking
  beforeStatement(node) {
    this.currentLine = node.line;

    // Record in history
    this.history.push({
      line: node.line,
      type: node.type,
      timestamp: Date.now(),
    });

    // Keep history limited
    if (this.history.length > 10000) {
      this.history = this.history.slice(-5000);
    }

    // Check breakpoint
    const breakpoint = [...this.breakpoints].find(bp => bp.line === node.line);
    if (breakpoint) {
      // Check condition if present
      if (!breakpoint.condition || this.evaluateCondition(breakpoint.condition)) {
        this.paused = true;
        if (this.callbacks.onBreakpoint) {
          this.callbacks.onBreakpoint(node.line, breakpoint);
        }
      }
    }

    // Step mode handling
    if (this.stepMode) {
      this.paused = true;
      if (this.callbacks.onStep) {
        this.callbacks.onStep(node.line, node);
      }

      if (this.stepOver && node.type === 'FunctionCall') {
        // Skip function internals
        this.stepMode = false;
      }
    }

    // Wait while paused
    while (this.paused && !this.stepMode) {
      // Busy wait (in real implementation, use async/await)
      // This is simplified for demonstration
    }
  }

  afterStatement(node) {
    // Track variable changes
    const currentVars = this.interpreter.globals;
    if (this.callbacks.onVariableChange) {
      // Compare with previous state
      this.callbacks.onVariableChange(currentVars);
    }
  }

  evaluateCondition(condition) {
    try {
      // Parse and evaluate condition
      return true; // Simplified
    } catch {
      return false;
    }
  }

  // State inspection
  getCurrentState() {
    return {
      line: this.currentLine,
      variables: this.interpreter.globals,
      callStack: this.getCallStack(),
      watches: this.evaluateWatches(),
      breakpoints: this.listBreakpoints(),
      paused: this.paused,
      stepMode: this.stepMode,
    };
  }

  // Execution history
  getHistory(limit = 100) {
    return this.history.slice(-limit);
  }

  // Performance profiling
  getProfile() {
    const profile = {
      totalStatements: this.history.length,
      lineFrequency: {},
      typeFrequency: {},
      functionCalls: this.callStack.length,
    };

    this.history.forEach(entry => {
      // Count line frequency
      profile.lineFrequency[entry.line] = (profile.lineFrequency[entry.line] || 0) + 1;

      // Count type frequency
      profile.typeFrequency[entry.type] = (profile.typeFrequency[entry.type] || 0) + 1;
    });

    return profile;
  }

  // Timeline of execution
  getTimeline() {
    return this.history.map(entry => ({
      line: entry.line,
      type: entry.type,
      timestamp: entry.timestamp,
    }));
  }

  // Hot spots (most executed lines)
  getHotSpots(limit = 10) {
    const frequency = {};
    this.history.forEach(entry => {
      frequency[entry.line] = (frequency[entry.line] || 0) + 1;
    });

    return Object.entries(frequency)
      .sort(([, a], [, b]) => b - a)
      .slice(0, limit)
      .map(([line, count]) => ({ line: parseInt(line), count }));
  }

  // Reset debugger state
  reset() {
    this.callStack = [];
    this.history = [];
    this.currentLine = null;
    this.paused = false;
    this.stepMode = false;
  }

  // Event callbacks
  on(event, callback) {
    if (this.callbacks.hasOwnProperty('on' + event.charAt(0).toUpperCase() + event.slice(1))) {
      this.callbacks['on' + event.charAt(0).toUpperCase() + event.slice(1)] = callback;
    }
  }
}

// Debug information extractor
export class DebugInfo {
  constructor(ast, source) {
    this.ast = ast;
    this.source = source;
    this.lines = source.split('\n');
  }

  // Get source line
  getLine(lineNumber) {
    return this.lines[lineNumber - 1] || '';
  }

  // Get context around a line
  getContext(lineNumber, radius = 2) {
    const start = Math.max(1, lineNumber - radius);
    const end = Math.min(this.lines.length, lineNumber + radius);

    const context = [];
    for (let i = start; i <= end; i++) {
      context.push({
        line: i,
        content: this.lines[i - 1],
        current: i === lineNumber,
      });
    }

    return context;
  }

  // Get all function definitions
  getFunctions() {
    const functions = [];

    const walk = (node) => {
      if (!node) return;

      if (node.type === 'FunctionDefinition') {
        functions.push({
          name: node.name,
          parameters: node.parameters,
          line: node.line,
        });
      }

      // Recursively walk
      if (node.statements) {
        node.statements.forEach(walk);
      }
      if (node.body) {
        node.body.forEach(walk);
      }
      if (node.thenBlock) {
        node.thenBlock.forEach(walk);
      }
      if (node.elseBlock) {
        node.elseBlock.forEach(walk);
      }
    };

    walk(this.ast);
    return functions;
  }

  // Get all variable assignments
  getVariables() {
    const variables = new Set();

    const walk = (node) => {
      if (!node) return;

      if (node.type === 'SetStatement') {
        variables.add(node.variable);
      }
      if (node.type === 'ChangeStatement') {
        variables.add(node.variable);
      }

      // Recursively walk
      if (node.statements) {
        node.statements.forEach(walk);
      }
      if (node.body) {
        node.body.forEach(walk);
      }
      if (node.thenBlock) {
        node.thenBlock.forEach(walk);
      }
      if (node.elseBlock) {
        node.elseBlock.forEach(walk);
      }
    };

    walk(this.ast);
    return [...variables];
  }

  // Generate code map
  getCodeMap() {
    const map = {
      functions: this.getFunctions(),
      variables: this.getVariables(),
      totalLines: this.lines.length,
    };

    return map;
  }
}
