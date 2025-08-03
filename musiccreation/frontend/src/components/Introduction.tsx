import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

const Introduction: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // 创建更复杂的粒子系统
    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      opacity: number;
      color: string;
      type: 'circle' | 'square' | 'line';
    }> = [];

    const colors = [
      'rgba(59, 130, 246, 0.6)',   // blue
      'rgba(147, 51, 234, 0.6)',   // purple
      'rgba(236, 72, 153, 0.6)',   // pink
      'rgba(34, 197, 94, 0.6)',    // green
      'rgba(251, 146, 60, 0.6)',   // orange
    ];

    for (let i = 0; i < 150; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 1.5,
        vy: (Math.random() - 0.5) * 1.5,
        size: Math.random() * 4 + 1,
        opacity: Math.random() * 0.8 + 0.2,
        color: colors[Math.floor(Math.random() * colors.length)],
        type: ['circle', 'square', 'line'][Math.floor(Math.random() * 3)] as 'circle' | 'square' | 'line',
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 绘制连接线
      particles.forEach((particle, i) => {
        particles.slice(i + 1).forEach((otherParticle) => {
          const dx = particle.x - otherParticle.x;
          const dy = particle.y - otherParticle.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 100) {
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(otherParticle.x, otherParticle.y);
            ctx.strokeStyle = `rgba(59, 130, 246, ${0.1 * (1 - distance / 100)})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        });
      });

      particles.forEach((particle) => {
        particle.x += particle.vx;
        particle.y += particle.vy;

        // 边界检测
        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;

        // 绘制粒子
        ctx.save();
        ctx.globalAlpha = particle.opacity;
        ctx.fillStyle = particle.color;

        switch (particle.type) {
          case 'circle':
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fill();
            break;
          case 'square':
            ctx.fillRect(particle.x - particle.size, particle.y - particle.size, particle.size * 2, particle.size * 2);
            break;
          case 'line':
            ctx.beginPath();
            ctx.moveTo(particle.x - particle.size, particle.y);
            ctx.lineTo(particle.x + particle.size, particle.y);
            ctx.strokeStyle = particle.color;
            ctx.lineWidth = 2;
            ctx.stroke();
            break;
        }
        ctx.restore();
      });

      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ zIndex: 1 }}
      />

      {/* 额外的背景效果 */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/20 to-black/40 pointer-events-none" />
      
      {/* 动态光效 */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-pink-500/10 rounded-full blur-2xl animate-pulse delay-500" />
      </div>

      <div className="relative z-10 text-center px-4 max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1 }}
          className="space-y-12"
        >
          {/* 主标题 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-6"
          >
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="text-6xl md:text-8xl lg:text-9xl font-black text-white drop-shadow-2xl tracking-tight"
            >
              FeedMusic
            </motion.h1>

            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8 }}
              className="w-24 h-1 bg-gradient-to-r from-blue-500 to-purple-600 mx-auto rounded-full"
            />
          </motion.div>

          {/* 副标题 */}
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
            className="text-2xl md:text-3xl text-gray-200 drop-shadow-lg max-w-3xl mx-auto font-light leading-relaxed"
          >
            发现最新音乐动态，分享你的音乐故事
          </motion.p>

          {/* 描述文字 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
            className="text-lg text-gray-300 drop-shadow-lg max-w-4xl mx-auto leading-relaxed space-y-4"
          >
            <p className="text-xl">
              欢迎来到FeedMusic，这里是音乐爱好者的聚集地。
            </p>
            <p>
              我们致力于为您提供最新、最热门的音乐资讯，让您第一时间了解音乐界的动态。
              无论您是音乐创作者、乐评人还是音乐爱好者，这里都有属于您的一片天地。
            </p>
          </motion.div>

          {/* 特性卡片 */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.5 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16"
          >
            {[
              {
                title: '最新资讯',
                description: '实时更新音乐界最新动态和热门话题',
                icon: '🎵',
                color: 'from-blue-500/20 to-blue-600/20',
              },
              {
                title: '社区互动',
                description: '与音乐爱好者分享观点，交流心得',
                icon: '💬',
                color: 'from-purple-500/20 to-purple-600/20',
              },
              {
                title: '创作平台',
                description: '为音乐创作者提供展示和交流的平台',
                icon: '🎤',
                color: 'from-pink-500/20 to-pink-600/20',
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.8 + index * 0.1 }}
                className={`bg-gradient-to-br ${feature.color} backdrop-blur-md rounded-2xl p-8 border border-white/10 hover:border-white/20 transition-all duration-300 hover:scale-105`}
              >
                <div className="text-6xl mb-6">{feature.icon}</div>
                <h3 className="text-2xl font-bold text-white mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-300 text-lg leading-relaxed">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* 滚动提示 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2.5 }}
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="text-white/60 text-sm"
            >
              向下滚动查看更多
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
};

export default Introduction; 