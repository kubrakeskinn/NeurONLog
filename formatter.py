"""
Markdown Formatter Module

Analiz sonuçlarını markdown formatında formatlar.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime


def format_markdown_summary(
    error_info: Dict[str, Any],
    explanation: str,
    fixes: List[Dict[str, Any]],
    original_log: str,
    include_original_log: bool = False
) -> str:
    """
    Analiz sonuçlarını markdown formatında formatlar.
    
    Args:
        error_info: Hata bilgileri
        explanation: Hata açıklaması
        fixes: Çözüm önerileri
        original_log: Orijinal log metni
        include_original_log: Orijinal log'u dahil et
        
    Returns:
        Markdown formatında rapor
    """
    # Başlık ve özet
    markdown = f"""# 🧠 Intel Toolchain Hata Analizi

**Analiz Tarihi:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🔍 Hata Özeti

**Hata Türü:** `{error_info['type']}`  
**Güvenilirlik:** {error_info['confidence']:.1%}  
**Önem Derecesi:** {get_severity_emoji(error_info.get('severity', 'low'))} {error_info.get('severity', 'low').title()}

{error_info.get('description', 'Açıklama bulunamadı')}

"""
    
    # Bağlam bilgileri
    if error_info.get('context'):
        context = error_info['context']
        markdown += "### 📋 Bağlam Bilgileri\n\n"
        
        if context.get('compiler_info'):
            markdown += f"- **Compiler:** {context['compiler_info']}\n"
        
        if context.get('files'):
            markdown += f"- **Etkilenen Dosyalar:** {', '.join(context['files'])}\n"
        
        if context.get('line_numbers'):
            markdown += f"- **Satır Numaraları:** {', '.join(context['line_numbers'])}\n"
        
        if context.get('error_messages'):
            markdown += f"- **Hata Mesajları:** {', '.join(context['error_messages'])}\n"
        
        markdown += "\n"
    
    # Açıklama
    markdown += f"## 📖 Açıklama\n\n{explanation}\n\n"
    
    # Çözüm önerileri
    markdown += "## 🛠️ Önerilen Çözümler\n\n"
    
    for i, fix in enumerate(fixes, 1):
        markdown += format_fix_section(fix, i)
    
    # Intel dokümantasyon linkleri
    markdown += get_intel_documentation_links(error_info['type'])
    
    # Orijinal log (opsiyonel)
    if include_original_log:
        markdown += f"""
## 📄 Orijinal Log

```log
{original_log}
```
"""
    
    # Footer
    markdown += f"""
---

*Bu analiz NeurONLog AI aracı tarafından oluşturulmuştur.*  
*Intel oneAPI ve toolchain'ler için özel olarak tasarlanmıştır.*
"""
    
    return markdown


def format_fix_section(fix: Dict[str, Any], index: int) -> str:
    """
    Tek bir çözüm önerisini formatlar.
    
    Args:
        fix: Çözüm önerisi
        index: Öneri numarası
        
    Returns:
        Formatlanmış çözüm önerisi
    """
    markdown = f"### {index}. {fix['title']}\n\n"
    markdown += f"{fix['description']}\n\n"
    
    # Komutlar
    if fix.get('commands'):
        markdown += "**Komutlar:**\n"
        markdown += "```bash\n"
        for cmd in fix['commands']:
            markdown += f"{cmd}\n"
        markdown += "```\n\n"
    
    # Adımlar
    if fix.get('steps'):
        markdown += "**Adımlar:**\n"
        for step in fix['steps']:
            markdown += f"- {step}\n"
        markdown += "\n"
    
    return markdown


def get_severity_emoji(severity: str) -> str:
    """
    Önem derecesi için emoji döndürür.
    
    Args:
        severity: Önem derecesi
        
    Returns:
        Emoji
    """
    emoji_map = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }
    return emoji_map.get(severity, '⚪')


def get_intel_documentation_links(error_type: str) -> str:
    """
    Hata türü için Intel dokümantasyon linklerini döndürür.
    
    Args:
        error_type: Hata türü
        
    Returns:
        Dokümantasyon linkleri
    """
    doc_links = {
        'MissingHeaderError': [
            ('Intel oneAPI DPC++ Compiler', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html'),
            ('SYCL Programming Guide', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/sycl.html'),
            ('oneAPI Installation Guide', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/get-started.html')
        ],
        'Segfault': [
            ('SYCL Memory Management', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/sycl-memory-management.html'),
            ('Intel GPU Programming', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/intel-gpu-programming.html'),
            ('Debugging SYCL Applications', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/debugging-sycl.html')
        ],
        'LinkerError': [
            ('SYCL Runtime Libraries', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/sycl-runtime.html'),
            ('oneAPI Linking Guide', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/linking-guide.html'),
            ('OpenCL Integration', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/opencl-integration.html')
        ],
        'OpenCLError': [
            ('Intel OpenCL Runtime', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/opencl.html'),
            ('GPU Driver Installation', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/gpu-driver-installation.html'),
            ('OpenCL Programming Guide', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/opencl-programming-guide.html')
        ],
        'VTuneError': [
            ('VTune Profiler User Guide', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-user-guide.html'),
            ('Profiling Driver Installation', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-driver-installation.html'),
            ('Performance Analysis', 'https://www.intel.com/content/www/us/en/developer/tools/oneapi/performance-analysis.html')
        ],
        'QuartusError': [
            ('Quartus Prime User Guide', 'https://www.intel.com/content/www/us/en/developer/tools/quartus-prime/user-guide.html'),
            ('FPGA Design Constraints', 'https://www.intel.com/content/www/us/en/developer/tools/quartus-prime/constraints-guide.html'),
            ('Synthesis and Fitting', 'https://www.intel.com/content/www/us/en/developer/tools/quartus-prime/synthesis-fitting.html')
        ]
    }
    
    if error_type not in doc_links:
        return ""
    
    markdown = "\n## 🔗 İlgili Dokümantasyon\n\n"
    
    for title, url in doc_links[error_type]:
        markdown += f"- [{title}]({url})\n"
    
    markdown += "\n"
    return markdown


def format_error_details(error_info: Dict[str, Any]) -> str:
    """
    Hata detaylarını formatlar.
    
    Args:
        error_info: Hata bilgileri
        
    Returns:
        Formatlanmış hata detayları
    """
    markdown = f"""
