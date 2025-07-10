# 🧠 NeurONLog - LLM-Powered Error Log Debugger for Intel Toolchains

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Intel oneAPI](https://img.shields.io/badge/Intel-oneAPI-orange.svg)](https://www.intel.com/content/www/us/en/developer/tools/oneapi/overview.html)

Intel toolchain'lerinden gelen hata loglarını analiz eden, sınıflandıran ve çözüm önerileri sunan AI destekli debug aracı.

## 🎯 Proje Amacı

NeurONLog, Intel oneAPI DPC++ compiler, VTune Profiler, Quartus Prime gibi Intel toolchain'lerinden gelen hata loglarını analiz ederek:

- **Hata türlerini otomatik sınıflandırır**
- **İnsan dilinde açıklamalar üretir**
- **Hedefli çözüm önerileri sunar**
- **Markdown formatında raporlar oluşturur**

Bu sayede mühendislerin debug süreçlerini hızlandırır ve Intel toolchain'lerini daha verimli kullanmalarını sağlar.

## 🏗️ Sistem Mimarisi

```
┌────────────┐
│ Raw Log In │ ◀──── stdin / file
└────┬───────┘
     ▼
┌────────────────────┐
│ Log Parser & Cleaner│
└────────────────────┘
     ▼
┌────────────────────┐
│ Error Classifier   │ ← Regex + keywords + optional LLM
└────────────────────┘
     ▼
┌──────────────────────────┐
│ Explanation Generator    │ ← LLM call (Chain-of-Thought)
└──────────────────────────┘
     ▼
┌──────────────────────────┐
│ Fix Recommender          │ ← LLM or rule-based suggestions
└──────────────────────────┘
     ▼
┌────────────────────┐
│ Markdown Formatter │
└────────────────────┘
```


## 🧩 Modüller

### 1. `parser.py` - Log Parser & Cleaner
- Ham log metnini temizler ve normalize eder
- Timestamp'leri, gereksiz whitespace'leri kaldırır
- Dosya yollarını güvenlik için kısaltır
- Hata ile ilgili satırları filtreler

### 2. `classifier.py` - Error Classifier
- Intel toolchain hatalarını sınıflandırır
- Regex pattern'leri ile hata türlerini tespit eder
- Güvenilirlik skorları hesaplar
- Bağlam bilgilerini çıkarır

### 3. `explainer.py` - Explanation Generator
- Hata türleri için önceden tanımlanmış açıklamalar
- Intel toolchain bağlamında detaylı açıklamalar
- Yaygın nedenler ve çözüm yolları

### 4. `fixer.py` - Fix Recommender
- Hata türüne özel çözüm önerileri
- Platform-specific komutlar (Linux, Windows, macOS)
- Adım adım çözüm rehberleri

### 5. `formatter.py` - Markdown Formatter
- Analiz sonuçlarını markdown formatında formatlar
- Intel dokümantasyon linkleri
- Görsel emoji'ler ve renkli çıktılar

## 🚀 Kurulum

### Gereksinimler
- Python 3.8 veya üzeri
- Intel oneAPI toolkit (opsiyonel, test için)

### Kurulum Adımları

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/yourusername/NeurONLog.git
cd NeurONLog
```

2. **Python bağımlılıklarını yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Çalıştırılabilir yapın:**
```bash
chmod +x main.py
```

## 💻 Kullanım

### Temel Kullanım

**Dosyadan log analizi:**
```bash
python main.py -f error.log
```

**Doğrudan metin girişi:**
```bash
python main.py -i "fatal error: 'CL/sycl.hpp' file not found"
```

**stdin'den okuma:**
```bash
cat error.log | python main.py
```

**Çıktıyı dosyaya yazma:**
```bash
python main.py -f error.log -o analysis_report.md
```

**Detaylı çıktı:**
```bash
python main.py -f error.log -v
```

### Örnek Çıktı

```markdown
# 🧠 Intel Toolchain Hata Analizi

**Analiz Tarihi:** 2024-01-15 14:30:25

## 🔍 Hata Özeti

**Hata Türü:** `MissingHeaderError`  
**Güvenilirlik:** 95.0%  
**Önem Derecesi:** 🟡 Medium

Header dosyası bulunamadı

### 📋 Bağlam Bilgileri

- **Compiler:** Intel DPC++
- **Etkilenen Dosyalar:** main.cpp
- **Hata Mesajları:** 'CL/sycl.hpp' file not found

## 📖 Açıklama

### Header Dosyası Bulunamadı

Bu hata, derleyicinin gerekli header dosyasını bulamadığında ortaya çıkar...

## 🛠️ Önerilen Çözümler

### 1. Intel oneAPI DPC++ Toolkit Kurulumu

Intel oneAPI DPC++ toolkit'in doğru kurulduğundan emin olun

**Komutlar:**
```bash
sudo apt-get install intel-oneapi-dpcpp-compiler
source /opt/intel/oneapi/setvars.sh
```

**Adımlar:**
- Intel oneAPI Base Toolkit'i indirin
- Kurulum sırasında DPC++ compiler seçeneğini işaretleyin
- Kurulum sonrası environment'ı source edin
```

## 🔧 Desteklenen Hata Türleri

| Hata Türü | Açıklama | Önem |
|-----------|----------|------|
| `MissingHeaderError` | Header dosyası bulunamadı | Medium |
| `Segfault` | Bellek erişim hatası | Critical |
| `LinkerError` | Bağlayıcı hatası | High |
| `SyntaxError` | Sözdizimi hatası | Medium |
| `SemanticError` | Anlamsal hata | Medium |
| `OpenCLError` | OpenCL hatası | High |
| `SYCLError` | SYCL hatası | High |
| `VTuneError` | VTune Profiler hatası | Medium |
| `QuartusError` | Quartus Prime hatası | High |
| `MemoryError` | Bellek hatası | Critical |

## Test

### Örnek Log Dosyaları

`examples/` klasöründe farklı Intel toolchain'lerinden örnek hata logları bulunmaktadır:

```bash
# DPC++ compiler hatası
python main.py -f examples/dpcpp_errors.log

# VTune Profiler hatası
python main.py -f examples/vtune_errors.log

# Quartus Prime hatası
python main.py -f examples/quartus_errors.log
```

### Test Senaryoları

```bash
# Basit header hatası testi
echo "fatal error: 'CL/sycl.hpp' file not found" | python main.py

# Linker hatası testi
echo "undefined reference to 'sycl::queue::submit'" | python main.py

# Segfault testi
echo "Segmentation fault (core dumped)" | python main.py
```

## Geliştirme

### Yeni Hata Türü Ekleme

1. `classifier.py` dosyasında `ERROR_PATTERNS` sözlüğüne yeni pattern'ler ekleyin
2. `explainer.py` dosyasında `ERROR_EXPLANATIONS` sözlüğüne açıklama ekleyin
3. `fixer.py` dosyasında `ERROR_FIXES` sözlüğüne çözüm önerileri ekleyin

### LLM Entegrasyonu

LLM entegrasyonu için `prompts/` klasöründeki şablonları kullanabilirsiniz:

```python
# Örnek LLM entegrasyonu
from prompts import get_explanation_prompt

prompt = get_explanation_prompt(error_type, log_content)


**NeurONLog** - Intel toolchain'leri için akıllı hata analizi 🧠 
