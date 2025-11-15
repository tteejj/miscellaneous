// Graphics and Canvas Support

export class Graphics {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.width = canvas.width || 800;
    this.height = canvas.height || 600;

    // Sprite system
    this.sprites = new Map();
    this.currentSprite = null;

    // Drawing state
    this.penDown = true;
    this.penColor = '#000000';
    this.penSize = 1;
    this.fillColor = '#000000';

    // Turtle graphics state
    this.x = this.width / 2;
    this.y = this.height / 2;
    this.angle = 0; // degrees, 0 = up

    // Animation
    this.animationFrame = null;
    this.sprites.forEach(sprite => sprite.update());

    this.init();
  }

  init() {
    this.clear();
  }

  // Canvas operations
  clear() {
    this.ctx.clearRect(0, 0, this.width, this.height);
    this.ctx.fillStyle = '#FFFFFF';
    this.ctx.fillRect(0, 0, this.width, this.height);
  }

  setBackgroundColor(color) {
    this.ctx.fillStyle = color;
    this.ctx.fillRect(0, 0, this.width, this.height);
  }

  // Pen operations
  penUp() {
    this.penDown = false;
  }

  penDown() {
    this.penDown = true;
  }

  setPenColor(color) {
    this.penColor = color;
    this.ctx.strokeStyle = color;
  }

  setPenSize(size) {
    this.penSize = size;
    this.ctx.lineWidth = size;
  }

  setFillColor(color) {
    this.fillColor = color;
    this.ctx.fillStyle = color;
  }

  // Turtle graphics
  forward(distance) {
    const newX = this.x + distance * Math.sin(this.angle * Math.PI / 180);
    const newY = this.y - distance * Math.cos(this.angle * Math.PI / 180);

    if (this.penDown) {
      this.ctx.beginPath();
      this.ctx.moveTo(this.x, this.y);
      this.ctx.lineTo(newX, newY);
      this.ctx.stroke();
    }

    this.x = newX;
    this.y = newY;
  }

  backward(distance) {
    this.forward(-distance);
  }

  turnRight(degrees) {
    this.angle = (this.angle + degrees) % 360;
  }

  turnLeft(degrees) {
    this.angle = (this.angle - degrees + 360) % 360;
  }

  setPosition(x, y) {
    this.x = x;
    this.y = y;
  }

  setAngle(degrees) {
    this.angle = degrees % 360;
  }

  goToCenter() {
    this.setPosition(this.width / 2, this.height / 2);
  }

  // Drawing primitives
  drawLine(x1, y1, x2, y2) {
    this.ctx.beginPath();
    this.ctx.moveTo(x1, y1);
    this.ctx.lineTo(x2, y2);
    this.ctx.stroke();
  }

  drawRectangle(x, y, width, height, filled = false) {
    if (filled) {
      this.ctx.fillRect(x, y, width, height);
    } else {
      this.ctx.strokeRect(x, y, width, height);
    }
  }

  drawCircle(x, y, radius, filled = false) {
    this.ctx.beginPath();
    this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
    if (filled) {
      this.ctx.fill();
    } else {
      this.ctx.stroke();
    }
  }

  drawEllipse(x, y, radiusX, radiusY, filled = false) {
    this.ctx.beginPath();
    this.ctx.ellipse(x, y, radiusX, radiusY, 0, 0, 2 * Math.PI);
    if (filled) {
      this.ctx.fill();
    } else {
      this.ctx.stroke();
    }
  }

  drawPolygon(points, filled = false) {
    if (points.length < 2) return;

    this.ctx.beginPath();
    this.ctx.moveTo(points[0].x, points[0].y);

    for (let i = 1; i < points.length; i++) {
      this.ctx.lineTo(points[i].x, points[i].y);
    }

    this.ctx.closePath();

    if (filled) {
      this.ctx.fill();
    } else {
      this.ctx.stroke();
    }
  }

  drawTriangle(x1, y1, x2, y2, x3, y3, filled = false) {
    this.drawPolygon([
      { x: x1, y: y1 },
      { x: x2, y: y2 },
      { x: x3, y: y3 },
    ], filled);
  }

  drawStar(x, y, points, outerRadius, innerRadius, filled = false) {
    const step = Math.PI / points;
    this.ctx.beginPath();

    for (let i = 0; i < 2 * points; i++) {
      const radius = i % 2 === 0 ? outerRadius : innerRadius;
      const angle = i * step - Math.PI / 2;
      const px = x + Math.cos(angle) * radius;
      const py = y + Math.sin(angle) * radius;

      if (i === 0) {
        this.ctx.moveTo(px, py);
      } else {
        this.ctx.lineTo(px, py);
      }
    }

    this.ctx.closePath();

    if (filled) {
      this.ctx.fill();
    } else {
      this.ctx.stroke();
    }
  }

  // Text
  drawText(text, x, y, font = '16px Arial', color = this.fillColor) {
    this.ctx.font = font;
    this.ctx.fillStyle = color;
    this.ctx.fillText(text, x, y);
  }

  // Images
  async loadImage(src) {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve(img);
      img.onerror = reject;
      img.src = src;
    });
  }

  drawImage(image, x, y, width = null, height = null) {
    if (width && height) {
      this.ctx.drawImage(image, x, y, width, height);
    } else {
      this.ctx.drawImage(image, x, y);
    }
  }

  // Effects
  setAlpha(alpha) {
    this.ctx.globalAlpha = alpha;
  }

  setBlendMode(mode) {
    this.ctx.globalCompositeOperation = mode;
  }

  // Transformations
  rotate(angle) {
    this.ctx.rotate(angle * Math.PI / 180);
  }

  scale(x, y = x) {
    this.ctx.scale(x, y);
  }

  translate(x, y) {
    this.ctx.translate(x, y);
  }

  save() {
    this.ctx.save();
  }

  restore() {
    this.ctx.restore();
  }

  // Gradients
  createLinearGradient(x0, y0, x1, y1, colorStops) {
    const gradient = this.ctx.createLinearGradient(x0, y0, x1, y1);
    colorStops.forEach(stop => {
      gradient.addColorStop(stop.position, stop.color);
    });
    return gradient;
  }

  createRadialGradient(x0, y0, r0, x1, y1, r1, colorStops) {
    const gradient = this.ctx.createRadialGradient(x0, y0, r0, x1, y1, r1);
    colorStops.forEach(stop => {
      gradient.addColorStop(stop.position, stop.color);
    });
    return gradient;
  }

  // Patterns
  createPattern(image, repetition = 'repeat') {
    return this.ctx.createPattern(image, repetition);
  }

  // Pixel manipulation
  getPixel(x, y) {
    const imageData = this.ctx.getImageData(x, y, 1, 1);
    return {
      r: imageData.data[0],
      g: imageData.data[1],
      b: imageData.data[2],
      a: imageData.data[3],
    };
  }

  setPixel(x, y, r, g, b, a = 255) {
    const imageData = this.ctx.createImageData(1, 1);
    imageData.data[0] = r;
    imageData.data[1] = g;
    imageData.data[2] = b;
    imageData.data[3] = a;
    this.ctx.putImageData(imageData, x, y);
  }

  // Screenshot
  toDataURL(type = 'image/png') {
    return this.canvas.toDataURL(type);
  }

  toBlob(callback, type = 'image/png', quality = 0.92) {
    return this.canvas.toBlob(callback, type, quality);
  }
}