### Hata Detayları

- **Tür:** {error_info['type']}
- **Güvenilirlik:** {error_info['confidence']:.1%}
- **Önem:** {error_info.get('severity', 'low').title()}
"""
    
    if error_info.get('patterns'):
        markdown += f"- **Eşleşen Pattern'ler:** {', '.join(error_info['patterns'])}\n"
    
    return markdown


def format_quick_fix_summary(fixes: List[Dict[str, Any]]) -> str:
    """
    Hızlı çözüm özeti oluşturur.
    
    Args:
        fixes: Çözüm önerileri
        
    Returns:
        Hızlı özet
    """
    if not fixes:
        return "Çözüm önerisi bulunamadı."
    
    markdown = "### 🚀 Hızlı Çözüm\n\n"
    
    # En yüksek öncelikli çözümü göster
    primary_fix = fixes[0]
    markdown += f"**{primary_fix['title']}**\n\n"
    markdown += f"{primary_fix['description']}\n\n"
    
    if primary_fix.get('commands'):
        markdown += "**Ana Komut:**\n"
        markdown += f"```bash\n{primary_fix['commands'][0]}\n```\n\n"
    
    return markdown


def format_troubleshooting_tips(error_type: str) -> str:
    """
    Hata türü için genel sorun giderme ipuçları oluşturur.
    
    Args:
        error_type: Hata türü
        
    Returns:
        Sorun giderme ipuçları
    """
    tips = {
        'MissingHeaderError': [
            'Intel oneAPI kurulum dizinini kontrol edin',
            'Environment variable\'ları yeniden set edin',
            'Include path\'lerini manuel olarak belirtin'
        ],
        'Segfault': [
            'Debug flag\'leri ile derleyin (-g -O0)',
            'Valgrind ile bellek hatalarını tespit edin',
            'SYCL kernel\'lerde bellek erişimlerini kontrol edin'
        ],
        'LinkerError': [
            'SYCL runtime kütüphanelerini kontrol edin',
            'Library path\'lerini doğrulayın',
            'Platform-specific flag\'leri ekleyin'
        ],
        'OpenCLError': [
            'Intel GPU driver\'larını güncelleyin',
            'OpenCL runtime kurulumunu kontrol edin',
            'Platform ve device erişimini test edin'
        ]
    }
    
    if error_type not in tips:
        return ""
    
    markdown = "\n### 💡 Genel İpuçları\n\n"
    
    for tip in tips[error_type]:
        markdown += f"- {tip}\n"
    
    markdown += "\n"
    return markdown


def create_minimal_report(error_info: Dict[str, Any], fixes: List[Dict[str, Any]]) -> str:
    """
    Minimal rapor oluşturur (CLI için).
    
    Args:
        error_info: Hata bilgileri
        fixes: Çözüm önerileri
        
    Returns:
        Minimal rapor
    """
    markdown = f"## {error_info['type']}\n\n"
    markdown += f"{error_info.get('description', 'Açıklama bulunamadı')}\n\n"
    
    if fixes:
        markdown += "**Çözüm:**\n"
        primary_fix = fixes[0]
        markdown += f"- {primary_fix['title']}: {primary_fix['description']}\n"
        
        if primary_fix.get('commands'):
            markdown += f"  ```bash\n  {primary_fix['commands'][0]}\n  ```\n"
    
    return markdown 