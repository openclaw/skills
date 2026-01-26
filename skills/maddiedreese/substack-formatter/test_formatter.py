#!/usr/bin/env python3
"""
Test the Substack formatter with example content
"""

from formatter import SubstackFormatter

def test_all_formats():
    formatter = SubstackFormatter()
    
    test_cases = [
        {
            "name": "Micro-Story",
            "structure": "micro-story", 
            "content": "I used to think being productive meant doing more things. Last week I tried something different. I did fewer things but focused completely on each one. The result was surprising. I got more done in less time and felt less stressed. Sometimes the answer isn't addition, it's subtraction."
        },
        {
            "name": "List Format",
            "structure": "list",
            "content": "Here are the three things that changed my writing. First, I stopped trying to sound smart and started trying to be clear. Second, I wrote for one specific person instead of everyone. Third, I cut every sentence that didn't move the story forward."
        },
        {
            "name": "Contrarian Take", 
            "structure": "contrarian",
            "content": "Everyone says you need to post every day to grow on social media. But I posted 3 times per week and grew faster than when I posted daily. Quality beats quantity when you're competing for attention. Most people scroll past filler content but stop for something valuable."
        },
        {
            "name": "Punchy Wisdom",
            "structure": "punchy-wisdom",
            "content": "Your first draft is not your last draft. It's your first attempt at organizing your thoughts. The magic happens in revision when you discover what you're actually trying to say."
        },
        {
            "name": "Auto-Detect",
            "structure": "auto", 
            "content": "The biggest mistake creators make is trying to be perfect. Perfect content takes forever and nobody cares about perfect. They care about valuable and authentic. Ship fast, get feedback, improve iteratively."
        }
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST: {test['name']} Format")
        print(f"{'='*60}")
        print(f"\nORIGINAL ({test['structure']}):")
        print(f'"{test["content"]}"')
        print(f"\nFORMATTED HTML:")
        print("-" * 40)
        
        formatted = formatter.format_text(
            test["content"], 
            test["structure"]
        )
        print(formatted)
        
        # Word count analysis
        original_words = len(test["content"].split())
        print(f"\n📊 ANALYSIS:")
        print(f"• Original word count: {original_words}")
        print(f"• Target range: 50-120 words (optimal)")
        print(f"• Status: {'✅ OPTIMAL' if 50 <= original_words <= 120 else '⚠️  Outside optimal range'}")

def test_word_count_optimization():
    """Test how formatter handles different content lengths"""
    formatter = SubstackFormatter()
    
    # Short content (under 50 words)
    short = "The best advice is often the simplest. Do less, but do it better. Focus wins."
    
    # Optimal content (50-120 words) 
    optimal = "I spent years trying to optimize my morning routine. Wake up at 5am, meditate, journal, exercise, cold shower, healthy breakfast. It was exhausting. Last month I simplified it to just two things: make my bed and drink a full glass of water. My days improved immediately. Sometimes the answer isn't adding more habits, it's removing the ones that don't serve you."
    
    # Long content (over 120 words)
    long = "The productivity industry wants you to believe that the right system will solve all your problems. Buy this app, follow this method, implement these seventeen daily habits and you'll finally get your life together. I bought into it completely. I tried GTD, bullet journaling, time blocking, the pomodoro technique, habit stacking, morning routines, evening routines, and dozens of apps that promised to change everything. After years of optimization, I realized the truth: productivity systems don't create motivation, they organize it. If you're not motivated to begin with, no system will save you. But if you have clear goals and genuine enthusiasm, almost any simple system will work. The magic isn't in the method, it's in the clarity of purpose behind it."
    
    test_contents = [
        ("Short (under 50 words)", short),
        ("Optimal (50-120 words)", optimal), 
        ("Long (over 120 words)", long)
    ]
    
    print(f"\n{'='*60}")
    print("WORD COUNT OPTIMIZATION TESTS")
    print(f"{'='*60}")
    
    for name, content in test_contents:
        word_count = len(content.split())
        formatted = formatter.format_text(content, "auto")
        
        print(f"\n{name}: {word_count} words")
        print("-" * 40)
        print(formatted)
        print(f"\nStatus: {'✅ Optimal length' if 50 <= word_count <= 120 else '⚠️ Consider editing for optimal engagement'}")

if __name__ == "__main__":
    print("🧪 TESTING SUBSTACK FORMATTER")
    print("Based on patterns from 80+ viral Substack posts")
    
    test_all_formats()
    test_word_count_optimization()
    
    print(f"\n{'='*60}")
    print("✅ ALL TESTS COMPLETE")
    print("💡 To copy formatted content to clipboard for Substack:")
    print("   python3 copy_to_substack.py 'your_html_output_here'")
    print(f"{'='*60}")