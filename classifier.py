"""
Error Classifier Module

Intel toolchain hatalarını sınıflandırır ve türlerini belirler.
"""

import re
from typing import Dict, List, Tuple, Any


# Intel toolchain hata türleri ve pattern'leri
ERROR_PATTERNS = {
    'MissingHeaderError': [
        r"file not found",
        r"cannot find header",
        r"no such file or directory",
        r"missing header",
        r"include.*not found",
        r"CL/sycl\.hpp.*not found",
        r"sycl/sycl\.hpp.*not found"
    ],
    
    'Segfault': [
        r"segmentation fault",
        r"segfault",
        r"core dumped",
        r"access violation",
        r"memory access violation",
        r"invalid memory reference"
    ],
    
    'LinkerError': [
        r"undefined reference",
        r"unresolved symbol",
        r"linker error",
        r"cannot find -l",
        r"library not found",
        r"symbol not found"
    ],
    
    'SyntaxError': [
        r"syntax error",
        r"expected.*before",
        r"missing.*before",
        r"unexpected.*token",
        r"invalid syntax",
        r"parse error"
    ],
    
    'SemanticError': [
        r"semantic error",
        r"type mismatch",
        r"cannot convert",
        r"incompatible types",
        r"no matching function",
        r"ambiguous call"
    ],
    
    'CompilationError': [
        r"compilation terminated",
        r"compilation failed",
        r"build failed",
        r"make.*error",
        r"compiler error"
    ],
    
    'RuntimeError': [
        r"runtime error",
        r"aborted",
        r"terminated",
        r"exception thrown",
        r"unhandled exception"
    ],
    
    'OpenCLError': [
        r"opencl error",
        r"cl.*error",
        r"platform not found",
        r"device not found",
        r"kernel compilation failed"
    ],
    
    'SYCLError': [
        r"sycl error",
        r"sycl exception",
        r"sycl runtime error",
        r"sycl kernel error",
        r"sycl device error"
    ],
    
    'VTuneError': [
        r"vtune.*error",
        r"profiler error",
        r"sampling error",
        r"analysis error",
        r"vtune.*failed"
    ],
    
    'QuartusError': [
        r"quartus.*error",
        r"synthesis error",
        r"fitter error",
        r"timing error",
        r"quartus.*failed"
    ],
    
    'MemoryError': [
        r"out of memory",
        r"memory allocation failed",
        r"insufficient memory",
        r"memory limit exceeded",
        r"stack overflow"
    ],
    
    'PermissionError': [
        r"permission denied",
        r"access denied",
        r"cannot create",
        r"cannot write",
        r"read-only"
    ],
    
    'NetworkError': [
        r"connection failed",
        r"network error",
        r"timeout",
        r"connection refused",
        r"host unreachable"
    ],
    
    'ConfigurationError': [
        r"configuration error",
        r"invalid configuration",
        r"missing configuration",
        r"config.*error",
        r"setup.*error"
    ]
}


def classify_error(log: str) -> Dict[str, Any]:
    """
    Log'daki hatayı sınıflandırır.
    
    Args:
        log: Temizlenmiş log metni
        
    Returns:
        Hata bilgileri sözlüğü
    """
    if not log or not log.strip():
        return {
            'type': 'UnknownError',
            'confidence': 0.0,
            'patterns': [],
            'description': 'Boş veya geçersiz log'
        }
    
    log_lower = log.lower()
    matches = []
    
    # Her hata türü için pattern'leri kontrol et
    for error_type, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, log_lower, re.IGNORECASE):
                matches.append({
                    'type': error_type,
                    'pattern': pattern,
                    'confidence': calculate_confidence(pattern, log_lower)
                })
    
    # Eşleşme bulunamadıysa
    if not matches:
        return {
            'type': 'UnknownError',
            'confidence': 0.1,
            'patterns': [],
            'description': 'Bilinmeyen hata türü'
        }
    
    # En yüksek güvenilirlik skoruna sahip eşleşmeyi seç
    best_match = max(matches, key=lambda x: x['confidence'])
    
    # Ek bağlam bilgilerini çıkar
    context = extract_error_context(log)
    
    return {
        'type': best_match['type'],
        'confidence': best_match['confidence'],
        'patterns': [m['pattern'] for m in matches],
        'description': get_error_description(best_match['type']),
        'context': context,
        'severity': get_error_severity(best_match['type'])
    }


