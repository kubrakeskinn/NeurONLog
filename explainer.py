"""
Explanation Generator Module

Intel toolchain hatalarını insan dilinde açıklar.
"""

import re
from typing import Dict, Any, Optional


# Hata türleri için önceden tanımlanmış açıklamalar
ERROR_EXPLANATIONS = {
    'MissingHeaderError': {
        'tr': {
            'title': 'Header Dosyası Bulunamadı',
            'explanation': 'Bu hata, derleyicinin gerekli header dosyasını bulamadığında ortaya çıkar. Genellikle Intel oneAPI DPC++ toolkit\'in doğru kurulmamış olması veya include path\'lerinin eksik olması nedeniyle oluşur.',
            'common_causes': [
                'Intel oneAPI DPC++ toolkit kurulu değil',
                'Include path\'leri doğru ayarlanmamış',
                'SYCL header dosyaları eksik',
                'Environment variables doğru set edilmemiş'
            ],
            'intel_context': 'Intel oneAPI DPC++ ile çalışırken SYCL header dosyalarına erişim gereklidir. Bu dosyalar genellikle Intel oneAPI kurulum dizininde bulunur.'
        }
    },
    
    'Segfault': {
        'tr': {
            'title': 'Bellek Erişim Hatası (Segmentation Fault)',
            'explanation': 'Program geçersiz bir bellek adresine erişmeye çalıştığında bu hata oluşur. Intel toolchain\'lerde genellikle GPU bellek yönetimi veya SYCL kernel\'lerindeki pointer hatalarından kaynaklanır.',
            'common_causes': [
                'Null pointer dereference',
                'Array bounds overflow',
                'GPU bellek erişim hatası',
                'SYCL kernel\'de geçersiz bellek erişimi',
                'Stack overflow'
            ],
            'intel_context': 'Intel GPU\'larda çalışan SYCL kernel\'lerde bellek erişim hataları sık görülür. Özellikle unified shared memory (USM) kullanırken dikkatli olunmalıdır.'
        }
    },
    
    'LinkerError': {
        'tr': {
            'title': 'Bağlayıcı Hatası',
            'explanation': 'Derleme aşamasında, linker gerekli sembolleri veya kütüphaneleri bulamadığında bu hata oluşur. Intel toolchain\'lerde genellikle SYCL runtime kütüphanelerinin eksik olmasından kaynaklanır.',
            'common_causes': [
                'SYCL runtime kütüphaneleri eksik',
                'Intel oneAPI runtime kurulu değil',
                'Library path\'leri doğru ayarlanmamış',
                'Eksik linker flag\'leri',
                'Platform-specific kütüphaneler eksik'
            ],
            'intel_context': 'Intel oneAPI DPC++ ile derleme yaparken SYCL runtime kütüphanelerinin doğru link edilmesi gerekir. Bu kütüphaneler Intel oneAPI kurulumu ile birlikte gelir.'
        }
    },
    
    'SyntaxError': {
        'tr': {
            'title': 'Sözdizimi Hatası',
            'explanation': 'Kod yazımında sözdizimi kurallarına uyulmadığında bu hata oluşur. Intel DPC++ compiler\'da SYCL syntax\'ına özgü hatalar da görülebilir.',
            'common_causes': [
                'Eksik noktalı virgül',
                'Yanlış parantez eşleşmesi',
                'SYCL syntax hatası',
                'Template syntax hatası',
                'Namespace kullanım hatası'
            ],
            'intel_context': 'Intel DPC++ compiler, standart C++ syntax\'ına ek olarak SYCL-specific syntax kurallarını da kontrol eder. SYCL namespace ve template kullanımına dikkat edilmelidir.'
        }
    },
    
    'SemanticError': {
        'tr': {
            'title': 'Anlamsal Hata',
            'explanation': 'Kod sözdizimi açısından doğru ancak anlamsal olarak hatalı olduğunda bu hata oluşur. Intel toolchain\'lerde genellikle tip uyumsuzlukları ve SYCL-specific kuralların ihlal edilmesinden kaynaklanır.',
            'common_causes': [
                'Tip uyumsuzluğu',
                'SYCL kernel parametre uyumsuzluğu',
                'Template instantiation hatası',
                'Function overload çözümleme hatası',
                'SYCL memory model ihlali'
            ],
            'intel_context': 'Intel DPC++ compiler, SYCL memory model kurallarını ve kernel parametre tiplerini sıkı bir şekilde kontrol eder. GPU\'ya gönderilen verilerin doğru tiplerde olması gerekir.'
        }
    },
    
    'OpenCLError': {
        'tr': {
            'title': 'OpenCL Hatası',
            'explanation': 'OpenCL platform veya device ile ilgili bir hata oluştuğunda bu hata görülür. Intel oneAPI\'de OpenCL backend kullanılırken ortaya çıkabilir.',
            'common_causes': [
                'OpenCL platform bulunamadı',
                'Intel GPU driver eksik',
                'OpenCL runtime kurulu değil',
                'Device erişim hatası',
                'Kernel compilation hatası'
            ],
            'intel_context': 'Intel oneAPI DPC++ OpenCL backend kullanır. Intel GPU driver\'larının ve OpenCL runtime\'ının doğru kurulmuş olması gerekir.'
        }
    },
    
    'SYCLError': {
        'tr': {
            'title': 'SYCL Hatası',
            'explanation': 'SYCL runtime veya kernel execution sırasında oluşan hatalar. Intel oneAPI DPC++ ile SYCL programları çalıştırırken görülebilir.',
            'common_causes': [
                'SYCL runtime hatası',
                'Kernel execution hatası',
                'Device selection hatası',
                'Memory allocation hatası',
                'Queue operation hatası'
            ],
            'intel_context': 'Intel DPC++ SYCL implementation\'ı kullanır. SYCL runtime\'ının doğru kurulmuş olması ve device\'ların erişilebilir olması gerekir.'
        }
    },
    
    'VTuneError': {
        'tr': {
            'title': 'VTune Profiler Hatası',
            'explanation': 'Intel VTune Profiler ile profiling yaparken oluşan hatalar. Genellikle sampling veya analiz sırasında ortaya çıkar.',
            'common_causes': [
                'Sampling permission hatası',
                'Target application erişim hatası',
                'Profiling driver eksik',
                'Hardware counter erişim hatası',
                'Analysis configuration hatası'
            ],
            'intel_context': 'VTune Profiler, Intel CPU ve GPU\'larda profiling yapmak için özel driver\'lar gerektirir. Bu driver\'ların doğru kurulmuş olması gerekir.'
        }
    },
    
    'QuartusError': {
        'tr': {
            'title': 'Quartus Prime Hatası',
            'explanation': 'Intel Quartus Prime ile FPGA synthesis veya fitting sırasında oluşan hatalar. Genellikle design constraint\'leri veya resource kullanımı ile ilgilidir.',
            'common_causes': [
                'Synthesis constraint hatası',
                'Resource limit aşımı',
                'Timing constraint ihlali',
                'Pin assignment hatası',
                'IP core configuration hatası'
            ],
            'intel_context': 'Quartus Prime, Intel FPGA\'lar için synthesis ve fitting yapar. Design constraint\'lerinin doğru tanımlanmış olması ve resource limitlerinin aşılmaması gerekir.'
        }
    }
}


