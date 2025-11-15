// File I/O Operations

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync, mkdirSync, unlinkSync, appendFileSync } from 'fs';
import { resolve, basename, dirname, extname, join } from 'path';

export class FileSystem {
  constructor(options = {}) {
    this.basePath = options.basePath || process.cwd();
    this.allowedPaths = options.allowedPaths || [];
    this.restrictAccess = options.restrictAccess || false;
  }

  // Security check
  checkAccess(filePath) {
    if (!this.restrictAccess) return true;

    const absolute = resolve(this.basePath, filePath);
    if (this.allowedPaths.length === 0) {
      // If no allowed paths, only allow basePath and below
      return absolute.startsWith(this.basePath);
    }

    return this.allowedPaths.some(allowed => {
      const allowedAbs = resolve(this.basePath, allowed);
      return absolute.startsWith(allowedAbs);
    });
  }

  // Read file
  readFile(filePath, encoding = 'utf-8') {
    if (!this.checkAccess(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }

    const absolute = resolve(this.basePath, filePath);
    if (!existsSync(absolute)) {
      throw new Error(`File not found: ${filePath}`);
    }

    return readFileSync(absolute, encoding);
  }

  // Write file
  writeFile(filePath, content, encoding = 'utf-8') {
    if (!this.checkAccess(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }

    const absolute = resolve(this.basePath, filePath);

    // Create directory if it doesn't exist
    const dir = dirname(absolute);
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
    }

    writeFileSync(absolute, content, encoding);
    return true;
  }

  // Append to file
  appendFile(filePath, content, encoding = 'utf-8') {
    if (!this.checkAccess(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }

    const absolute = resolve(this.basePath, filePath);
    appendFileSync(absolute, content, encoding);
    return true;
  }

  // Delete file
  deleteFile(filePath) {
    if (!this.checkAccess(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }

    const absolute = resolve(this.basePath, filePath);
    if (!existsSync(absolute)) {
      throw new Error(`File not found: ${filePath}`);
    }

    unlinkSync(absolute);
    return true;
  }

  // Check if file exists
  exists(filePath) {
    if (!this.checkAccess(filePath)) {
      return false;
    }

    const absolute = resolve(this.basePath, filePath);
    return existsSync(absolute);
  }

  // List files in directory
  listFiles(dirPath = '.') {
    if (!this.checkAccess(dirPath)) {
      throw new Error(`Access denied: ${dirPath}`);
    }

    const absolute = resolve(this.basePath, dirPath);
    if (!existsSync(absolute)) {
      throw new Error(`Directory not found: ${dirPath}`);
    }

    return readdirSync(absolute);
  }

  // Get file info
  getInfo(filePath) {
    if (!this.checkAccess(filePath)) {
      throw new Error(`Access denied: ${filePath}`);
    }

    const absolute = resolve(this.basePath, filePath);
    if (!existsSync(absolute)) {
      throw new Error(`File not found: ${filePath}`);
    }

    const stats = statSync(absolute);
    return {
      size: stats.size,
      isFile: stats.isFile(),
      isDirectory: stats.isDirectory(),
      created: stats.birthtime,
      modified: stats.mtime,
      accessed: stats.atime,
    };
  }

  // Create directory
  createDir(dirPath) {
    if (!this.checkAccess(dirPath)) {
      throw new Error(`Access denied: ${dirPath}`);
    }

    const absolute = resolve(this.basePath, dirPath);
    mkdirSync(absolute, { recursive: true });
    return true;
  }

  // Path utilities
  resolvePath(filePath) {
    return resolve(this.basePath, filePath);
  }

  basename(filePath) {
    return basename(filePath);
  }

  dirname(filePath) {
    return dirname(filePath);
  }

  extname(filePath) {
    return extname(filePath);
  }

  join(...paths) {
    return join(...paths);
  }

  // Read lines from file
  readLines(filePath, encoding = 'utf-8') {
    const content = this.readFile(filePath, encoding);
    return content.split('\n');
  }

  // Write lines to file
  writeLines(filePath, lines, encoding = 'utf-8') {
    const content = lines.join('\n');
    return this.writeFile(filePath, content, encoding);
  }

  // Read JSON
  readJSON(filePath) {
    const content = this.readFile(filePath, 'utf-8');
    return JSON.parse(content);
  }

  // Write JSON
  writeJSON(filePath, data, pretty = false) {
    const content = pretty ? JSON.stringify(data, null, 2) : JSON.stringify(data);
    return this.writeFile(filePath, content, 'utf-8');
  }

  // Read CSV (simple implementation)
  readCSV(filePath, delimiter = ',') {
    const lines = this.readLines(filePath);
    return lines.map(line => line.split(delimiter).map(cell => cell.trim()));
  }

  // Write CSV
  writeCSV(filePath, data, delimiter = ',') {
    const lines = data.map(row => row.join(delimiter));
    return this.writeLines(filePath, lines);
  }
}

// File I/O operations for interpreter
export const fileOperations = {
  read: (path) => new FileSystem().readFile(path),
  write: (path, content) => new FileSystem().writeFile(path, content),
  append: (path, content) => new FileSystem().appendFile(path, content),
  delete: (path) => new FileSystem().deleteFile(path),
  exists: (path) => new FileSystem().exists(path),
  list: (path) => new FileSystem().listFiles(path),
  info: (path) => new FileSystem().getInfo(path),
  readJSON: (path) => new FileSystem().readJSON(path),
  writeJSON: (path, data, pretty) => new FileSystem().writeJSON(path, data, pretty),
  readLines: (path) => new FileSystem().readLines(path),
  writeLines: (path, lines) => new FileSystem().writeLines(path, lines),
  readCSV: (path, delimiter) => new FileSystem().readCSV(path, delimiter),
  writeCSV: (path, data, delimiter) => new FileSystem().writeCSV(path, data, delimiter),
};
