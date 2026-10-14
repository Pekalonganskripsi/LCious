import React from 'react'
import { ArrowRight, Brain, Users, MapPin, TrendingUp } from 'lucide-react'

function HomePage() {
  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 px-4">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 via-orange-500/10 to-yellow-500/10"></div>
        <div className="absolute top-20 left-10 w-72 h-72 bg-red-400/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-72 h-72 bg-orange-400/20 rounded-full blur-3xl"></div>

        <div className="container mx-auto relative">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/20 backdrop-blur-sm border border-white/30 mb-6">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className="text-sm font-medium text-gray-700">Research-Based Application</span>
            </div>

            {/* Heading */}
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="text-gradient">Temukan Kuliner Lokal</span>
              <br />
              <span className="text-gray-800">Sesuai Selera Anda</span>
            </h1>

            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Sistem rekomendasi kuliner dengan Hybrid Fuzzy-Collaborative Filtering.
              Personalisasi berdasarkan preferensi rasa, lokasi, dan tren komunitas.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="btn-primary text-lg px-8 py-4 flex items-center justify-center gap-2">
                Mulai Sekarang
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="btn-secondary text-lg px-8 py-4">
                Pelajari Lebih Lanjut
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 mt-16 max-w-2xl mx-auto">
              <div className="text-center">
                <div className="text-3xl font-bold text-gradient">3+</div>
                <div className="text-sm text-gray-600">Algoritma Hybrid</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gradient">UMKM</div>
                <div className="text-sm text-gray-600">Kuliner Lokal</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-gradient">AI</div>
                <div className="text-sm text-gray-600">Personalisasi</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-800">
              Teknologi di Balik LCious
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Menggabungkan kecerdasan buatan dengan pemahaman preferensi manusia
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Feature 1: Fuzzy Logic */}
            <div className="card-glass p-8">
              <div className="w-14 h-14 bg-blue-500/20 rounded-xl flex items-center justify-center mb-6">
                <Brain className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Fuzzy Logic</h3>
              <p className="text-gray-600 mb-4">
                Memahami preferensi subjektif seperti "pedas", "manis", "gurih" dengan fungsi keanggotaan
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">Triangular MF</span>
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">Price</span>
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">Taste</span>
              </div>
            </div>

            {/* Feature 2: Collaborative Filtering */}
            <div className="card-glass p-8">
              <div className="w-14 h-14 bg-purple-500/20 rounded-xl flex items-center justify-center mb-6">
                <Users className="w-7 h-7 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Collaborative Filtering</h3>
              <p className="text-gray-600 mb-4">
                Menganalisis pola komunitas dengan Pearson Correlation dan K-Nearest Neighbors
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">Pearson</span>
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">KNN</span>
                <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">User-Based</span>
              </div>
            </div>

            {/* Feature 3: Hybrid + Geolocation */}
            <div className="card-glass p-8">
              <div className="w-14 h-14 bg-red-500/20 rounded-xl flex items-center justify-center mb-6">
                <TrendingUp className="w-7 h-7 text-red-600" />
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-800">Hybrid Integration</h3>
              <p className="text-gray-600 mb-4">
                Menggabungkan preferensi pribadi dengan tren komunitas menggunakan weighted combination
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">α-Tuning</span>
                <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">MAE/RMSE</span>
                <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">Cold Start</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-20 px-4 bg-white/30 backdrop-blur-sm">
        <div className="container mx-auto max-w-4xl">
          <div className="card-glass p-12 text-center">
            <h2 className="text-3xl font-bold mb-6 text-gray-800">
              Untuk Penelitian Akademik
            </h2>
            <p className="text-lg text-gray-600 mb-8">
              LCious dikembangkan untuk penelitian dengan judul:<br/>
              <span className="italic font-medium text-gray-800">
                "Personalized Local Culinary Recommendation System using Hybrid Fuzzy-Collaborative Filtering in LCious Application"
              </span>
            </p>
            <div className="grid sm:grid-cols-2 gap-6 text-left">
              <div className="flex items-start gap-3">
                <MapPin className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">Lokasi-Aware</h4>
                  <p className="text-sm text-gray-600">Rekomendasi berdasarkan jarak dengan Geolocation API</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Brain className="w-6 h-6 text-blue-500 flex-shrink-0 mt-1" />
                <div>
                  <h4 className="font-semibold text-gray-800 mb-1">AI-Powered</h4>
                  <p className="text-sm text-gray-600">Algoritma hybrid dengan transparansi penuh untuk research</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-white/20">
        <div className="container mx-auto text-center text-gray-600">
          <p>&copy; 2025 LCious - Local Culinary & Delicious. Research Application.</p>
        </div>
      </footer>
    </div>
  )
}

export default HomePage
