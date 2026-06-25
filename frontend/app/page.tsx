import Navbar from './components/Navbar';
import HeroBanner from './components/HeroBanner';
import CategorySection from './components/CategorySection';
import FeaturedProducts from './components/FeaturedProducts';
import Footer from './components/Footer';

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main className="flex-1 bg-gray-50">
        {/* 輪播 Banner */}
        <HeroBanner />
        {/* 分類導覽 */}
        <CategorySection />
        {/* 熱門商品 */}
        <FeaturedProducts />
      </main>
      <Footer />
    </>
  );
}
