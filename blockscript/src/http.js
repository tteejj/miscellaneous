// HTTP and Networking Support

export class HTTP {
  constructor(options = {}) {
    this.baseURL = options.baseURL || '';
    this.timeout = options.timeout || 30000;
    this.headers = options.headers || {};
  }

  // GET request
  async get(url, options = {}) {
    const fullURL = this.buildURL(url);
    const headers = { ...this.headers, ...options.headers };

    try {
      const response = await fetch(fullURL, {
        method: 'GET',
        headers,
        signal: this.createTimeout(options.timeout || this.timeout),
      });

      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // POST request
  async post(url, data, options = {}) {
    const fullURL = this.buildURL(url);
    const headers = {
      'Content-Type': 'application/json',
      ...this.headers,
      ...options.headers,
    };

    try {
      const response = await fetch(fullURL, {
        method: 'POST',
        headers,
        body: JSON.stringify(data),
        signal: this.createTimeout(options.timeout || this.timeout),
      });

      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // PUT request
  async put(url, data, options = {}) {
    const fullURL = this.buildURL(url);
    const headers = {
      'Content-Type': 'application/json',
      ...this.headers,
      ...options.headers,
    };

    try {
      const response = await fetch(fullURL, {
        method: 'PUT',
        headers,
        body: JSON.stringify(data),
        signal: this.createTimeout(options.timeout || this.timeout),
      });

      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // DELETE request
  async delete(url, options = {}) {
    const fullURL = this.buildURL(url);
    const headers = { ...this.headers, ...options.headers };

    try {
      const response = await fetch(fullURL, {
        method: 'DELETE',
        headers,
        signal: this.createTimeout(options.timeout || this.timeout),
      });

      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Download file
  async download(url, options = {}) {
    const fullURL = this.buildURL(url);

    try {
      const response = await fetch(fullURL);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();

      return {
        success: true,
        data: blob,
        size: blob.size,
        type: blob.type,
      };
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Upload file
  async upload(url, file, options = {}) {
    const fullURL = this.buildURL(url);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(fullURL, {
        method: 'POST',
        body: formData,
        headers: { ...this.headers, ...options.headers },
      });

      return await this.handleResponse(response);
    } catch (error) {
      return this.handleError(error);
    }
  }

  // Helper methods
  buildURL(url) {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      return url;
    }
    return this.baseURL + url;
  }

  createTimeout(ms) {
    const controller = new AbortController();
    setTimeout(() => controller.abort(), ms);
    return controller.signal;
  }

  async handleResponse(response) {
    const contentType = response.headers.get('content-type');

    let data;
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    return {
      success: response.ok,
      status: response.status,
      statusText: response.statusText,
      data,
      headers: Object.fromEntries(response.headers.entries()),
    };
  }

  handleError(error) {
    return {
      success: false,
      error: error.message,
      type: error.name,
    };
  }

  // Set default headers
  setHeader(key, value) {
    this.headers[key] = value;
  }

  // Remove header
  removeHeader(key) {
    delete this.headers[key];
  }

  // Set base URL
  setBaseURL(url) {
    this.baseURL = url;
  }
}

// Simple HTTP server for testing
export class SimpleServer {
  constructor(port = 3000) {
    this.port = port;
    this.routes = new Map();
    this.middleware = [];
  }

  // Add route
  get(path, handler) {
    this.routes.set(`GET ${path}`, handler);
  }

  post(path, handler) {
    this.routes.set(`POST ${path}`, handler);
  }

  put(path, handler) {
    this.routes.set(`PUT ${path}`, handler);
  }

  delete(path, handler) {
    this.routes.set(`DELETE ${path}`, handler);
  }

  // Add middleware
  use(middleware) {
    this.middleware.push(middleware);
  }

  // Static file serving
  static(directory) {
    this.middleware.push((req, res) => {
      // Simplified static file serving
      return null;
    });
  }

  // Start server
  listen(callback) {
    console.log(`Server would start on port ${this.port}`);
    if (callback) callback();
  }

  // Handle request
  async handleRequest(method, path, body) {
    const key = `${method} ${path}`;
    const handler = this.routes.get(key);

    if (handler) {
      const req = { method, path, body };
      const res = {
        json: (data) => ({ type: 'json', data }),
        send: (data) => ({ type: 'text', data }),
        status: (code) => ({ statusCode: code }),
      };

      return await handler(req, res);
    }

    return { statusCode: 404, data: 'Not Found' };
  }
}

// WebSocket support
export class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.callbacks = {
      onOpen: null,
      onMessage: null,
      onClose: null,
      onError: null,
    };
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          if (this.callbacks.onOpen) {
            this.callbacks.onOpen();
          }
          resolve();
        };

        this.ws.onmessage = (event) => {
          if (this.callbacks.onMessage) {
            this.callbacks.onMessage(event.data);
          }
        };

        this.ws.onclose = () => {
          if (this.callbacks.onClose) {
            this.callbacks.onClose();
          }
        };

        this.ws.onerror = (error) => {
          if (this.callbacks.onError) {
            this.callbacks.onError(error);
          }
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
    }
  }

  close() {
    if (this.ws) {
      this.ws.close();
    }
  }

  on(event, callback) {
    const eventMap = {
      'open': 'onOpen',
      'message': 'onMessage',
      'close': 'onClose',
      'error': 'onError',
    };

    const callbackName = eventMap[event];
    if (callbackName) {
      this.callbacks[callbackName] = callback;
    }
  }
}

// HTTP operations for interpreter
export const httpOperations = {
  get: async (url) => new HTTP().get(url),
  post: async (url, data) => new HTTP().post(url, data),
  put: async (url, data) => new HTTP().put(url, data),
  delete: async (url) => new HTTP().delete(url),
  download: async (url) => new HTTP().download(url),
};
