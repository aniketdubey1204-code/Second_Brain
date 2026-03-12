'use client';

import React, { useEffect, useRef } from 'react';

export default function LiquidBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let particles: Particle[] = [];
    let pulses: Pulse[] = [];
    let bioCells: BioCell[] = [];
    
    const particleCount = 60;
    const connectionDistance = 180;
    const bioCellCount = 40;

    const getTheme = () => document.documentElement.getAttribute('data-theme') || 'cyber-dark';
    
    const getThemeColor = () => {
      return getComputedStyle(document.documentElement)
        .getPropertyValue('--theme-accent')
        .trim() || '#00f2ff';
    };

    const hexToRgb = (hex: string) => {
      const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
      hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : '0, 242, 255';
    };

    // --- CYBER-DARK CLASSES ---
    class Particle {
      x: number; y: number; vx: number; vy: number; size: number;
      constructor(width: number, height: number) {
        this.x = Math.random() * width; this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 0.3; this.vy = (Math.random() - 0.5) * 0.3;
        this.size = Math.random() * 2 + 1;
      }
      update(width: number, height: number) {
        this.x += this.vx; this.y += this.vy;
        if (this.x < 0 || this.x > width) this.vx *= -1;
        if (this.y < 0 || this.y > height) this.vy *= -1;
      }
      draw(ctx: CanvasRenderingContext2D, themeColor: string) {
        ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = themeColor; ctx.globalAlpha = 0.4; ctx.fill(); ctx.globalAlpha = 1.0;
        ctx.shadowBlur = 10; ctx.shadowColor = themeColor;
      }
    }

    class Pulse {
      p1: Particle; p2: Particle; progress: number; speed: number;
      constructor(p1: Particle, p2: Particle) {
        this.p1 = p1; this.p2 = p2; this.progress = 0; this.speed = 0.005 + Math.random() * 0.01;
      }
      update() { this.progress += this.speed; return this.progress < 1; }
      draw(ctx: CanvasRenderingContext2D, themeColor: string) {
        const x = this.p1.x + (this.p2.x - this.p1.x) * this.progress;
        const y = this.p1.y + (this.p2.y - this.p1.y) * this.progress;
        ctx.beginPath(); ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fillStyle = themeColor; ctx.shadowBlur = 15; ctx.shadowColor = themeColor; ctx.fill();
        ctx.shadowBlur = 0;
      }
    }

    // --- BIO-SYMBIOTE & LIQUID-GLASS CLASSES ---
    class BioCell {
      x: number; y: number; vx: number; vy: number; radius: number;
      angle: number; speed: number; wobble: number;
      
      constructor(width: number, height: number) {
        this.x = Math.random() * width; this.y = Math.random() * height;
        this.vx = (Math.random() - 0.5) * 0.5; this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 40 + 20;
        this.angle = Math.random() * Math.PI * 2;
        this.speed = Math.random() * 0.02 + 0.01;
        this.wobble = Math.random() * 10 + 5;
      }
      update(width: number, height: number) {
        this.x += this.vx; this.y += this.vy;
        if (this.x < -this.radius) this.x = width + this.radius;
        if (this.x > width + this.radius) this.x = -this.radius;
        if (this.y < -this.radius) this.y = height + this.radius;
        if (this.y > height + this.radius) this.y = -this.radius;
        this.angle += this.speed;
      }
      draw(ctx: CanvasRenderingContext2D, themeColor: string) {
        // Wobble effect for organic feel
        const r = this.radius + Math.sin(this.angle) * this.wobble;
        ctx.beginPath();
        ctx.arc(this.x, this.y, r, 0, Math.PI * 2);
        
        const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, r);
        gradient.addColorStop(0, `rgba(${hexToRgb(themeColor)}, 0.15)`);
        gradient.addColorStop(1, `rgba(${hexToRgb(themeColor)}, 0)`);
        
        ctx.fillStyle = gradient;
        ctx.fill();
      }
    }

    const init = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      particles = []; pulses = []; bioCells = [];
      for (let i = 0; i < particleCount; i++) particles.push(new Particle(canvas.width, canvas.height));
      for (let i = 0; i < bioCellCount; i++) bioCells.push(new BioCell(canvas.width, canvas.height));
    };

    const animate = () => {
      const theme = getTheme();
      
      // Create trailing effect only for bio symbiote to feel slimy/fluid
      if (theme === "bio-symbiote") {
         ctx.fillStyle = "rgba(5, 10, 5, 0.2)";
         ctx.fillRect(0, 0, canvas.width, canvas.height);
      } else {
         ctx.clearRect(0, 0, canvas.width, canvas.height);
      }

      ctx.shadowBlur = 0; 
      const themeColor = getThemeColor();
      const rgbColor = hexToRgb(themeColor);

      if (theme === "cyber-dark") {
          // Render particles & network
          for (let i = 0; i < particles.length; i++) {
            particles[i].update(canvas.width, canvas.height);
            particles[i].draw(ctx, themeColor);
            for (let j = i + 1; j < particles.length; j++) {
              const dx = particles[i].x - particles[j].x;
              const dy = particles[i].y - particles[j].y;
              const distance = Math.sqrt(dx * dx + dy * dy);
              if (distance < connectionDistance) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                const opacity = 1 - distance / connectionDistance;
                ctx.strokeStyle = `rgba(${rgbColor}, ${opacity * 0.15})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
                
                if (Math.random() > 0.9995 && pulses.length < 20) pulses.push(new Pulse(particles[i], particles[j]));
              }
            }
          }
          pulses = pulses.filter(pulse => {
            const alive = pulse.update();
            if (alive) pulse.draw(ctx, themeColor);
            return alive;
          });
      } else if (theme === "bio-symbiote") {
          // Render organic floating cells / tendrils
          for (let i = 0; i < bioCells.length; i++) {
            bioCells[i].update(canvas.width, canvas.height);
            bioCells[i].draw(ctx, themeColor);
            
            // Draw slimy connections
            for (let j = i + 1; j < bioCells.length; j++) {
              const dx = bioCells[i].x - bioCells[j].x;
              const dy = bioCells[i].y - bioCells[j].y;
              const distance = Math.sqrt(dx * dx + dy * dy);
              if (distance < connectionDistance * 1.5) {
                ctx.beginPath();
                ctx.moveTo(bioCells[i].x, bioCells[i].y);
                ctx.lineTo(bioCells[j].x, bioCells[j].y);
                
                const opacity = Math.pow(1 - distance / (connectionDistance * 1.5), 2);
                ctx.strokeStyle = `rgba(${rgbColor}, ${opacity * 0.1})`;
                ctx.lineWidth = opacity * 15; // thick tendrils
                ctx.lineCap = "round";
                ctx.stroke();
              }
            }
          }
      } else if (theme === "liquid-glass") {
          // iOS 26 Aesthetic: Vibrant ambient orbs with soft blending
          ctx.save();
          ctx.globalCompositeOperation = 'lighter';
          
          const colors = [
            '120, 100, 255', // Purple
            '80, 160, 255',  // Blue
            '255, 100, 200', // Pink
            '100, 255, 200'  // Cyan-ish
          ];

          for (let i = 0; i < bioCells.length / 2; i++) {
             bioCells[i].update(canvas.width, canvas.height);
             
             // Dynamic color based on index
             const color = colors[i % colors.length];
             const r = bioCells[i].radius * (4 + Math.sin(bioCells[i].angle) * 2); // Pulsating size
             
             ctx.beginPath();
             const gradient = ctx.createRadialGradient(
               bioCells[i].x, bioCells[i].y, 0, 
               bioCells[i].x, bioCells[i].y, r
             );
             gradient.addColorStop(0, `rgba(${color}, 0.12)`);
             gradient.addColorStop(0.5, `rgba(${color}, 0.04)`);
             gradient.addColorStop(1, `rgba(${color}, 0)`);
             
             ctx.fillStyle = gradient;
             ctx.arc(bioCells[i].x, bioCells[i].y, r, 0, Math.PI * 2);
             ctx.fill();
          }
          ctx.restore();
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    const handleResize = () => init();
    window.addEventListener('resize', handleResize);
    init();
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="fixed inset-0 w-full h-full overflow-hidden pointer-events-none z-0">
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full opacity-60"
        aria-hidden="true"
      />
      {/* Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.7)_100%)]" />
    </div>
  );
}