def calculate_confidence(pattern: str, log: str) -> float:
    """
    Pattern eşleşmesinin güvenilirlik skorunu hesaplar.
    
    Args:
        pattern: Regex pattern
        log: Log metni (lowercase)
        
    Returns:
        Güvenilirlik skoru (0.0 - 1.0)
    """
    # Temel skor
    base_score = 0.5
    
    # Pattern'in log'da kaç kez geçtiği
    matches = re.findall(pattern, log, re.IGNORECASE)
    frequency_score = min(len(matches) * 0.1, 0.3)
    
    # Pattern'in spesifikliği (daha uzun pattern'ler daha güvenilir)
    specificity_score = min(len(pattern) * 0.01, 0.2)
    
    # Hata anahtar kelimelerinin varlığı
    error_keywords = ['error', 'fatal', 'failed', 'cannot', 'missing', 'undefined']
    keyword_score = sum(0.05 for keyword in error_keywords if keyword in log)
    
    total_score = base_score + frequency_score + specificity_score + keyword_score
    return min(total_score, 1.0)


def extract_error_context(log: str) -> Dict[str, Any]:
    """
    Log'dan hata bağlamını çıkarır.
    
    Args:
        log: Log metni
        
    Returns:
        Bağlam bilgileri
    """
    context = {
        'files': [],
        'line_numbers': [],
        'error_messages': [],
        'compiler_info': None
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
    
    # Hata mesajlarını çıkar
    error_matches = re.findall(r'error[^:]*:\s*([^\n]+)', log, re.IGNORECASE)
    context['error_messages'] = [msg.strip() for msg in error_matches]
    
    # Compiler bilgisini çıkar
    if 'dpcpp' in log.lower() or 'sycl' in log.lower():
        context['compiler_info'] = 'Intel DPC++'
    elif 'icx' in log.lower() or 'icpx' in log.lower():
        context['compiler_info'] = 'Intel ICPX'
    elif 'vtune' in log.lower():
        context['compiler_info'] = 'Intel VTune'
    elif 'quartus' in log.lower():
        context['compiler_info'] = 'Intel Quartus'
    
    return context


def get_error_description(error_type: str) -> str:
    """
    Hata türü için açıklama döndürür.
    
    Args:
        error_type: Hata türü
        
    Returns:
        Hata açıklaması
    """
    descriptions = {
        'MissingHeaderError': 'Header dosyası bulunamadı',
        'Segfault': 'Bellek erişim hatası (segmentation fault)',
        'LinkerError': 'Bağlayıcı hatası - sembol bulunamadı',
        'SyntaxError': 'Sözdizimi hatası',
        'SemanticError': 'Anlamsal hata - tip uyumsuzluğu',
        'CompilationError': 'Derleme hatası',
        'RuntimeError': 'Çalışma zamanı hatası',
        'OpenCLError': 'OpenCL hatası',
        'SYCLError': 'SYCL hatası',
        'VTuneError': 'VTune Profiler hatası',
        'QuartusError': 'Quartus Prime hatası',
        'MemoryError': 'Bellek hatası',
        'PermissionError': 'İzin hatası',
        'NetworkError': 'Ağ hatası',
        'ConfigurationError': 'Yapılandırma hatası',
        'UnknownError': 'Bilinmeyen hata türü'
    }
    
    return descriptions.get(error_type, 'Bilinmeyen hata türü')


def get_error_severity(error_type: str) -> str:
    """
    Hata türü için önem derecesini döndürür.
    
    Args:
        error_type: Hata türü
        
    Returns:
        Önem derecesi (critical, high, medium, low)
    """
    severity_map = {
        'MissingHeaderError': 'medium',
        'Segfault': 'critical',
        'LinkerError': 'high',
        'SyntaxError': 'medium',
        'SemanticError': 'medium',
        'CompilationError': 'high',
        'RuntimeError': 'critical',
        'OpenCLError': 'high',
        'SYCLError': 'high',
        'VTuneError': 'medium',
        'QuartusError': 'high',
        'MemoryError': 'critical',
        'PermissionError': 'medium',
        'NetworkError': 'medium',
        'ConfigurationError': 'medium',
        'UnknownError': 'low'
    }
    
    return severity_map.get(error_type, 'low')


def get_related_errors(log: str) -> List[str]:
    """
    Log'da bulunan ilgili hata türlerini döndürür.
    
    Args:
        log: Log metni
        
    Returns:
        İlgili hata türleri listesi
    """
    related = []
    log_lower = log.lower()
    
    for error_type, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, log_lower, re.IGNORECASE):
                if error_type not in related:
                    related.append(error_type)
    
    return related 