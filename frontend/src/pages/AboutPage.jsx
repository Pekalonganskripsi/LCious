import React from 'react';
import { Brain, Users, TrendingUp, BookOpen, Code, Award, ArrowRight } from 'lucide-react';

function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Tentang LCious
          </h1>
          <p className="text-xl md:text-2xl text-blue-100 mb-6">
            Sistem Rekomendasi Kuliner Lokal dengan Hybrid Fuzzy-Collaborative Filtering
          </p>
          <p className="text-lg text-blue-200 max-w-3xl mx-auto">
            LCious adalah sistem cerdas yang merekomendasikan kuliner lokal berdasarkan preferensi selera, lokasi, dan rating komunitas menggunakan algoritma hybrid Fuzzy Logic dan Collaborative Filtering.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-16">
        {/* Problem Statement */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-red-100 rounded-full">
              <TrendingUp className="w-6 h-6 text-red-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800">Permasalahan</h2>
          </div>
          <div className="card-glass p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-3">
                  🍽️ Banyak Pilihan Kuliner Lokal
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Indonesia, khususnya kota Pekalongan dan sekitarnya, memiliki kekayaan kuliner lokal yang sangat beragam. Namun, seringkali wisatawan dan bahkan warga lokal kesulitan memilih menu yang sesuai dengan selera dan preferensi mereka.
                </p>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-3">
                  🤔 Kesulitan Memilih
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  Tanpa informasi yang memadai tentang rasa, harga, dan jarak, pelanggan sering membuat pilihan yang kurang tepat. UMKM juga kesulitan menjangkau pasar yang tepat untuk produk kuliner mereka.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Solution */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-green-100 rounded-full">
              <Brain className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800">Solusi: Hybrid Recommendation System</h2>
          </div>
          <div className="card-glass p-8">
            <p className="text-gray-600 leading-relaxed mb-6">
              LCious menggabungkan dua pendekatan recommendation system untuk memberikan rekomendasi yang lebih akurat dan personal:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <span className="text-2xl">🎯</span>
                  Fuzzy Logic System
                </h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500">•</span>
                    <span>Memodelkan preferensi user (harga, jarak, rasa)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500">•</span>
                    <span>Menangani ketidakpastian dan subjektivitas selera</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-500">•</span>
                    <span>Membership function untuk setiap kriteria</span>
                  </li>
                </ul>
              </div>
              <div className="p-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg">
                <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-center gap-2">
                  <span className="text-2xl">👥</span>
                  Collaborative Filtering
                </h3>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-start gap-2">
                    <span className="text-purple-500">•</span>
                    <span>Menggunakan rating komunitas untuk rekomendasi</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-500">•</span>
                    <span>Pearson Correlation untuk mencari user similar</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-purple-500">•</span>
                    <span>K-Nearest Neighbors (KNN) untuk prediksi rating</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Algorithm Detail */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-purple-100 rounded-full">
              <Code className="w-6 h-6 text-purple-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800">Algoritma Hybrid</h2>
          </div>
          <div className="card-glass p-8">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Rumus Utama</h3>
            <div className="bg-gray-900 text-green-400 p-6 rounded-lg font-mono text-sm md:text-base overflow-x-auto mb-6">
              <pre>{`Hscore(u,i) = (α × Sf(u,i)) + ((1-α) × Pcf(u,i)/Rmax)

Dimana:
• Hscore(u,i) = Hybrid score untuk user u dan menu i
• Sf(u,i) = Fuzzy score berdasarkan preferensi user
• Pcf(u,i) = Predicted rating dari Collaborative Filtering
• α (Alpha) = Bobot kombinasi (0-1)
• Rmax = Maximum rating (5.0)`}</pre>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">Adaptive Alpha (α)</h4>
                <p className="text-gray-600 mb-3">
                  Bobot alpha menyesuaikan secara otomatis berdasarkan jumlah rating user:
                </p>
                <ul className="space-y-2 text-gray-600">
                  <li className="flex items-center gap-2">
                    <span className="font-mono bg-red-100 text-red-700 px-2 py-1 rounded">α = 0.8</span>
                    <span>Cold Start (0-10 rating) → Lebih ke Fuzzy</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="font-mono bg-yellow-100 text-yellow-700 px-2 py-1 rounded">α = 0.5</span>
                    <span>Normal (10-50 rating) → Seimbang</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="font-mono bg-green-100 text-green-700 px-2 py-1 rounded">α = 0.2</span>
                    <span>Active (50+ rating) → Lebih ke CF</span>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">Komponen Fuzzy</h4>
                <p className="text-gray-600 mb-3">
                  Tiga kriteria utama dengan membership function triangular:
                </p>
                <ul className="space-y-2 text-gray-600">
                  <li>💰 <strong>Price</strong>: Cheap, Medium, Expensive</li>
                  <li>📍 <strong>Distance</strong>: Near, Medium, Far</li>
                  <li>⭐ <strong>Popularity</strong>: Low, Medium, High</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* System Architecture */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-blue-100 rounded-full">
              <Code className="w-6 h-6 text-blue-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800">Arsitektur Sistem</h2>
          </div>
          <div className="card-glass p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                  1
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">Data Collection</h3>
                <p className="text-sm text-gray-600">
                  User preferences, menu data, dan ratings dari komunitas
                </p>
              </div>
              <div className="text-center p-6 bg-purple-50 rounded-lg">
                <div className="w-16 h-16 bg-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                  2
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">Processing</h3>
                <p className="text-sm text-gray-600">
                  Fuzzy inference & Pearson correlation calculation
                </p>
              </div>
              <div className="text-center p-6 bg-pink-50 rounded-lg">
                <div className="w-16 h-16 bg-pink-500 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                  3
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">Recommendation</h3>
                <p className="text-sm text-gray-600">
                  Hybrid scoring dengan adaptive alpha weighting
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Technology Stack */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-orange-100 rounded-full">
              <Award className="w-6 h-6 text-orange-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800">Teknologi</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card-glass p-6">
              <h3 className="font-semibold text-gray-800 mb-4">Backend</h3>
              <ul className="space-y-2 text-gray-600">
                <li>🐍 <strong>Python</strong> dengan FastAPI</li>
                <li>💾 <strong>SQLite</strong> Database</li>
                <li>🧮 <strong>Pandas, NumPy</strong> untuk perhitungan</li>
                <li>🤖 <strong>SQLAlchemy</strong> ORM</li>
              </ul>
            </div>
            <div className="card-glass p-6">
              <h3 className="font-semibold text-gray-800 mb-4">Frontend</h3>
              <ul className="space-y-2 text-gray-600">
                <li>⚛️ <strong>React 18</strong> dengan Vite</li>
                <li>🎨 <strong>Tailwind CSS</strong> untuk styling</li>
                <li>🔄 <strong>Zustand</strong> untuk state management</li>
                <li>🛣️ <strong>React Router</strong> untuk navigasi</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Features */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-cyan-100 rounded-full">
              <Users className="w-6 h-6 text-cyan-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800">Fitur Utama</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card-glass p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-blue-100 rounded-full">
                  <Brain className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-800">Rekomendasi Personal</h3>
              </div>
              <p className="text-gray-600">
                Rekomendasi berdasarkan selera pribadi (pedas, manis, gurih) dan lokasi
              </p>
            </div>
            <div className="card-glass p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-purple-100 rounded-full">
                  <Star className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-800">Rating & Review</h3>
              </div>
              <p className="text-gray-600">
                Beri rating 1-5 bintang dan tulis review untuk menu yang sudah dicoba
              </p>
            </div>
            <div className="card-glass p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-3 bg-green-100 rounded-full">
                  <Store className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-800">Dashboard Merchant</h3>
              </div>
              <p className="text-gray-600">
                Kelola menu UMKM dan lihat statistik rating dan performa
              </p>
            </div>
          </div>
        </section>

        {/* References */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-3 bg-yellow-100 rounded-full">
              <BookOpen className="w-6 h-6 text-yellow-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800">Referensi & Jurnal</h2>
          </div>
          <div className="card-glass p-8">
            <p className="text-gray-600 mb-4">
              Sistem ini dikembangkan berdasarkan penelitian di bidang Recommender Systems:
            </p>
            <div className="space-y-3">
              <div className="p-4 bg-yellow-50 rounded-lg">
                <p className="font-medium text-gray-800">Fuzzy Logic in Recommender Systems</p>
                <p className="text-sm text-gray-600">
                  Penerapan fuzzy logic untuk menangani ketidakpastian preferensi user
                </p>
              </div>
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="font-medium text-gray-800">Collaborative Filtering</p>
                <p className="text-sm text-gray-600">
                  Item-based dan User-based filtering dengan Pearson Correlation
                </p>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <p className="font-medium text-gray-800">Hybrid Approaches</p>
                <p className="text-sm text-gray-600">
                  Menggabungkan multiple techniques untuk akurasi yang lebih baik
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="text-center">
          <div className="card-glass p-12 bg-gradient-to-r from-blue-500 to-purple-500 text-white">
            <h2 className="text-3xl font-bold mb-4">
              Siap Mencoba LCious?
            </h2>
            <p className="text-blue-100 mb-6">
              Bergabung dengan LCious sekarang dan temukan kuliner lokal favorit Anda!
            </p>
            <div className="flex items-center justify-center gap-4">
              <a
                href="/register"
                className="px-8 py-4 bg-white text-blue-600 rounded-lg font-semibold hover:shadow-lg transition-all inline-flex items-center gap-2"
              >
                Daftar Sekarang
                <ArrowRight className="w-5 h-5" />
              </a>
              <a
                href="/"
                className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-lg font-semibold hover:bg-white/10 transition-all"
              >
                Ke Beranda
              </a>
            </div>
          </div>
        </section>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2024 LCious - Local Culinary Recommendation System
          </p>
          <p className="text-gray-500 text-sm mt-2">
            Dibuat dengan ❤️ untuk UMKM Indonesia
          </p>
        </div>
      </footer>
    </div>
  );
}

export default AboutPage;
