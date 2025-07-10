"""
Fix Recommender Module

Intel toolchain hataları için çözüm önerileri sunar.
"""

import re
from typing import List, Dict, Any


# Hata türleri için önceden tanımlanmış çözümler
ERROR_FIXES = {
    'MissingHeaderError': {
        'tr': [
            {
                'title': 'Intel oneAPI DPC++ Toolkit Kurulumu',
                'description': 'Intel oneAPI DPC++ toolkit\'in doğru kurulduğundan emin olun',
                'commands': [
                    'sudo apt-get install intel-oneapi-dpcpp-compiler',  # Ubuntu/Debian
                    'sudo yum install intel-oneapi-dpcpp-compiler',      # RHEL/CentOS
                    'brew install intel-oneapi-dpcpp-compiler'           # macOS
                ],
                'steps': [
                    'Intel oneAPI Base Toolkit\'i indirin',
                    'Kurulum sırasında DPC++ compiler seçeneğini işaretleyin',
                    'Kurulum sonrası environment\'ı source edin'
                ]
            },
            {
                'title': 'Include Path Ayarları',
                'description': 'SYCL header dosyaları için include path\'lerini ayarlayın',
                'commands': [
                    'export CPATH=/opt/intel/oneapi/compiler/latest/linux/include/sycl:$CPATH',
                    'export CPLUS_INCLUDE_PATH=/opt/intel/oneapi/compiler/latest/linux/include/sycl:$CPLUS_INCLUDE_PATH',
                    'dpcpp -I/opt/intel/oneapi/compiler/latest/linux/include/sycl your_file.cpp'
                ],
                'steps': [
                    'Intel oneAPI kurulum dizinini bulun',
                    'SYCL include path\'ini environment variable\'a ekleyin',
                    'Derleme komutunda -I flag\'i ile path belirtin'
                ]
            },
            {
                'title': 'Environment Setup',
                'description': 'Intel oneAPI environment\'ını doğru şekilde ayarlayın',
                'commands': [
                    'source /opt/intel/oneapi/setvars.sh',
                    'source /opt/intel/oneapi/compiler/latest/env/vars.sh',
                    'which dpcpp  # Compiler\'ın PATH\'te olduğunu kontrol edin'
                ],
                'steps': [
                    'setvars.sh script\'ini source edin',
                    'Environment variable\'ları kontrol edin',
                    'Compiler\'ın erişilebilir olduğunu doğrulayın'
                ]
            }
        ]
    },
    
    'Segfault': {
        'tr': [
            {
                'title': 'Bellek Erişim Kontrolü',
                'description': 'Pointer ve array erişimlerini kontrol edin',
                'commands': [
                    'dpcpp -g -O0 your_file.cpp  # Debug bilgileri ile derle',
                    'valgrind ./your_program     # Bellek hatalarını tespit et',
                    'gdb ./your_program          # Debugger ile analiz et'
                ],
                'steps': [
                    'Null pointer kontrolü ekleyin',
                    'Array bounds kontrolü yapın',
                    'SYCL kernel\'lerde bellek erişimlerini kontrol edin'
                ]
            },
            {
                'title': 'SYCL Bellek Yönetimi',
                'description': 'SYCL bellek modelini doğru kullanın',
                'commands': [
                    'sycl::buffer<int, 1> buf(data, sycl::range<1>(size));',
                    'sycl::accessor acc(buf, sycl::read_write);',
                    'queue.wait();  # Kernel completion\'ı bekle'
                ],
                'steps': [
                    'USM (Unified Shared Memory) kullanımını kontrol edin',
                    'Kernel execution completion\'ını bekleyin',
                    'Memory allocation/deallocation sırasını kontrol edin'
                ]
            }
        ]
    },
    
    'LinkerError': {
        'tr': [
            {
                'title': 'SYCL Runtime Kütüphaneleri',
                'description': 'SYCL runtime kütüphanelerini doğru link edin',
                'commands': [
                    'dpcpp your_file.cpp -fsycl',
                    'dpcpp your_file.cpp -fsycl -lOpenCL',
                    'dpcpp your_file.cpp -fsycl -lsycl'
                ],
                'steps': [
                    '-fsycl flag\'ini kullanın',
                    'OpenCL kütüphanelerini link edin',
                    'Platform-specific kütüphaneleri ekleyin'
                ]
            },
            {
                'title': 'Library Path Ayarları',
                'description': 'Kütüphane path\'lerini doğru ayarlayın',
                'commands': [
                    'export LIBRARY_PATH=/opt/intel/oneapi/compiler/latest/linux/lib:$LIBRARY_PATH',
                    'export LD_LIBRARY_PATH=/opt/intel/oneapi/compiler/latest/linux/lib:$LD_LIBRARY_PATH',
                    'dpcpp -L/opt/intel/oneapi/compiler/latest/linux/lib your_file.cpp'
                ],
                'steps': [
                    'Intel oneAPI library path\'ini ayarlayın',
                    'Runtime kütüphanelerinin erişilebilir olduğunu kontrol edin',
                    'Platform-specific kütüphaneleri ekleyin'
                ]
            }
        ]
    },
    
    'SyntaxError': {
        'tr': [
            {
                'title': 'SYCL Syntax Kontrolü',
                'description': 'SYCL syntax kurallarına uygun kod yazın',
                'commands': [
                    'dpcpp -fsyntax-only your_file.cpp  # Sadece syntax kontrolü',
                    'dpcpp -E your_file.cpp | grep -A 10 -B 10 "error"  # Preprocessor çıktısını kontrol et'
                ],
                'steps': [
                    'SYCL namespace kullanımını kontrol edin',
                    'Template syntax\'ını doğrulayın',
                    'Missing semicolon\'ları kontrol edin'
                ]
            }
        ]
    },
    
    'OpenCLError': {
        'tr': [
            {
                'title': 'OpenCL Driver Kurulumu',
                'description': 'Intel GPU driver\'larını ve OpenCL runtime\'ını kurun',
                'commands': [
                    'sudo apt-get install intel-opencl-icd',  # Ubuntu/Debian
                    'sudo yum install intel-opencl',          # RHEL/CentOS
                    'clinfo  # OpenCL platform\'ları listele'
                ],
                'steps': [
                    'Intel GPU driver\'larını güncelleyin',
                    'OpenCL runtime\'ını kurun',
                    'Platform ve device\'ların erişilebilir olduğunu kontrol edin'
                ]
            }
        ]
    },
    
    'VTuneError': {
        'tr': [
            {
                'title': 'VTune Driver Kurulumu',
                'description': 'VTune Profiler için gerekli driver\'ları kurun',
                'commands': [
                    'sudo /opt/intel/oneapi/vtune/latest/install.sh',
                    'sudo /opt/intel/oneapi/vtune/latest/sepdk/src/insmod-sep',
                    'vtune --version  # VTune versiyonunu kontrol et'
                ],
                'steps': [
                    'VTune Profiler\'ı doğru kurun',
                    'Sampling driver\'larını yükleyin',
                    'Permission ayarlarını kontrol edin'
                ]
            }
        ]
    },
    
    'QuartusError': {
        'tr': [
            {
                'title': 'Quartus Constraint Kontrolü',
                'description': 'Design constraint\'lerini kontrol edin',
                'commands': [
                    'quartus_map --read_settings_files=on your_project',
                    'quartus_fit --read_settings_files=on your_project',
                    'quartus_tan --read_settings_files=on your_project'
                ],
                'steps': [
                    'Timing constraint\'lerini kontrol edin',
                    'Resource kullanımını analiz edin',
                    'Pin assignment\'ları doğrulayın'
                ]
            }
        ]
    }
}


