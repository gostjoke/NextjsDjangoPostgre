'use client';

import { AntdRegistry } from '@ant-design/nextjs-registry';
import { ConfigProvider } from 'antd';
import zhTW from 'antd/locale/zh_TW';

// 包裝 AntD，支援 Next.js App Router SSR
export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <AntdRegistry>
      <ConfigProvider
        locale={zhTW}
        theme={{
          token: {
            colorPrimary: '#1a1a2e',
            borderRadius: 6,
          },
        }}
      >
        {children}
      </ConfigProvider>
    </AntdRegistry>
  );
}
