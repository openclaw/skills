#!/usr/bin/env python3
"""
Minimal Substack Formatter - Pure formatting only
No content changes, no added CTAs, just visual improvements
"""

import re
import sys
import html

class MinimalSubstackFormatter:
    def __init__(self):
        pass
    
    def format_text(self, text):
        """Apply minimal formatting - pure visual improvements only"""
        # Clean input but preserve original structure
        text = self.clean_input(text)
        
        # Split into sentences
        sentences = self.split_sentences(text)
        
        if not sentences:
            return f"<p>{html.escape(text)}</p>"
        
        html_parts = []
        
        # Convert each sentence to paragraph, with minimal emphasis
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Apply very minimal emphasis to first and last sentences
            if i == 0 and len(sentences) > 1:
                # Slight emphasis on opening
                html_parts.append(f"<p><strong>{html.escape(sentence)}</strong></p>")
            elif i == len(sentences) - 1 and len(sentences) > 2:
                # Slight emphasis on conclusion
                html_parts.append(f"<p><em>{html.escape(sentence)}</em></p>")
            else:
                # Regular paragraph
                html_parts.append(f"<p>{html.escape(sentence)}</p>")
        
        return '\n\n'.join(html_parts)
    
    def format_text_minimal(self, text):
        """Even more minimal - just proper HTML paragraphs, no emphasis"""
        text = self.clean_input(text)
        sentences = self.split_sentences(text)
        
        html_parts = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                html_parts.append(f"<p>{html.escape(sentence)}</p>")
        
        return '\n\n'.join(html_parts)
    
    def format_text_spacing_only(self, text):
        """Pure spacing formatting - preserve exact content, just add paragraph breaks"""
        # Split by existing paragraph breaks first
        paragraphs = text.split('\n\n')
        
        html_parts = []
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Convert single paragraph to HTML, preserving line breaks
                lines = paragraph.split('\n')
                if len(lines) == 1:
                    html_parts.append(f"<p>{html.escape(paragraph)}</p>")
                else:
                    # Multiple lines within paragraph - use <br> tags
                    formatted_lines = '<br>'.join(html.escape(line.strip()) for line in lines if line.strip())
                    html_parts.append(f"<p>{formatted_lines}</p>")
        
        return '\n\n'.join(html_parts)
    
    def clean_input(self, text):
        """Minimal cleanup - just remove excessive whitespace"""
        return re.sub(r'\n\s*\n\s*\n+', '\n\n', text.strip())
    
    def split_sentences(self, text):
        """Split into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

def main():
    formatter = MinimalSubstackFormatter()
    
    if len(sys.argv) < 2:
        print("Usage: python3 minimal_formatter.py 'your text here' [mode]")
        print("Modes:")
        print("  default: Minimal emphasis (first/last sentence)")  
        print("  minimal: Just paragraph formatting, no emphasis")
        print("  spacing: Pure spacing, preserve exact content")
        return
    
    text = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    if mode == "minimal":
        formatted = formatter.format_text_minimal(text)
    elif mode == "spacing":
        formatted = formatter.format_text_spacing_only(text)
    else:
        formatted = formatter.format_text(text)
    
    print(formatted)

if __name__ == "__main__":
    main()