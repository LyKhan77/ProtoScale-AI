<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue';
import { useThemeStore } from '../stores/theme';

const canvasRef = ref(null);
const theme = useThemeStore();

const props = defineProps({
  count: { type: Number, default: 75 },
  interactionRadius: { type: Number, default: 200 }
});

let ctx = null;
let animationFrameId = null;
let stars = [];
let width = 0;
let height = 0;

// Mouse State
const mouse = { x: -1000, y: -1000 };

class Star {
  constructor() {
    this.init();
  }

  init() {
    this.x = Math.random() * width;
    this.y = Math.random() * height;
    this.vx = (Math.random() - 0.5) * 0.2; // Base drift velocity
    this.vy = (Math.random() - 0.5) * 0.2;
    this.radius = Math.random() * 2.5 + 1.0;
    this.baseColor = theme.isDark ? '#00AFB9' : '#564D4D'; // Teal (Dark) vs Dark Grey (Light)
    this.alpha = Math.random() * 0.5 + 0.1;
  }

  update() {
    // 1. Base movement
    this.x += this.vx;
    this.y += this.vy;

    // 2. Mouse Interaction (Gravity)
    const dx = mouse.x - this.x;
    const dy = mouse.y - this.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < props.interactionRadius) {
      const force = (props.interactionRadius - distance) / props.interactionRadius;
      const angle = Math.atan2(dy, dx);
      
      const pushX = Math.cos(angle) * force * 0.5; // Attraction strength
      const pushY = Math.sin(angle) * force * 0.5;

      this.vx += pushX * 0.05;
      this.vy += pushY * 0.05;
    }

    // 3. Friction (Damping)
    this.vx *= 0.98;
    this.vy *= 0.98;

    // 4. Screen Wrap
    if (this.x < 0) this.x = width;
    if (this.x > width) this.x = 0;
    if (this.y < 0) this.y = height;
    if (this.y > height) this.y = 0;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.baseColor;
    ctx.globalAlpha = this.alpha;
    ctx.fill();
    ctx.globalAlpha = 1.0;
  }
}

function resize() {
  if (!canvasRef.value) return;
  width = window.innerWidth;
  height = window.innerHeight;
  canvasRef.value.width = width;
  canvasRef.value.height = height;
  
  // Re-init stars on resize to distribute them
  stars = Array.from({ length: props.count }, () => new Star());
}

function animate() {
  if (!ctx) return;
  
  ctx.clearRect(0, 0, width, height);
  
  stars.forEach(star => {
    star.update();
    star.draw();
  });

  // Connecting lines for nearby stars (Constellation effect)
  stars.forEach((star, i) => {
    for (let j = i + 1; j < stars.length; j++) {
      const other = stars[j];
      const dx = star.x - other.x;
      const dy = star.y - other.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 100) {
        ctx.beginPath();
        ctx.strokeStyle = theme.isDark ? '#00AFB9' : '#564D4D';
        ctx.globalAlpha = (1 - dist / 100) * 0.15; // Very subtle lines
        ctx.lineWidth = 0.5;
        ctx.moveTo(star.x, star.y);
        ctx.lineTo(other.x, other.y);
        ctx.stroke();
        ctx.globalAlpha = 1.0;
      }
    }
  });

  animationFrameId = requestAnimationFrame(animate);
}

function handleMouseMove(e) {
  const rect = canvasRef.value.getBoundingClientRect();
  mouse.x = e.clientX - rect.left;
  mouse.y = e.clientY - rect.top;
}

// Watch theme changes to update star colors immediately
watch(() => theme.isDark, (newVal) => {
  const newColor = newVal ? '#00AFB9' : '#564D4D';
  stars.forEach(star => star.baseColor = newColor);
});

onMounted(() => {
  ctx = canvasRef.value.getContext('2d');
  resize();
  window.addEventListener('resize', resize);
  window.addEventListener('mousemove', handleMouseMove);
  animate();
});

onUnmounted(() => {
  window.removeEventListener('resize', resize);
  window.removeEventListener('mousemove', handleMouseMove);
  cancelAnimationFrame(animationFrameId);
});
</script>

<template>
  <canvas 
    ref="canvasRef" 
    class="fixed inset-0 pointer-events-none z-0"
  />
</template>
