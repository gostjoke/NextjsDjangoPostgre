'use client';

import { useEffect, useState } from 'react';
import { Spin, Empty, Button } from 'antd';
import ProductCard, { Product } from './ProductCard';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export default function FeaturedProducts() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 撈上架中的商品，最多 8 筆
    fetch(`${API_BASE}/api/store/products/?status=on_sale&ordering=-sales_count`)
      .then((r) => r.json())
      .then((data) => {
        // DRF 分頁回傳 { results: [...] } 或直接是陣列
        const list: Product[] = Array.isArray(data) ? data : (data.results ?? []);
        setProducts(list.slice(0, 8));
      })
      .catch(() => setProducts([]))   // API 未啟動時顯示空狀態
      .finally(() => setLoading(false));
  }, []);

  return (
    <section className="max-w-7xl mx-auto px-4 pb-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">熱門商品</h2>
        <Button type="link" href="#">查看全部 →</Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <Spin size="large" />
        </div>
      ) : products.length === 0 ? (
        <Empty description="目前沒有商品" className="py-20" />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}
    </section>
  );
}