// Sprite class for game development
export class Sprite {
  constructor(graphics, options = {}) {
    this.graphics = graphics;
    this.x = options.x || 0;
    this.y = options.y || 0;
    this.width = options.width || 50;
    this.height = options.height || 50;
    this.angle = options.angle || 0;
    this.visible = true;
    this.color = options.color || '#FF0000';
    this.image = options.image || null;

    // Physics
    this.velocity = { x: 0, y: 0 };
    this.acceleration = { x: 0, y: 0 };
    this.friction = 0.95;

    // Collision
    this.collidable = true;
  }

  update() {
    // Apply physics
    this.velocity.x += this.acceleration.x;
    this.velocity.y += this.acceleration.y;

    this.velocity.x *= this.friction;
    this.velocity.y *= this.friction;

    this.x += this.velocity.x;
    this.y += this.velocity.y;
  }

  draw() {
    if (!this.visible) return;

    const ctx = this.graphics.ctx;
    ctx.save();

    ctx.translate(this.x, this.y);
    ctx.rotate(this.angle * Math.PI / 180);

    if (this.image) {
      ctx.drawImage(
        this.image,
        -this.width / 2,
        -this.height / 2,
        this.width,
        this.height
      );
    } else {
      ctx.fillStyle = this.color;
      ctx.fillRect(
        -this.width / 2,
        -this.height / 2,
        this.width,
        this.height
      );
    }

    ctx.restore();
  }

  move(dx, dy) {
    this.x += dx;
    this.y += dy;
  }

  moveTo(x, y) {
    this.x = x;
    this.y = y;
  }

  rotate(degrees) {
    this.angle = (this.angle + degrees) % 360;
  }

  setAngle(degrees) {
    this.angle = degrees % 360;
  }

  pointTowards(x, y) {
    const dx = x - this.x;
    const dy = y - this.y;
    this.angle = Math.atan2(dy, dx) * 180 / Math.PI + 90;
  }

  distanceTo(x, y) {
    const dx = x - this.x;
    const dy = y - this.y;
    return Math.sqrt(dx * dx + dy * dy);
  }

  touching(other) {
    if (!this.collidable || !other.collidable) return false;

    return this.x < other.x + other.width &&
           this.x + this.width > other.x &&
           this.y < other.y + other.height &&
           this.y + this.height > other.y;
  }

  touchingEdge() {
    return this.x <= 0 ||
           this.x + this.width >= this.graphics.width ||
           this.y <= 0 ||
           this.y + this.height >= this.graphics.height;
  }

  bounceOffEdge() {
    if (this.x <= 0 || this.x + this.width >= this.graphics.width) {
      this.velocity.x *= -1;
    }
    if (this.y <= 0 || this.y + this.height >= this.graphics.height) {
      this.velocity.y *= -1;
    }
  }

  show() {
    this.visible = true;
  }

  hide() {
    this.visible = false;
  }

  setSize(width, height) {
    this.width = width;
    this.height = height;
  }

  clone() {
    return new Sprite(this.graphics, {
      x: this.x,
      y: this.y,
      width: this.width,
      height: this.height,
      angle: this.angle,
      color: this.color,
      image: this.image,
    });
  }
}

// Animation helpers
export class Animation {
  constructor() {
    this.animations = new Map();
    this.running = false;
  }

  add(name, callback, fps = 60) {
    this.animations.set(name, {
      callback,
      fps,
      lastFrame: 0,
    });
  }

  remove(name) {
    this.animations.delete(name);
  }

  start() {
    this.running = true;
    this.loop();
  }

  stop() {
    this.running = false;
  }

  loop() {
    if (!this.running) return;

    const now = Date.now();

    for (const [name, anim] of this.animations) {
      const interval = 1000 / anim.fps;
      if (now - anim.lastFrame >= interval) {
        anim.callback();
        anim.lastFrame = now;
      }
    }

    requestAnimationFrame(() => this.loop());
  }
}
