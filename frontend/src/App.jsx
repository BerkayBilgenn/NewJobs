/**
 * Reverse Job Search Dashboard
 * CV yükle ve LinkedIn'de en uygun işleri bul
 */

import React, { useState, useCallback } from 'react';
import axios from 'axios';
import JobCard from './components/JobCard';

// API Base URL - Uses environment variable in production
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Türkiye'nin 81 ili
const TURKISH_CITIES = [
  "Tüm Türkiye", "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara",
  "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman", "Bayburt",
  "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı",
  "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne", "Elazığ", "Erzincan", "Erzurum",
  "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta",
  "İstanbul", "İzmir", "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri",
  "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya", "Kütahya", "Malatya",
  "Manisa", "Mardin", "Mersin", "Muğla", "Muş", "Nevşehir", "Niğde", "Ordu",
  "Osmaniye", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Şanlıurfa",
  "Şırnak", "Tekirdağ", "Tokat", "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak"
];

function App() {
  // State management
  const [cvFile, setCvFile] = useState(null);
  const [cvData, setCvData] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedCity, setSelectedCity] = useState("İstanbul");
  const [selectedJobTitle, setSelectedJobTitle] = useState(null);
  const [selectedPlatform, setSelectedPlatform] = useState("linkedin");

  /**
   * Handle file drop
   */
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        setCvFile(file);
        setError(null);
      } else {
        setError('Please upload a PDF file');
      }
    }
  }, []);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setCvFile(e.target.files[0]);
      setError(null);
    }
  };

  /**
   * Upload CV to backend
   */
  const uploadCV = async () => {
    if (!cvFile) return;
    
    setIsUploading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', cvFile);
      
      const response = await axios.post(`${API_URL}/upload_cv`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setCvData(response.data);
      // Auto-select first job title suggestion
      if (response.data.job_titles && response.data.job_titles.length > 0) {
        setSelectedJobTitle(response.data.job_titles[0]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload CV');
    } finally {
      setIsUploading(false);
    }
  };

  /**
   * Search for jobs on selected platform
   */
  const searchJobs = async (platform = "linkedin") => {
    if (!cvData) return;
    
    setSelectedPlatform(platform);
    setIsSearching(true);
    setError(null);
    
    try {
      const location = selectedCity === "Tüm Türkiye" ? "Turkey" : selectedCity;
      const jobTitle = selectedJobTitle || cvData.job_title;
      const response = await axios.post(`${API_URL}/search_jobs`, null, {
        params: {
          job_title: jobTitle,
          location: location,
          platform: platform
        }
      });
      
      setJobs(response.data.jobs);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to search jobs');
    } finally {
      setIsSearching(false);
    }
  };

  /**
   * Reset all state
   */
  const resetSearch = () => {
    setCvFile(null);
    setCvData(null);
    setJobs([]);
    setError(null);
    setSelectedCity("İstanbul");
    setSelectedJobTitle(null);
    setSelectedPlatform("linkedin");
  };

  return (
    <div className="min-h-screen bg-gradient-hero text-white">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
          <div className="flex items-center gap-2 sm:gap-3">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <svg className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h1 className="text-lg sm:text-xl font-bold">
              <span className="text-blue-400">Yeni</span>İşim
            </h1>
          </div>
          
          {(cvData || jobs.length > 0) && (
            <button
              onClick={resetSearch}
              className="px-3 sm:px-4 py-2 text-xs sm:text-sm text-gray-400 hover:text-white transition-colors"
            >
              Baştan Başla
            </button>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-12">
        {/* Hero Section - Show when no CV uploaded */}
        {!cvData && (
          <section className="text-center mb-8 sm:mb-12">
            <h2 className="text-2xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4 px-2">
              CV'ni yükle,
              <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent"> yapay zeka sana en uygun işleri bulsun</span>
            </h2>
            <p className="text-gray-400 text-sm sm:text-lg max-w-2xl mx-auto px-4">
              Akıllı botumuz LinkedIn ve Kariyer.net'i tarar, iş ilanlarını analiz eder ve senin için uyumluluk puanları hesaplar.
            </p>
          </section>
        )}

        {/* Upload Section */}
        {!cvData && (
          <section className="max-w-xl mx-auto mb-8 sm:mb-12 px-2">
            <div
              className={`
                relative border-2 border-dashed rounded-2xl p-6 sm:p-12 text-center transition-all duration-300
                ${dragActive ? 'dropzone-active border-blue-500' : 'border-gray-600 hover:border-gray-500'}
                ${cvFile ? 'bg-blue-500/10 border-blue-500' : ''}
              `}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              
              <div className="mb-4">
                <svg className={`w-16 h-16 mx-auto ${cvFile ? 'text-blue-400' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              
              {cvFile ? (
                <>
                  <p className="text-lg font-medium text-blue-400 mb-1">{cvFile.name}</p>
                  <p className="text-sm text-gray-400">Analiz için hazır</p>
                </>
              ) : (
                <>
                  <p className="text-lg font-medium text-gray-300 mb-1">
                    CV'ni buraya sürükle bırak
                  </p>
                  <p className="text-sm text-gray-500">veya dosya seçmek için tıkla (sadece PDF)</p>
                </>
              )}
            </div>
            
            {cvFile && (
              <button
                onClick={uploadCV}
                disabled={isUploading}
                className="mt-6 w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed text-white py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-3"
              >
                {isUploading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    CV Analiz Ediliyor...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                    </svg>
                    CV'yi Analiz Et
                  </>
                )}
              </button>
            )}
          </section>
        )}

        {/* CV Analysis Results */}
        {cvData && !isSearching && jobs.length === 0 && (
          <section className="max-w-2xl mx-auto mb-8 sm:mb-12 px-2">
            <div className="glass rounded-2xl p-4 sm:p-8">
              <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <span className="text-green-400">✓</span>
                CV Analizi Tamamlandı
              </h3>
              
              <div className="grid gap-4 mb-6">
                {/* Job Title Selection */}
                <div className="p-4 bg-white/5 rounded-xl">
                  <span className="text-gray-400 block mb-3">Pozisyon Seçin</span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {(cvData.job_titles || [cvData.job_title]).map((title, index) => (
                      <button
                        key={index}
                        onClick={() => setSelectedJobTitle(title)}
                        className={`p-3 rounded-xl text-left transition-all duration-300 border-2 ${
                          selectedJobTitle === title
                            ? 'bg-blue-500/20 border-blue-500 text-blue-300'
                            : 'bg-white/5 border-transparent hover:border-white/20 text-gray-300 hover:text-white'
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                            selectedJobTitle === title ? 'border-blue-400' : 'border-gray-500'
                          }`}>
                            {selectedJobTitle === title && (
                              <div className="w-2 h-2 rounded-full bg-blue-400" />
                            )}
                          </div>
                          <span className="font-medium">{title}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* Location Selection */}
                <div className="p-4 bg-white/5 rounded-xl">
                  <span className="text-gray-400 block mb-2">Arama Lokasyonu</span>
                  <select
                    value={selectedCity}
                    onChange={(e) => setSelectedCity(e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition-colors"
                  >
                    {TURKISH_CITIES.map((city) => (
                      <option key={city} value={city} className="bg-gray-800 text-white">
                        {city}
                      </option>
                    ))}
                  </select>
                </div>
                
                {/* Keywords */}
                <div className="p-4 bg-white/5 rounded-xl">
                  <span className="text-gray-400 block mb-2">Bulunan Anahtar Kelimeler</span>
                  <div className="flex flex-wrap gap-2">
                    {cvData.keywords.map((keyword, index) => (
                      <span key={index} className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-sm">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Search Buttons - Two Platforms */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button
                  onClick={() => searchJobs("linkedin")}
                  className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-3"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                  </svg>
                  LinkedIn'de Ara
                </button>
                <button
                  onClick={() => searchJobs("kariyer")}
                  className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-400 hover:to-red-400 text-white py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-300 flex items-center justify-center gap-3"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Kariyer.net'te Ara
                </button>
              </div>
            </div>
          </section>
        )}

        {/* Loading State - Bot is searching with Progress Bar */}
        {isSearching && (
          <section className="max-w-xl mx-auto text-center py-12">
            {/* Animated Icon */}
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <svg className="w-10 h-10 text-white animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            
            <h3 className="text-2xl font-bold mb-2">İş İlanları Aranıyor</h3>
            <p className="text-gray-400 mb-8">
              {selectedJobTitle} pozisyonu için uygun ilanlar taranıyor...
            </p>
            
            {/* Progress Bar Container */}
            <div className="glass rounded-2xl p-6 mb-6">
              {/* Progress Bar */}
              <div className="relative h-3 bg-white/10 rounded-full overflow-hidden mb-6">
                {/* Animated gradient bar */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-blue-500 rounded-full progress-bar-animate" />
                {/* Shimmer effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent shimmer-animate" />
              </div>
              
              {/* Steps Indicator - All animated */}
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center mb-2">
                    <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-green-400">Bağlantı</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-green-500/20 flex items-center justify-center mb-2">
                    <svg className="w-4 h-4 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <span className="text-green-400">Liste</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center mb-2 animate-pulse">
                    <div className="w-3 h-3 rounded-full bg-blue-400" />
                  </div>
                  <span className="text-blue-400">Detaylar</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center mb-2 animate-pulse">
                    <div className="w-3 h-3 rounded-full bg-purple-400" />
                  </div>
                  <span className="text-purple-400">Eşleştirme</span>
                </div>
              </div>
            </div>
            
            {/* Simple info text */}
            <p className="text-gray-500 text-sm">
              Bu işlem yaklaşık 15-20 saniye sürebilir
            </p>
          </section>
        )}

        {/* Job Results */}
        {jobs.length > 0 && (
          <section>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 sm:mb-8 gap-2">
              <h3 className="text-xl sm:text-2xl font-bold">
                {jobs.length} uygun iş bulundu
              </h3>
              <button
                onClick={searchJobs}
                disabled={isSearching}
                className="px-4 py-2 text-sm text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Yenile
              </button>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {jobs.map((job, index) => (
                <JobCard key={index} job={job} />
              ))}
            </div>
          </section>
        )}

        {/* Error Message */}
        {error && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-red-500/90 backdrop-blur-sm text-white px-6 py-3 rounded-xl shadow-lg flex items-center gap-3">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
            <button onClick={() => setError(null)} className="ml-2 hover:opacity-70">✕</button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-16 py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-gray-500 text-sm">
          <p>Kaan Berkay Bilgen tarafından yapıldı</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
