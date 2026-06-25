'use client';

import {
  LaptopOutlined,
  SkinOutlined,
  HomeOutlined,
  HeartOutlined,
  CameraOutlined,
  GiftOutlined,
} from '@ant-design/icons';
import Link from 'next/link';

// 靜態分類資料（之後可換成 /api/store/categories/ API）
const categories = [
  { icon: <LaptopOutlined />, label: '3C 電子', color: 'bg-blue-50 text-blue-600', href: '#' },
  { icon: <SkinOutlined />, label: '服飾配件', color: 'bg-pink-50 text-pink-600', href: '#' },
  { icon: <HomeOutlined />, label: '家居生活', color: 'bg-amber-50 text-amber-600', href: '#' },
  { icon: <HeartOutlined />, label: '美妝保養', color: 'bg-rose-50 text-rose-600', href: '#' },
  { icon: <CameraOutlined />, label: '運動戶外', color: 'bg-green-50 text-green-600', href: '#' },
  { icon: <GiftOutlined />, label: '禮品特區', color: 'bg-purple-50 text-purple-600', href: '#' },
];

export default function CategorySection() {
  return (
    <section className="max-w-7xl mx-auto px-4 py-10">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">商品分類</h2>
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-4">
        {categories.map((cat) => (
          <Link
            key={cat.label}
            href={cat.href}
            className={`flex flex-col items-center gap-2 p-4 rounded-xl ${cat.color} hover:scale-105 transition-transform`}
          >
            <span className="text-3xl">{cat.icon}</span>
            <span className="text-sm font-medium">{cat.label}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
