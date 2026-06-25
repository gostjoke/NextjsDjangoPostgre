'use client';

import { Divider } from 'antd';
import {
  GithubOutlined,
  InstagramOutlined,
  FacebookOutlined,
} from '@ant-design/icons';
import Link from 'next/link';

const links = [
  { title: '關於我們', items: ['品牌故事', '聯絡我們', '加入我們'] },
  { title: '購物指南', items: ['如何下單', '付款方式', '配送說明'] },
  { title: '會員服務', items: ['會員登入', '訂單查詢', '退換貨政策'] },
];

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-400 mt-auto">
      <div className="max-w-7xl mx-auto px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div>
            <h2 className="text-white text-lg font-bold mb-3">ShopNow</h2>
            <p className="text-sm leading-relaxed">
              提供最優質的商品與購物體驗，讓每一次購物都令人滿意。
            </p>
            <div className="flex gap-4 mt-4 text-xl">
              <GithubOutlined className="hover:text-white cursor-pointer transition-colors" />
              <InstagramOutlined className="hover:text-white cursor-pointer transition-colors" />
              <FacebookOutlined className="hover:text-white cursor-pointer transition-colors" />
            </div>
          </div>

          {/* Link groups */}
          {links.map((group) => (
            <div key={group.title}>
              <h3 className="text-white text-sm font-semibold mb-3">{group.title}</h3>
              <ul className="space-y-2">
                {group.items.map((item) => (
                  <li key={item}>
                    <Link
                      href="#"
                      className="text-sm hover:text-white transition-colors"
                    >
                      {item}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <Divider className="!border-gray-700 !my-8" />
        <p className="text-center text-xs">© 2026 ShopNow. All rights reserved.</p>
      </div>
    </footer>
  );
}
