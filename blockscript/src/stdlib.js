// Standard Library - Built-in functions and utilities

export const stdlib = {
  // Math functions
  math: {
    random: (from, to) => Math.floor(Math.random() * (to - from + 1)) + from,
    abs: (x) => Math.abs(x),
    round: (x) => Math.round(x),
    floor: (x) => Math.floor(x),
    ceil: (x) => Math.ceil(x),
    sqrt: (x) => Math.sqrt(x),
    pow: (base, exp) => Math.pow(base, exp),
    min: (...args) => Math.min(...args),
    max: (...args) => Math.max(...args),

    // Trigonometry
    sin: (x) => Math.sin(x),
    cos: (x) => Math.cos(x),
    tan: (x) => Math.tan(x),
    asin: (x) => Math.asin(x),
    acos: (x) => Math.acos(x),
    atan: (x) => Math.atan(x),
    atan2: (y, x) => Math.atan2(y, x),

    // Constants
    PI: Math.PI,
    E: Math.E,

    // Advanced
    log: (x) => Math.log(x),
    log10: (x) => Math.log10(x),
    exp: (x) => Math.exp(x),
    clamp: (value, min, max) => Math.min(Math.max(value, min), max),
    lerp: (a, b, t) => a + (b - a) * t,
    map: (value, inMin, inMax, outMin, outMax) => {
      return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
    },
  },

  // String functions
  string: {
    join: (a, b) => String(a) + String(b),
    length: (str) => String(str).length,
    letter: (index, str) => String(str)[index - 1] || '',
    uppercase: (str) => String(str).toUpperCase(),
    lowercase: (str) => String(str).toLowerCase(),
    trim: (str) => String(str).trim(),
    replace: (str, search, replacement) => String(str).replace(search, replacement),
    replaceAll: (str, search, replacement) => String(str).replaceAll(search, replacement),
    split: (str, separator) => String(str).split(separator),
    substring: (str, start, end) => String(str).substring(start - 1, end),
    indexOf: (str, search) => String(str).indexOf(search) + 1, // 1-based
    contains: (str, search) => String(str).includes(search),
    startsWith: (str, search) => String(str).startsWith(search),
    endsWith: (str, search) => String(str).endsWith(search),
    repeat: (str, count) => String(str).repeat(count),
    reverse: (str) => String(str).split('').reverse().join(''),
    padStart: (str, length, char) => String(str).padStart(length, char),
    padEnd: (str, length, char) => String(str).padEnd(length, char),
  },

  // List/Array functions
  list: {
    length: (list) => Array.isArray(list) ? list.length : 0,
    push: (list, item) => { list.push(item); return list; },
    pop: (list) => list.pop(),
    shift: (list) => list.shift(),
    unshift: (list, item) => { list.unshift(item); return list; },
    reverse: (list) => { list.reverse(); return list; },
    sort: (list) => { list.sort((a, b) => a - b); return list; },
    sortAlpha: (list) => { list.sort(); return list; },
    shuffle: (list) => {
      for (let i = list.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [list[i], list[j]] = [list[j], list[i]];
      }
      return list;
    },
    slice: (list, start, end) => list.slice(start - 1, end),
    concat: (list1, list2) => list1.concat(list2),
    indexOf: (list, item) => list.indexOf(item) + 1, // 1-based
    contains: (list, item) => list.includes(item),
    filter: (list, predicate) => list.filter(predicate),
    map: (list, transform) => list.map(transform),
    reduce: (list, reducer, initial) => list.reduce(reducer, initial),
    sum: (list) => list.reduce((a, b) => a + b, 0),
    average: (list) => list.reduce((a, b) => a + b, 0) / list.length,
    min: (list) => Math.min(...list),
    max: (list) => Math.max(...list),
    unique: (list) => [...new Set(list)],
    flatten: (list) => list.flat(Infinity),
    join: (list, separator) => list.join(separator || ''),
  },

  // Type checking
  type: {
    isNumber: (value) => typeof value === 'number' && !isNaN(value),
    isString: (value) => typeof value === 'string',
    isList: (value) => Array.isArray(value),
    isBoolean: (value) => typeof value === 'boolean',
    isNull: (value) => value === null || value === undefined,
    typeof: (value) => {
      if (Array.isArray(value)) return 'list';
      if (value === null || value === undefined) return 'null';
      return typeof value;
    },
  },

  // Conversion
  convert: {
    toNumber: (value) => Number(value),
    toString: (value) => String(value),
    toBoolean: (value) => Boolean(value),
    toList: (value) => {
      if (Array.isArray(value)) return value;
      if (typeof value === 'string') return value.split('');
      return [value];
    },
    parseInt: (str, radix) => parseInt(str, radix || 10),
    parseFloat: (str) => parseFloat(str),
  },

  // Date and Time
  time: {
    now: () => Date.now(),
    timestamp: () => Math.floor(Date.now() / 1000),
    year: () => new Date().getFullYear(),
    month: () => new Date().getMonth() + 1,
    day: () => new Date().getDate(),
    hour: () => new Date().getHours(),
    minute: () => new Date().getMinutes(),
    second: () => new Date().getSeconds(),
    millisecond: () => new Date().getMilliseconds(),
    dayOfWeek: () => new Date().getDay(),
    formatDate: (timestamp) => new Date(timestamp).toLocaleDateString(),
    formatTime: (timestamp) => new Date(timestamp).toLocaleTimeString(),
    formatDateTime: (timestamp) => new Date(timestamp).toLocaleString(),
  },

  // Console/Debug
  console: {
    log: (...args) => console.log(...args),
    error: (...args) => console.error(...args),
    warn: (...args) => console.warn(...args),
    info: (...args) => console.info(...args),
    clear: () => console.clear(),
    table: (data) => console.table(data),
  },

  // Data structures
  data: {
    createMap: () => new Map(),
    createSet: () => new Set(),
    createStack: () => ({ items: [], push: (x) => this.items.push(x), pop: () => this.items.pop() }),
    createQueue: () => ({
      items: [],
      enqueue: (x) => this.items.push(x),
      dequeue: () => this.items.shift(),
      peek: () => this.items[0],
    }),
  },

  // JSON
  json: {
    parse: (str) => JSON.parse(str),
    stringify: (obj) => JSON.stringify(obj),
    stringifyPretty: (obj) => JSON.stringify(obj, null, 2),
  },

  // Color utilities (for graphics)
  color: {
    rgb: (r, g, b) => `rgb(${r}, ${g}, ${b})`,
    rgba: (r, g, b, a) => `rgba(${r}, ${g}, ${b}, ${a})`,
    hsl: (h, s, l) => `hsl(${h}, ${s}%, ${l}%)`,
    hsla: (h, s, l, a) => `hsla(${h}, ${s}%, ${l}%, ${a})`,
    hex: (r, g, b) => '#' + [r, g, b].map(x => {
      const hex = Math.round(x).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join(''),
    random: () => '#' + Math.floor(Math.random()*16777215).toString(16),
  },

  // Validation
  validate: {
    isEmail: (str) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(str),
    isURL: (str) => {
      try { new URL(str); return true; } catch { return false; }
    },
    isPhone: (str) => /^\+?[\d\s-()]+$/.test(str),
    isAlpha: (str) => /^[a-zA-Z]+$/.test(str),
    isAlphaNumeric: (str) => /^[a-zA-Z0-9]+$/.test(str),
    isNumeric: (str) => /^[0-9]+$/.test(str),
    isEmpty: (value) => {
      if (value === null || value === undefined) return true;
      if (typeof value === 'string') return value.trim() === '';
      if (Array.isArray(value)) return value.length === 0;
      return false;
    },
  },

  // Utility
  util: {
    sleep: (ms) => new Promise(resolve => setTimeout(resolve, ms)),
    range: (start, end, step = 1) => {
      const result = [];
      for (let i = start; i <= end; i += step) {
        result.push(i);
      }
      return result;
    },
    repeat: (fn, times) => {
      for (let i = 0; i < times; i++) {
        fn(i);
      }
    },
    times: (n, value) => Array(n).fill(value),
    identity: (x) => x,
    constant: (x) => () => x,
    noop: () => {},
    assert: (condition, message) => {
      if (!condition) throw new Error(message || 'Assertion failed');
    },
    deepClone: (obj) => JSON.parse(JSON.stringify(obj)),
    deepEqual: (a, b) => JSON.stringify(a) === JSON.stringify(b),
  },
};

// Helper to get standard library function
export function getStdlibFunction(namespace, name) {
  if (stdlib[namespace] && stdlib[namespace][name]) {
    return stdlib[namespace][name];
  }
  return null;
}

// Get all available stdlib functions
export function getStdlibFunctions() {
  const functions = [];
  for (const namespace in stdlib) {
    for (const name in stdlib[namespace]) {
      functions.push(`${namespace}.${name}`);
    }
  }
  return functions;
}
