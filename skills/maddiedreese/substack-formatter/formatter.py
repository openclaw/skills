#!/usr/bin/env python3
"""
Substack Article Formatter - Transform plain text using viral Substack patterns
Based on analysis of 80+ viral Substack posts
"""

import re
import sys
import html

class SubstackFormatter:
    def __init__(self):
        self.engagement_questions = [
            "What's your experience with this?",
            "How does this land for you?", 
            "What would you add?",
            "Does this resonate?",
            "What's your take?",
            "Have you noticed this too?",
            "What am I missing here?",
            "Share your story below 👇"
        ]
        
        self.contrarian_hooks = [
            "Everyone says",
            "Most people think", 
            "The conventional wisdom is",
            "You've probably heard",
            "The popular belief is"
        ]
    
    def format_text(self, text, structure="minimal", target_length="optimal"):
        """Apply Substack formatting to input text"""
        # Clean and analyze input
        text = self.clean_input(text)
        word_count = len(text.split())
        
        # Determine structure if auto
        if structure == "auto":
            structure = self.detect_best_structure(text, word_count)
        
        # Format based on structure type
        if structure == "punchy-wisdom":
            return self.format_punchy_wisdom(text)
        elif structure == "micro-story":
            return self.format_micro_story(text)
        elif structure == "list":
            return self.format_list(text)
        elif structure == "contrarian":
            return self.format_contrarian(text)
        elif structure == "relatable":
            return self.format_relatable(text)
        elif structure == "poetic":
            return self.format_poetic(text)
        else:
            return self.format_general(text, target_length)
    
    def clean_input(self, text):
        """Basic cleanup of input text"""
        # Remove extra whitespace but preserve intentional breaks
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned = line.strip()
            if cleaned:
                cleaned_lines.append(cleaned)
            elif cleaned_lines and cleaned_lines[-1]:
                cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines)
    
    def detect_best_structure(self, text, word_count):
        """Auto-detect the best structure based on content"""
        text_lower = text.lower()
        
        # Very short = punchy wisdom
        if word_count < 40:
            return "punchy-wisdom"
        
        # Contains story elements = micro-story  
        story_indicators = ['i was', 'last week', 'yesterday', 'then i', 'suddenly', 'but then']
        if any(indicator in text_lower for indicator in story_indicators):
            return "micro-story"
            
        # Contains contrarian language = contrarian
        if any(hook.lower() in text_lower for hook in self.contrarian_hooks):
            return "contrarian"
            
        # Contains list patterns = list
        list_indicators = ['first', 'second', 'third', '1.', '2.', '3.', '•', '-']
        if any(indicator in text_lower for indicator in list_indicators):
            return "list"
            
        # Contains humor indicators = relatable
        humor_indicators = ['lol', 'haha', 'funny', 'hilarious', 'ridiculous']
        if any(indicator in text_lower for indicator in humor_indicators):
            return "relatable"
            
        # Default to general formatting
        return "general"
    
    def format_punchy_wisdom(self, text):
        """Format as punchy wisdom (30-60 words)"""
        sentences = self.split_sentences(text)
        
        if len(sentences) < 2:
            # Single powerful statement
            return f"<p><strong>{html.escape(sentences[0])}</strong></p>"
        
        # First sentence as hook, rest as context
        hook = sentences[0]
        context = '. '.join(sentences[1:])
        
        return f"""<p><strong>{html.escape(hook)}</strong></p>

<p>{html.escape(context)}</p>"""
    
    def format_micro_story(self, text):
        """Format as micro-story with twist ending"""
        sentences = self.split_sentences(text)
        
        if len(sentences) < 3:
            return self.format_general(text, "optimal")
        
        # Group into story parts
        setup = sentences[:len(sentences)//2]
        twist = sentences[len(sentences)//2:-1] 
        revelation = sentences[-1]
        
        html_parts = []
        
        # Setup (hook the reader)
        for sentence in setup[:2]:  # Max 2 setup sentences
            html_parts.append(f"<p>{html.escape(sentence)}</p>")
        
        # Twist/action (short paragraphs)
        if twist:
            twist_text = '. '.join(twist)
            # Break into short lines for tension
            twist_parts = self.break_into_short_lines(twist_text)
            for part in twist_parts:
                html_parts.append(f"<p>{html.escape(part)}</p>")
        
        # Revelation (emphasized)
        html_parts.append(f"<p><strong>{html.escape(revelation)}</strong></p>")
        
        # Add engagement question
        html_parts.append(f"<p><em>{self.get_random_question()}</em></p>")
        
        return '\n\n'.join(html_parts)
    
    def format_list(self, text):
        """Format as bulleted/numbered list"""
        items = self.extract_list_items(text)
        intro = self.extract_intro_text(text)
        
        html_parts = []
        
        # Add intro if exists
        if intro:
            html_parts.append(f"<p><strong>{html.escape(intro)}</strong></p>")
        
        # Format items
        if len(items) > 1:
            html_parts.append("<ul>")
            for item in items[:5]:  # Max 5 items for optimal length
                clean_item = self.clean_list_item(item)
                html_parts.append(f"<li><strong>{html.escape(clean_item)}</strong></li>")
            html_parts.append("</ul>")
        
        # Add CTA
        html_parts.append(f"<p><em>{self.get_random_question()}</em></p>")
        
        return '\n'.join(html_parts)
    
    def format_contrarian(self, text):
        """Format contrarian take with hook-evidence-conclusion"""
        sentences = self.split_sentences(text)
        
        if len(sentences) < 2:
            return self.format_punchy_wisdom(text)
        
        # First sentence should be the contrarian hook
        hook = sentences[0]
        evidence = sentences[1:-1] if len(sentences) > 2 else []
        conclusion = sentences[-1] if len(sentences) > 1 else ""
        
        html_parts = []
        
        # Bold contrarian statement  
        html_parts.append(f"<p><strong>{html.escape(hook)}</strong></p>")
        
        # Evidence (if any)
        if evidence:
            evidence_text = '. '.join(evidence)
            html_parts.append(f"<p>{html.escape(evidence_text)}</p>")
        
        # Conclusion
        if conclusion:
            html_parts.append(f"<p><em>{html.escape(conclusion)}</em></p>")
        
        # Engagement question
        html_parts.append(f"<p>{self.get_random_question()}</p>")
        
        return '\n\n'.join(html_parts)
    
    def format_relatable(self, text):
        """Format relatable humor with setup-scenario-punchline"""
        sentences = self.split_sentences(text)
        
        if len(sentences) < 2:
            return self.format_general(text, "optimal")
        
        # Structure: setup, scenario(s), punchline
        setup = sentences[0]
        scenario = sentences[1:-1] if len(sentences) > 2 else []
        punchline = sentences[-1]
        
        html_parts = []
        
        # Setup
        html_parts.append(f"<p>{html.escape(setup)}</p>")
        
        # Scenario (short lines for comedic timing)
        for sentence in scenario:
            html_parts.append(f"<p>{html.escape(sentence)}</p>")
        
        # Punchline (emphasized)
        html_parts.append(f"<p><strong>{html.escape(punchline)}</strong></p>")
        
        # Light engagement
        html_parts.append(f"<p><em>Can you relate? 😅</em></p>")
        
        return '\n\n'.join(html_parts)
    
    def format_poetic(self, text):
        """Format as poetic reflection with rhythm"""
        lines = text.split('. ')
        
        html_parts = []
        html_parts.append("<p>")
        
        # Each phrase on its own line with <br> tags
        for i, line in enumerate(lines):
            if i > 0:
                html_parts.append("<br>")
            html_parts.append(html.escape(line.strip()))
        
        html_parts.append("</p>")
        
        # Add reflective CTA
        html_parts.append(f"<p><em>What resonates with you?</em></p>")
        
        return '\n'.join(html_parts)
    
    def format_general(self, text, target_length):
        """General formatting with viral patterns applied"""
        sentences = self.split_sentences(text)
        
        # Optimize for target length (50-120 words optimal)
        word_count = len(text.split())
        
        html_parts = []
        
        # Strong opening
        if sentences:
            html_parts.append(f"<p><strong>{html.escape(sentences[0])}</strong></p>")
        
        # Body with short paragraphs
        body_sentences = sentences[1:-1] if len(sentences) > 2 else sentences[1:]
        for sentence in body_sentences:
            # Emphasize key insights
            if self.is_key_insight(sentence):
                html_parts.append(f"<p><em>{html.escape(sentence)}</em></p>")
            else:
                html_parts.append(f"<p>{html.escape(sentence)}</p>")
        
        # Strong conclusion if available
        if len(sentences) > 1:
            conclusion = sentences[-1]
            html_parts.append(f"<p><strong>{html.escape(conclusion)}</strong></p>")
        
        # Engagement CTA
        html_parts.append(f"<p>{self.get_random_question()}</p>")
        
        return '\n\n'.join(html_parts)
    
    def split_sentences(self, text):
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def break_into_short_lines(self, text, max_words=8):
        """Break text into short lines for tension/readability"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(current_line) >= max_words or word.endswith('.'):
                lines.append(' '.join(current_line))
                current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def extract_list_items(self, text):
        """Extract list items from text"""
        patterns = [
            r'^\d+[.)]\s*(.+)',  # 1. or 1)
            r'^\*\s*(.+)',       # * bullets  
            r'^\-\s*(.+)',       # - bullets
            r'(?:First|Second|Third|Fourth|Fifth)[,\s]+(.+?)(?=(?:First|Second|Third|Fourth|Fifth|$))'
        ]
        
        items = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
            if matches:
                items.extend(matches)
                break
        
        # Fallback: split by periods if no clear list pattern
        if not items:
            sentences = self.split_sentences(text)
            if len(sentences) > 2:
                items = sentences[1:]  # Skip intro sentence
        
        return items[:5]  # Max 5 items
    
    def extract_intro_text(self, text):
        """Extract introductory text before list items"""
        first_item_match = re.search(r'(^\d+[.)]|^\*|^\-|First|Here are)', text, re.MULTILINE | re.IGNORECASE)
        if first_item_match:
            intro = text[:first_item_match.start()].strip()
            if intro:
                return intro
        
        # Fallback: first sentence
        sentences = self.split_sentences(text)
        if sentences:
            return sentences[0]
        
        return ""
    
    def clean_list_item(self, item):
        """Clean up list item text"""
        # Remove any residual numbering or bullets
        item = re.sub(r'^\d+[.)]\s*', '', item)
        item = re.sub(r'^[*\-]\s*', '', item)
        return item.strip()
    
    def is_key_insight(self, sentence):
        """Detect if sentence contains key insight worthy of emphasis"""
        insight_indicators = [
            'the key is', 'the secret', 'here\'s why', 'the truth is',
            'what i learned', 'the lesson', 'remember this', 'most important'
        ]
        sentence_lower = sentence.lower()
        return any(indicator in sentence_lower for indicator in insight_indicators)
    
    def get_random_question(self):
        """Get random engagement question"""
        import random
        return random.choice(self.engagement_questions)

def main():
    formatter = SubstackFormatter()
    
    if len(sys.argv) < 2:
        print("Usage: python3 formatter.py 'your text here' [structure] [length]")
        print("Structures: auto, punchy-wisdom, micro-story, list, contrarian, relatable, poetic")  
        print("Lengths: short, optimal, long")
        return
    
    text = sys.argv[1]
    structure = sys.argv[2] if len(sys.argv) > 2 else "auto"
    length = sys.argv[3] if len(sys.argv) > 3 else "optimal"
    
    formatted = formatter.format_text(text, structure, length)
    print(formatted)

if __name__ == "__main__":
    main()