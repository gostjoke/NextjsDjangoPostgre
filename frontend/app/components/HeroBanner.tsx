'use client';

import { Carousel, Button } from 'antd';

// 輪播資料 (之後可替換成 API)
const slides = [
  {
    id: 1,
    title: '夏日新品上市',
    subtitle: '精選商品，限時優惠最高 5 折',
    bg: 'from-indigo-900 to-blue-700',
    cta: '立即選購',
    badge: 'NEW',
  },
  {
    id: 2,
    title: '品牌特賣會',
    subtitle: '頂級品牌，全場免運費',
    bg: 'from-rose-800 to-pink-600',
    cta: '查看活動',
    badge: 'SALE',
  },
  {
    id: 3,
    title: '精選 3C 好物',
    subtitle: '最新科技產品，一次看完',
    bg: 'from-slate-800 to-gray-600',
    cta: '探索商品',
    badge: 'HOT',
  },
];

export default function HeroBanner() {
  return (
    <Carousel autoplay autoplaySpeed={4000} dots={{ className: 'hero-dots' }}>
      {slides.map((slide) => (
        <div key={slide.id}>
          <div
            className={`bg-gradient-to-r ${slide.bg} h-[480px] flex items-center`}
          >
            <div className="max-w-7xl mx-auto px-8 w-full">
              {/* Badge */}
              <span className="inline-block bg-white/20 text-white text-xs font-bold tracking-widest px-3 py-1 rounded-full mb-4">
                {slide.badge}
              </span>

              {/* 標題 */}
              <h1 className="text-5xl font-extrabold text-white mb-4 leading-tight">
                {slide.title}
              </h1>

              {/* 副標題 */}
              <p className="text-white/80 text-lg mb-8">{slide.subtitle}</p>

              {/* CTA */}
              <Button
                type="primary"
                size="large"
                className="!bg-white !text-gray-900 !border-white hover:!bg-gray-100 font-semibold px-8"
              >
                {slide.cta}
              </Button>
            </div>
          </div>
        </div>
      ))}
    </Carousel>
  );
}
