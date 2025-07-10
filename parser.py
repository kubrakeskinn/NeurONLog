"""
Log Parser & Cleaner Module

Intel toolchain loglarını temizler ve normalize eder.
"""

import re
from typing import List, Dict, Any


def parse_log(log: str) -> str:
    """
    Ham log metnini temizler ve normalize eder.
    
    Args:
        log: Ham log metni
        
    Returns:
        Temizlenmiş log metni
    """
    if not log or not log.strip():
        return ""
    
    # 1. Temel temizlik
    cleaned = log.strip()
    
    # 2. Gereksiz whitespace'leri normalize et
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)  # Çoklu boş satırları azalt
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)  # Çoklu boşlukları tek boşluğa çevir
    
    # 3. Timestamp'leri kaldır (Intel log formatları)
    timestamp_patterns = [
        r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]\s*',
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s*',
        r'\d{2}:\d{2}:\d{2}\.\d+\s*',
        r'\[.*?\]\s*'  # Genel bracket pattern
    ]
    
    for pattern in timestamp_patterns:
        cleaned = re.sub(pattern, '', cleaned)
    
    # 4. Dosya yollarını normalize et (güvenlik için)
    # Tam dosya yollarını kısalt
    cleaned = re.sub(r'/[^\s]*/([^/\s]+)', r'.../\1', cleaned)
    cleaned = re.sub(r'C:\\[^\s]*\\([^\\\s]+)', r'...\\\1', cleaned)
    
    # 5. Stack trace'lerdeki gereksiz detayları kaldır
    # Intel toolchain'lerin tipik stack trace pattern'leri
    stack_patterns = [
        r'at\s+[^\n]*\s+\([^)]*\)\s*',
        r'#\d+\s+[^\n]*\s+in\s+[^\n]*\s*',
        r'Thread\s+\d+\s+\([^)]*\)\s*',
    ]
    
    for pattern in stack_patterns:
        cleaned = re.sub(pattern, '', cleaned)
    
    # 6. Compiler çıktısındaki gereksiz bilgileri kaldır
    compiler_noise = [
        r'Intel\(R\)\s+oneAPI\s+DPC\+\+\s+Compiler\s+[^\n]*\n',
        r'Copyright\s+\(C\)\s+[^\n]*\n',
        r'Version\s+[^\n]*\n',
        r'Target:\s+[^\n]*\n',
        r'Thread\s+model:\s+[^\n]*\n',
        r'InstalledDir:\s+[^\n]*\n',
    ]
    
    for pattern in compiler_noise:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # 7. Sadece hata ile ilgili satırları tut
    error_keywords = [
        'error', 'fatal', 'warning', 'failed', 'failed to',
        'undefined', 'missing', 'not found', 'cannot',
        'segmentation fault', 'core dumped', 'aborted',
        'compilation terminated', 'linker error',
        'syntax error', 'semantic error'
    ]
    
    lines = cleaned.split('\n')
    relevant_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Hata anahtar kelimelerini içeren satırları tut
        if any(keyword.lower() in line.lower() for keyword in error_keywords):
            relevant_lines.append(line)
        # Hata satırından önceki 1-2 satırı da tut (context için)
        elif relevant_lines and len(relevant_lines) <= 3:
            relevant_lines.append(line)
    
    # Eğer hiç hata satırı bulunamadıysa, orijinal metni döndür
    if not relevant_lines:
        return cleaned
    
    return '\n'.join(relevant_lines)


def extract_error_context(log: str) -> Dict[str, Any]:
    """
    Log'dan hata bağlamını çıkarır.
    
    Args:
        log: Temizlenmiş log metni
        
    Returns:
        Hata bağlamı bilgileri
    """
    context = {
        'compiler': None,
        'file_paths': [],
        'line_numbers': [],
        'error_messages': [],
        'warning_messages': []
    }
    
    # Compiler türünü tespit et
    if 'dpcpp' in log.lower() or 'sycl' in log.lower():
        context['compiler'] = 'Intel DPC++'
    elif 'icx' in log.lower() or 'icpx' in log.lower():
        context['compiler'] = 'Intel ICPX'
    elif 'vtune' in log.lower():
        context['compiler'] = 'Intel VTune'
    elif 'quartus' in log.lower():
        context['compiler'] = 'Intel Quartus'
    
    # Dosya yollarını çıkar
    file_patterns = [
        r'([a-zA-Z0-9_\-\./\\]+\.(cpp|hpp|c|h|sycl|cl))',
        r'([a-zA-Z0-9_\-\./\\]+\.(o|obj|so|dll|a|lib))',
    ]
    
    for pattern in file_patterns:
        matches = re.findall(pattern, log, re.IGNORECASE)
        for match in matches:
            if match[0] not in context['file_paths']:
                context['file_paths'].append(match[0])
    
    # Satır numaralarını çıkar
    line_patterns = [
        r':(\d+):',
        r'line\s+(\d+)',
        r'at\s+line\s+(\d+)'
    ]
    
    for pattern in line_patterns:
        matches = re.findall(pattern, log)
        for match in matches:
            if match not in context['line_numbers']:
                context['line_numbers'].append(match)
    
    # Hata mesajlarını çıkar
    error_patterns = [
        r'error[^:]*:\s*([^\n]+)',
        r'fatal\s+error[^:]*:\s*([^\n]+)',
        r'failed[^:]*:\s*([^\n]+)'
    ]
    
    for pattern in error_patterns:
        matches = re.findall(pattern, log, re.IGNORECASE)
        for match in matches:
            if match.strip() not in context['error_messages']:
                context['error_messages'].append(match.strip())
    
    # Uyarı mesajlarını çıkar
    warning_patterns = [
        r'warning[^:]*:\s*([^\n]+)',
        r'note[^:]*:\s*([^\n]+)'
    ]
    
    for pattern in warning_patterns:
        matches = re.findall(pattern, log, re.IGNORECASE)
        for match in matches:
            if match.strip() not in context['warning_messages']:
                context['warning_messages'].append(match.strip())
    
    return context


def is_intel_toolchain_log(log: str) -> bool:
    """
    Log'un Intel toolchain'den gelip gelmediğini kontrol eder.
    
    Args:
        log: Log metni
        
    Returns:
        Intel toolchain log'u ise True
    """
    intel_indicators = [
        'intel', 'dpc++', 'sycl', 'oneapi', 'icx', 'icpx',
        'vtune', 'quartus', 'opencl', 'level-zero',
        'intel oneapi', 'intel(r)', 'intel®'
    ]
    
    log_lower = log.lower()
    return any(indicator in log_lower for indicator in intel_indicators) 