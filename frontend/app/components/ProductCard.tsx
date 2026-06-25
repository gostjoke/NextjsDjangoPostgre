'use client';

import { Card, Rate, Tag, Button } from 'antd';
import { ShoppingCartOutlined, HeartOutlined } from '@ant-design/icons';

export interface Product {
  id: number;
  name: string;
  base_price: string;
  rating_avg: string;
  rating_count: number;
  status: string;
  images: { image_url: string; is_main: boolean }[];
  brand?: { name: string };
}

interface Props {
  product: Product;
}

// 商品狀態對應 Tag 顏色
const statusTag: Record<string, { color: string; label: string }> = {
  on_sale:  { color: 'green',  label: '熱賣中' },
  sold_out: { color: 'red',    label: '已售完' },
  draft:    { color: 'default', label: '未上架' },
  off_sale: { color: 'orange', label: '已下架' },
};

export default function ProductCard({ product }: Props) {
  const mainImg = product.images.find((i) => i.is_main)?.image_url ?? '/placeholder.png';
  const tag = statusTag[product.status] ?? statusTag['on_sale'];
  const price = parseFloat(product.base_price).toLocaleString('zh-TW');

  return (
    <Card
      hoverable
      cover={
        <div className="relative overflow-hidden h-52 bg-gray-100">
          {/* 商品圖片 */}
          <img
            src={mainImg}
            alt={product.name}
            className="w-full h-full object-cover transition-transform duration-300 hover:scale-105"
            onError={(e) => { (e.target as HTMLImageElement).src = '/placeholder.png'; }}
          />
          {/* 收藏按鈕 */}
          <button className="absolute top-2 right-2 bg-white/80 rounded-full p-1.5 hover:bg-white transition-colors">
            <HeartOutlined className="text-gray-500" />
          </button>
          {/* 狀態 Tag */}
          <Tag color={tag.color} className="absolute top-2 left-2">
            {tag.label}
          </Tag>
        </div>
      }
      bodyStyle={{ padding: '12px 16px' }}
    >
      {/* 品牌 */}
      {product.brand && (
        <p className="text-xs text-gray-400 mb-1">{product.brand.name}</p>
      )}

      {/* 商品名稱 */}
      <p className="text-sm font-semibold text-gray-800 line-clamp-2 mb-2 leading-snug">
        {product.name}
      </p>

      {/* 評分 */}
      <div className="flex items-center gap-1 mb-3">
        <Rate disabled allowHalf defaultValue={parseFloat(product.rating_avg)} className="text-xs" />
        <span className="text-xs text-gray-400">({product.rating_count})</span>
      </div>

      {/* 價格 + 加入購物車 */}
      <div className="flex items-center justify-between">
        <span className="text-lg font-bold text-red-500">NT$ {price}</span>
        <Button
          type="primary"
          size="small"
          icon={<ShoppingCartOutlined />}
          disabled={product.status === 'sold_out'}
        >
          加入
        </Button>
      </div>
    </Card>
  );
}
