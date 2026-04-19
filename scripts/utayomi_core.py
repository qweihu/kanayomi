#!/usr/bin/env python3
"""
Utayomi - 日语歌词注音工具

用法：
    # 从标准输入注音
    echo "歌词文本" | python scripts/utayomi_core.py
    
    # 从文件注音
    python scripts/utayomi_core.py < lyrics.txt
    
    # 罗马音模式
    python scripts/utayomi_core.py --romaji < lyrics.txt
"""
import sys
import re
import argparse
import pykakasi
import fugashi


def has_kanji(text):
    """检查文本中是否包含日文汉字"""
    return bool(re.search(r'[\u4e00-\u9faf]', text))


def has_japanese(text):
    """检查文本中是否包含任何日文字符（汉字、平假名、片假名）"""
    return bool(re.search(r'[\u4e00-\u9faf\u3040-\u309f\u30a0-\u30ff]', text))


def convert_to_ruby(text, mode='hiragana'):
    """
    将日文文本转换为带有 <ruby> 标签的格式
    
    Args:
        text: 输入文本（应为已清洗的纯文本）
        mode: 'hiragana' 或 'romaji'，默认为平假名
    """
    tagger = fugashi.Tagger()
    kks = pykakasi.Kakasi()
    
    lines = text.split('\n')
    result_lines = []
    
    for line in lines:
        if not line.strip():
            result_lines.append('')
            continue
            
        result_line = ""
        words = tagger(line)
        
        for word in words:
            surface = word.surface
            
            if mode == 'romaji':
                # 罗马音模式：对包含日文的词汇进行罗马音转换
                if not has_japanese(surface):
                    result_line += surface
                    continue
                
                converted = kks.convert(surface)
                for item in converted:
                    orig = item['orig']
                    if has_japanese(orig):
                        romaji = item['hepburn']
                        result_line += f"<ruby>{orig}<rt>{romaji}</rt></ruby>"
                    else:
                        result_line += orig
            else:
                # 平假名模式：仅对包含汉字的词汇进行转换
                if not has_kanji(surface):
                    result_line += surface
                    continue
                
                # 使用 pykakasi 进行细粒度拆分
                converted = kks.convert(surface)
                
                # 尝试拆分每个字符，处理送假名
                for item in converted:
                    orig = item['orig']
                    hira = item['hira']
                    
                    # 如果是汉字，标注读音
                    if has_kanji(orig):
                        result_line += f"<ruby>{orig}<rt>{hira}</rt></ruby>"
                    else:
                        # 假名直接保留
                        result_line += orig
                        
        result_lines.append(result_line)
        
    return '\n'.join(result_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Utayomi - 日语歌词注音工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  echo "夢ならばどれほどよかったでしょう" | python scripts/utayomi_core.py
  cat lyrics.txt | python scripts/utayomi_core.py --romaji
        '''
    )
    
    parser.add_argument(
        '--romaji', '-r',
        action='store_true',
        help='使用罗马音标注（默认使用平假名）'
    )
    
    args = parser.parse_args()
    
    # 从标准输入读取，并清理末尾换行符
    input_content = sys.stdin.read().strip()
    
    if not input_content:
        print("Error: 没有输入内容。请通过管道传入文本。", file=sys.stderr)
        print("用法: echo '歌词' | python scripts/utayomi_core.py", file=sys.stderr)
        sys.exit(1)
    
    # 转换注音
    mode = 'romaji' if args.romaji else 'hiragana'
    ruby_text = convert_to_ruby(input_content, mode=mode)
    
    # 输出结果
    print(ruby_text)


if __name__ == "__main__":
    main()