def suggest_fixes(error_type: str, log: str, max_fixes: int = 3) -> List[Dict[str, Any]]:
    """
    Hata türü için çözüm önerileri sunar.
    
    Args:
        error_type: Hata türü
        log: Log metni (bağlam için)
        max_fixes: Maksimum öneri sayısı
        
    Returns:
        Çözüm önerileri listesi
    """
    if error_type in ERROR_FIXES:
        fixes = ERROR_FIXES[error_type]['tr'][:max_fixes]
        
        # Log'dan çıkarılan bağlam bilgilerini kullanarak önerileri özelleştir
        context_info = extract_context_from_log(log)
        
        for fix in fixes:
            # Bağlam bilgilerine göre önerileri özelleştir
            customize_fix_for_context(fix, context_info)
        
        return fixes
    
    # Bilinmeyen hata türü için genel öneriler
    return generate_generic_fixes(error_type, log, max_fixes)


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
        'platform': None,
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
    
    # Platform bilgisini çıkar
    if 'linux' in log.lower():
        context['platform'] = 'Linux'
    elif 'windows' in log.lower() or 'win' in log.lower():
        context['platform'] = 'Windows'
    elif 'mac' in log.lower() or 'darwin' in log.lower():
        context['platform'] = 'macOS'
    
    # Hata mesajlarını çıkar
    error_matches = re.findall(r'error[^:]*:\s*([^\n]+)', log, re.IGNORECASE)
    context['error_messages'] = [msg.strip() for msg in error_matches]
    
    return context