def generate_explanation(error_type: str, log: str, language: str = 'tr') -> str:
    """
    Hata türü için açıklama oluşturur.
    
    Args:
        error_type: Hata türü
        log: Log metni (bağlam için)
        language: Dil ('tr' veya 'en')
        
    Returns:
        Hata açıklaması
    """
    # Önceden tanımlanmış açıklamaları kontrol et
    if error_type in ERROR_EXPLANATIONS:
        explanation_data = ERROR_EXPLANATIONS[error_type].get(language, ERROR_EXPLANATIONS[error_type]['tr'])
        
        # Bağlam bilgilerini çıkar
        context_info = extract_context_from_log(log)
        
        # Açıklamayı oluştur
        explanation = f"""
## {explanation_data['title']}

{explanation_data['explanation']}

### Yaygın Nedenler:
"""
        
        for cause in explanation_data['common_causes']:
            explanation += f"- {cause}\n"
        
        explanation += f"\n### Intel Toolchain Bağlamı:\n{explanation_data['intel_context']}"
        
        # Log'dan çıkarılan bağlam bilgilerini ekle
        if context_info:
            explanation += "\n\n### Bu Hata İçin Özel Bilgiler:\n"
            if context_info.get('files'):
                explanation += f"- **Etkilenen Dosyalar:** {', '.join(context_info['files'])}\n"
            if context_info.get('line_numbers'):
                explanation += f"- **Satır Numaraları:** {', '.join(context_info['line_numbers'])}\n"
            if context_info.get('compiler_info'):
                explanation += f"- **Compiler:** {context_info['compiler_info']}\n"
        
        return explanation.strip()
    
    # Bilinmeyen hata türü için genel açıklama
    return generate_generic_explanation(error_type, log, language)


