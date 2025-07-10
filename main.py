#!/usr/bin/env python3
"""
🧠 LLM-Powered Error Log Debugger for Intel Toolchains

Intel toolchain'lerinden gelen hata loglarını analiz eden AI aracı.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from parser import parse_log
from classifier import classify_error
from explainer import generate_explanation
from fixer import suggest_fixes
from formatter import format_markdown_summary


def main():
    parser = argparse.ArgumentParser(
        description="Intel toolchain hata loglarını analiz eden AI aracı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py -f error.log
  python main.py -i "fatal error: 'CL/sycl.hpp' file not found"
  cat error.log | python main.py
        """
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Analiz edilecek log dosyasının yolu"
    )
    
    parser.add_argument(
        "-i", "--input",
        type=str,
        help="Doğrudan analiz edilecek log metni"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Çıktı dosyasının yolu (varsayılan: stdout)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Detaylı çıktı göster"
    )
    
    args = parser.parse_args()
    
    # Giriş verisini al
    log_content = ""
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                log_content = f.read()
        except FileNotFoundError:
            print(f"❌ Hata: '{args.file}' dosyası bulunamadı.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Dosya okuma hatası: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.input:
        log_content = args.input
    
    else:
        # stdin'den oku
        if not sys.stdin.isatty():
            log_content = sys.stdin.read()
        else:
            print("❌ Hata: Giriş verisi belirtilmedi. -f, -i kullanın veya stdin'den veri gönderin.", file=sys.stderr)
            parser.print_help()
            sys.exit(1)
    
    if not log_content.strip():
        print("❌ Hata: Boş log içeriği.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Pipeline'ı çalıştır
        if args.verbose:
            print("🔍 Log analizi başlatılıyor...", file=sys.stderr)
        
        # 1. Log'u parse et
        cleaned_log = parse_log(log_content)
        if args.verbose:
            print("✅ Log temizlendi", file=sys.stderr)
        
        # 2. Hatayı sınıflandır
        error_info = classify_error(cleaned_log)
        if args.verbose:
            print(f"✅ Hata sınıflandırıldı: {error_info['type']}", file=sys.stderr)
        
        # 3. Açıklama oluştur
        explanation = generate_explanation(error_info['type'], cleaned_log)
        if args.verbose:
            print("✅ Açıklama oluşturuldu", file=sys.stderr)
        
        # 4. Çözüm önerileri
        fixes = suggest_fixes(error_info['type'], cleaned_log)
        if args.verbose:
            print("✅ Çözüm önerileri oluşturuldu", file=sys.stderr)
        
        # 5. Markdown formatında çıktı
        result = format_markdown_summary(
            error_info=error_info,
            explanation=explanation,
            fixes=fixes,
            original_log=log_content
        )
        
        # Çıktıyı yaz
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            if args.verbose:
                print(f"✅ Sonuç '{args.output}' dosyasına yazıldı", file=sys.stderr)
        else:
            print(result)
            
    except Exception as e:
        print(f"❌ Analiz sırasında hata oluştu: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 