def customize_fix_for_context(fix: Dict[str, Any], context: Dict[str, Any]):
    """
    Çözüm önerisini bağlam bilgilerine göre özelleştirir.
    
    Args:
        fix: Çözüm önerisi
        context: Bağlam bilgileri
    """
    # Platform-specific komutları filtrele
    if context.get('platform'):
        platform = context['platform']
        if platform == 'Linux':
            # Linux-specific komutları tut, diğerlerini kaldır
            fix['commands'] = [cmd for cmd in fix['commands'] 
                             if not any(os in cmd.lower() for os in ['windows', 'macos', 'brew'])]
        elif platform == 'Windows':
            # Windows-specific komutları tut
            fix['commands'] = [cmd for cmd in fix['commands'] 
                             if any(os in cmd.lower() for os in ['windows', 'choco', 'winget'])]
        elif platform == 'macOS':
            # macOS-specific komutları tut
            fix['commands'] = [cmd for cmd in fix['commands'] 
                             if any(os in cmd.lower() for os in ['macos', 'brew'])]
    
    # Compiler-specific öneriler ekle
    if context.get('compiler_info'):
        compiler = context['compiler_info']
        if compiler == 'Intel DPC++':
            fix['steps'].append('DPC++ compiler flag\'lerini kontrol edin (-fsycl)')
        elif compiler == 'Intel VTune':
            fix['steps'].append('VTune Profiler permission ayarlarını kontrol edin')
    
    # Dosya-specific öneriler ekle
    if context.get('files'):
        files = context['files']
        if any('.sycl' in f for f in files):
            fix['steps'].append('SYCL dosyalarının doğru derlendiğinden emin olun')
        if any('.cl' in f for f in files):
            fix['steps'].append('OpenCL kernel dosyalarının doğru işlendiğini kontrol edin')


def generate_generic_fixes(error_type: str, log: str, max_fixes: int) -> List[Dict[str, Any]]:
    """
    Bilinmeyen hata türü için genel çözüm önerileri oluşturur.
    
    Args:
        error_type: Hata türü
        log: Log metni
        max_fixes: Maksimum öneri sayısı
        
    Returns:
        Genel çözüm önerileri
    """
    context_info = extract_context_from_log(log)
    
    generic_fixes = [
        {
            'title': 'Intel oneAPI Kurulum Kontrolü',
            'description': 'Intel oneAPI toolkit\'in doğru kurulduğunu kontrol edin',
            'commands': [
                'source /opt/intel/oneapi/setvars.sh',
                'which dpcpp',
                'dpcpp --version'
            ],
            'steps': [
                'Intel oneAPI Base Toolkit\'in kurulu olduğunu kontrol edin',
                'Environment variable\'ların doğru set edildiğini kontrol edin',
                'Compiler\'ın PATH\'te olduğunu doğrulayın'
            ]
        },
        {
            'title': 'Log Analizi',
            'description': 'Hata log\'unu detaylı analiz edin',
            'commands': [
                'grep -i "error" your_log_file',
                'grep -i "fatal" your_log_file',
                'grep -i "failed" your_log_file'
            ],
            'steps': [
                'Log dosyasını tam olarak inceleyin',
                'Hata mesajlarını Intel dokümantasyonunda araştırın',
                'Benzer hatalar için Intel forum\'larını kontrol edin'
            ]
        },
        {
            'title': 'Sistem Gereksinimleri',
            'description': 'Sistem gereksinimlerini kontrol edin',
            'commands': [
                'uname -a  # Linux kernel versiyonu',
                'lscpu     # CPU bilgileri',
                'lspci | grep -i intel  # Intel GPU kontrolü'
            ],
            'steps': [
                'İşletim sistemi versiyonunu kontrol edin',
                'CPU ve GPU uyumluluğunu doğrulayın',
                'Driver versiyonlarını güncelleyin'
            ]
        }
    ]
    
    # Bağlam bilgilerine göre özelleştir
    for fix in generic_fixes:
        customize_fix_for_context(fix, context_info)
    
    return generic_fixes[:max_fixes]


def get_fix_priority(fix: Dict[str, Any]) -> int:
    """
    Çözüm önerisinin öncelik skorunu hesaplar.
    
    Args:
        fix: Çözüm önerisi
        
    Returns:
        Öncelik skoru (düşük sayı = yüksek öncelik)
    """
    priority = 0
    
    # Kurulum ile ilgili öneriler daha yüksek öncelikli
    if any(word in fix['title'].lower() for word in ['kurulum', 'install', 'setup']):
        priority -= 10
    
    # Environment ile ilgili öneriler
    if any(word in fix['title'].lower() for word in ['environment', 'path', 'variable']):
        priority -= 5
    
    # Debug ile ilgili öneriler daha düşük öncelikli
    if any(word in fix['title'].lower() for word in ['debug', 'analiz', 'log']):
        priority += 5
    
    return priority


def sort_fixes_by_priority(fixes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Çözüm önerilerini öncelik sırasına göre sıralar.
    
    Args:
        fixes: Çözüm önerileri listesi
        
    Returns:
        Sıralanmış çözüm önerileri
    """
    return sorted(fixes, key=get_fix_priority) 