def extract_context_from_log(log: str) -> Dict[str, Any]:
    """
    Log'dan bağlam bilgilerini çıkarır.
    
    Args:
        log: Log metni
        
    Returns:
        Bağlam bilgileri
    """
    context = {
        'files': [],
        'line_numbers': [],
        'compiler_info': None,
        'error_messages': []
    }
    
    # Dosya adlarını çıkar
    file_patterns = [
        r'([a-zA-Z0-9_\-\./\\]+\.(cpp|hpp|c|h|sycl|cl))',
        r'([a-zA-Z0-9_\-\./\\]+\.(o|obj|so|dll|a|lib))'
    ]
    
    for pattern in file_patterns:
        matches = re.findall(pattern, log, re.IGNORECASE)
        for match in matches:
            if match[0] not in context['files']:
                context['files'].append(match[0])
    
    # Satır numaralarını çıkar
    line_matches = re.findall(r':(\d+):', log)
    context['line_numbers'] = list(set(line_matches))
    
    # Compiler bilgisini çıkar
    if 'dpcpp' in log.lower() or 'sycl' in log.lower():
        context['compiler_info'] = 'Intel DPC++'
    elif 'icx' in log.lower() or 'icpx' in log.lower():
        context['compiler_info'] = 'Intel ICPX'
    elif 'vtune' in log.lower():
        context['compiler_info'] = 'Intel VTune'
    elif 'quartus' in log.lower():
        context['compiler_info'] = 'Intel Quartus'
    
    # Hata mesajlarını çıkar
    error_matches = re.findall(r'error[^:]*:\s*([^\n]+)', log, re.IGNORECASE)
    context['error_messages'] = [msg.strip() for msg in error_matches]
    
    return context


def generate_generic_explanation(error_type: str, log: str, language: str = 'tr') -> str:
    """
    Bilinmeyen hata türü için genel açıklama oluşturur.
    
    Args:
        error_type: Hata türü
        log: Log metni
        language: Dil
        
    Returns:
        Genel açıklama
    """
    context_info = extract_context_from_log(log)
    
    explanation = f"""
## {error_type}

Bu hata türü için özel bir açıklama bulunmuyor. Log analizi sonucunda tespit edilen bilgiler:

### Log İçeriği:
```
{log[:500]}{'...' if len(log) > 500 else ''}
```

### Tespit Edilen Bağlam:
"""
    
    if context_info.get('files'):
        explanation += f"- **Dosyalar:** {', '.join(context_info['files'])}\n"
    if context_info.get('line_numbers'):
        explanation += f"- **Satır Numaraları:** {', '.join(context_info['line_numbers'])}\n"
    if context_info.get('compiler_info'):
        explanation += f"- **Compiler:** {context_info['compiler_info']}\n"
    if context_info.get('error_messages'):
        explanation += f"- **Hata Mesajları:** {', '.join(context_info['error_messages'])}\n"
    
    explanation += """
### Öneriler:
- Log'un tamamını inceleyin
- Intel oneAPI dokümantasyonunu kontrol edin
- Benzer hatalar için Intel forum'larını araştırın
- Compiler ve runtime versiyonlarını kontrol edin
"""
    
    return explanation.strip()


def get_error_summary(error_type: str, log: str) -> str:
    """
    Hata için kısa özet oluşturur.
    
    Args:
        error_type: Hata türü
        log: Log metni
        
    Returns:
        Kısa özet
    """
    if error_type in ERROR_EXPLANATIONS:
        title = ERROR_EXPLANATIONS[error_type]['tr']['title']
        return f"{title} — {ERROR_EXPLANATIONS[error_type]['tr']['explanation'][:100]}..."
    
    return f"{error_type} — Bilinmeyen hata türü" 