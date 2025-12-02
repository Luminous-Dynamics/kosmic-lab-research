#!/usr/bin/env python3
"""
Count words in LaTeX manuscript, excluding commands and comments.
Provides accurate word count for journal submission limits.
"""

import re
from pathlib import Path

def count_latex_words(tex_file):
    """Count words in LaTeX file, excluding commands and metadata."""

    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove comments (lines starting with %)
    content = re.sub(r'%.*$', '', content, flags=re.MULTILINE)

    # Remove preamble (everything before \begin{document})
    content = re.sub(r'^.*?\\begin\{document\}', '', content, flags=re.DOTALL)

    # Remove bibliography (everything after \begin{thebibliography})
    content = re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}', '', content, flags=re.DOTALL)

    # Remove \end{document} and everything after
    content = re.sub(r'\\end\{document\}.*$', '', content, flags=re.DOTALL)

    # Remove LaTeX commands (but keep their arguments for text commands)
    # Remove \section, \subsection, etc. but keep the title
    content = re.sub(r'\\(sub)*section\*?\{([^}]+)\}', r'\2', content)

    # Remove \cite commands
    content = re.sub(r'\\cite\{[^}]+\}', '', content)

    # Remove \ref commands
    content = re.sub(r'\\ref\{[^}]+\}', '', content)

    # Remove \label commands
    content = re.sub(r'\\label\{[^}]+\}', '', content)

    # Remove other common commands that don't contribute text
    content = re.sub(r'\\(textbf|textit|emph)\{([^}]+)\}', r'\2', content)

    # Remove math environments but count text within
    content = re.sub(r'\$[^$]+\$', '', content)
    content = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{align\}.*?\\end\{align\}', '', content, flags=re.DOTALL)

    # Remove tables and figures
    content = re.sub(r'\\begin\{table\}.*?\\end\{table\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}', '', content, flags=re.DOTALL)

    # Remove other LaTeX commands
    content = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?\{[^}]*\}', '', content)
    content = re.sub(r'\\[a-zA-Z]+\*?', '', content)

    # Remove special characters and extra whitespace
    content = re.sub(r'[{}]', '', content)
    content = re.sub(r'\\', '', content)

    # Count words
    words = content.split()
    word_count = len(words)

    # Also count by section for detailed breakdown
    sections = {}

    with open(tex_file, 'r', encoding='utf-8') as f:
        full_content = f.read()

    # Extract sections
    section_pattern = r'\\section\{([^}]+)\}(.*?)(?=\\section|\\begin\{thebibliography\}|\\end\{document\}|$)'
    matches = re.finditer(section_pattern, full_content, re.DOTALL)

    for match in matches:
        section_name = match.group(1)
        section_text = match.group(2)

        # Apply same cleaning to section text
        section_clean = re.sub(r'%.*$', '', section_text, flags=re.MULTILINE)
        section_clean = re.sub(r'\\cite\{[^}]+\}', '', section_clean)
        section_clean = re.sub(r'\$[^$]+\$', '', section_clean)
        section_clean = re.sub(r'\\begin\{equation\}.*?\\end\{equation\}', '', section_clean, flags=re.DOTALL)
        section_clean = re.sub(r'\\begin\{table\}.*?\\end\{table\}', '', section_clean, flags=re.DOTALL)
        section_clean = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', section_clean, flags=re.DOTALL)
        section_clean = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?\{[^}]*\}', '', section_clean)
        section_clean = re.sub(r'\\[a-zA-Z]+\*?', '', section_clean)
        section_clean = re.sub(r'[{}\\]', '', section_clean)

        sections[section_name] = len(section_clean.split())

    return word_count, sections

if __name__ == '__main__':
    tex_file = Path(__file__).parent / 'k_index_manuscript.tex'

    print("=" * 70)
    print("MANUSCRIPT WORD COUNT ANALYSIS")
    print("=" * 70)
    print()

    total_words, sections = count_latex_words(tex_file)

    print(f"Total Word Count: {total_words:,}")
    print()
    print("Journal Limits:")
    print(f"  Nature:  3,000 words  {'✅ WITHIN LIMIT' if total_words <= 3000 else '❌ EXCEEDS by ' + str(total_words - 3000)}")
    print(f"  Science: 4,500 words  {'✅ WITHIN LIMIT' if total_words <= 4500 else '❌ EXCEEDS by ' + str(total_words - 4500)}")
    print(f"  PNAS:    3,000 words  {'✅ WITHIN LIMIT' if total_words <= 3000 else '❌ EXCEEDS by ' + str(total_words - 3000)}")
    print()

    if sections:
        print("Word Count by Section:")
        print("-" * 70)
        for section, count in sections.items():
            print(f"  {section:<50} {count:>6,} words")
        print()

    # Recommendations
    print("Recommendations:")
    print("-" * 70)
    if total_words <= 3000:
        print("✅ Manuscript is within all journal limits - no trimming needed!")
    elif total_words <= 4500:
        print("⚠️  Manuscript exceeds Nature/PNAS limits but fits Science")
        print("   Options:")
        print("   1. Target Science first (fits current length)")
        print("   2. Trim", total_words - 3000, "words for Nature/PNAS")
    else:
        print("❌ Manuscript exceeds all journal limits")
        print("   Must trim", total_words - 4500, "words minimum for Science")
        print("   Or trim", total_words - 3000, "words for Nature/PNAS")
    print()
