# Substack Formatter Examples

## Example 1: Micro-Story Format

### Input:
```
I used to think being productive meant doing more things. Last week I tried something different. I did fewer things but focused completely on each one. The result was surprising. I got more done in less time and felt less stressed. Sometimes the answer isn't addition, it's subtraction.
```

### Output (HTML for Substack):
```html
<p><strong>I used to think being productive meant doing more things.</strong></p>

<p>Last week I tried something different.</p>

<p>I did fewer things but focused completely on each one.</p>

<p><strong>The result was surprising.</strong></p>

<p><em>I got more done in less time and felt less stressed. Sometimes the answer isn't addition, it's subtraction.</em></p>

<p><em>What's one thing you could subtract from your routine?</em></p>
```

## Example 2: List Format

### Input:
```
Here are the three things that changed my writing. First, I stopped trying to sound smart and started trying to be clear. Second, I wrote for one specific person instead of everyone. Third, I cut every sentence that didn't move the story forward.
```

### Output (HTML for Substack):
```html
<p><strong>Here are the three things that changed my writing.</strong></p>

<ul>
<li><strong>I stopped trying to sound smart and started trying to be clear</strong></li>
<li><strong>I wrote for one specific person instead of everyone</strong></li>
<li><strong>I cut every sentence that didn't move the story forward</strong></li>
</ul>

<p><em>What's worked for you?</em></p>
```

## Example 3: Contrarian Take

### Input:
```
Everyone says you need to post every day to grow on social media. But I posted 3 times per week and grew faster than when I posted daily. Quality beats quantity when you're competing for attention. Most people scroll past filler content but stop for something valuable.
```

### Output (HTML for Substack):
```html
<p><strong>Everyone says you need to post every day to grow on social media.</strong></p>

<p>But I posted 3 times per week and grew faster than when I posted daily. Quality beats quantity when you're competing for attention.</p>

<p><em>Most people scroll past filler content but stop for something valuable.</em></p>

<p>What's your take?</p>
```

## Example 4: Punchy Wisdom

### Input:
```
Your first draft is not your last draft. It's your first attempt at organizing your thoughts. The magic happens in revision when you discover what you're actually trying to say.
```

### Output (HTML for Substack):
```html
<p><strong>Your first draft is not your last draft.</strong></p>

<p>It's your first attempt at organizing your thoughts. The magic happens in revision when you discover what you're actually trying to say.</p>
```

## Usage Commands

### Basic Formatting
```bash
python3 formatter.py "Your content here"
```

### With Specific Structure
```bash
python3 formatter.py "Your content here" micro-story
python3 formatter.py "Your content here" contrarian  
python3 formatter.py "Your content here" list
```

### Copy to Substack (Properly Formatted)
```bash
# Format and copy in one step
python3 formatter.py "Your content here" | python3 copy_to_substack.py

# Or format first, then copy
python3 formatter.py "Your content here" > output.html
python3 copy_to_substack.py "$(cat output.html)"
```

## Integration with Clawdbot

```
Format this for Substack as a micro-story:
[your content]
```

```
Format this for Substack:
[your content]
```

The skill will automatically:
1. Apply viral formatting patterns
2. Convert to proper HTML
3. Provide copy instructions for Substack editor
4. Ensure bold/italic/headers work when pasted

## Key Benefits

- ✅ **Research-backed patterns** from 80+ viral Substack posts
- ✅ **Proper HTML formatting** that Substack editor recognizes  
- ✅ **Optimal length targeting** (50-120 words for best engagement)
- ✅ **Copy-paste ready** with formatting preserved
- ✅ **Multiple structure types** for different content styles