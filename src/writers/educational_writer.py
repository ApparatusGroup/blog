"""
Educational Writer - Simplifies complex topics, generates infographics
Myth-busting, clear explanations, visual learning aids
"""
import os
from datetime import datetime
import json

class EducationalWriter:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.style = "educational"
        
    def write(self, config):
        """Generate educational content with infographics"""
        context = self._build_context(config)
        
        # Generate main educational content
        draft = self._generate_draft(config, context)
        
        # Generate infographic data
        infographic_data = self._generate_infographic(config, context)
        
        # Multi-pass for clarity
        if config.get('multiPass', True):
            draft = self._refine_for_clarity(draft, config)
        
        # Humanize
        if config.get('humanize', True):
            draft = self._humanize(draft)
        
        # Embed infographic data
        draft = self._embed_infographic(draft, infographic_data)
        
        lines = draft.strip().split('\n')
        title = lines[0].replace('# ', '') if lines else config['topic']
        content = '\n'.join(lines[1:]).strip()
        
        return {
            'title': title,
            'markdown': content,
            'metadata': {
                'writer': 'educational',
                'generated_at': datetime.now().isoformat(),
                'word_count': len(content.split()),
                'infographics': len(infographic_data)
            }
        }
    
    def _build_context(self, config):
        """Aggregate source materials"""
        context_parts = []
        
        if config.get('rawText'):
            context_parts.append(config['rawText'])
        
        if config.get('documents'):
            for doc in config['documents']:
                context_parts.append(doc['content'])
        
        if config.get('links'):
            context_parts.append(f"References: {', '.join(config['links'])}")
        
        return '\n\n'.join(context_parts)
    
    def _generate_draft(self, config, context):
        """Generate educational content"""
        if self.api_key:
            return self._generate_with_llm(config, context)
        else:
            return self._generate_template(config, context)
    
    def _generate_with_llm(self, config, context):
        """LLM-powered educational content"""
        import requests
        
        word_counts = {
            'short': '600-1000 words',
            'medium': '1200-1800 words',
            'long': '2000-2800 words',
            'deep-dive': '3000+ words'
        }
        
        prompt = f"""You are an educational content creator specializing in making complex topics accessible. Create an educational piece on: {config['topic']}

Content Requirements:
- Length: {word_counts.get(config['length'], 'medium length')}
- Audience: General readers, no assumed expertise
- Tone: {config['tone']}, clear, encouraging
- Focus: {config['focus']}
- Goals:
  * Explain fundamentals clearly
  * Bust common myths and misconceptions
  * Use analogies and examples
  * Break down complex concepts step-by-step
  * Include practical takeaways
  * Encourage further learning

"""
        
        if context:
            prompt += f"\nSource Materials:\n{context}\n"
        
        prompt += """
Output Format:
# [Clear, Engaging Title - What You'll Learn]

[Friendly opening that acknowledges complexity but promises clarity]

## The Basics: What Is It Really?

[Simple explanation with analogies]

## Common Misconceptions

**Myth 1:** [Common misconception]
**Reality:** [Clear correction]

**Myth 2:** [Another misconception]
**Reality:** [Truth explained simply]

## How It Actually Works

[Step-by-step breakdown with examples]

## Why It Matters

[Real-world applications and impact explained clearly]

## Key Takeaways

- [Clear point 1]
- [Clear point 2]
- [Clear point 3]

## Learn More

[Encouraging note about further resources]

---

*INFOGRAPHIC_PROMPT*
Suggest 2-3 visual infographics that would help explain this topic:
1. [Description of helpful diagram/chart]
2. [Description of another visual aid]
3. [Description of comparison or process visualization]

Use simple language throughout. Explain jargon when necessary. Make complex ideas accessible without dumbing down. Write like you're explaining to a curious friend.
"""
        
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'anthropic/claude-3.5-sonnet',
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=180
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return self._generate_template(config, context)
                
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._generate_template(config, context)
    
    def _generate_template(self, config, context):
        """Template-based educational content"""
        topic = config['topic']
        
        return f"""# Understanding {topic}: A Clear Guide

If {topic.lower()} seems confusing, you're not alone. This guide breaks down the complexity into clear, understandable concepts.

## The Basics: What Is It Really?

Think of {topic.lower()} as [simple analogy]. Just like [familiar comparison], it works by [basic explanation].

In simple terms: {topic.lower()} is a way to [core function explained plainly]. No advanced degree required to understand why it matters.

## Common Misconceptions

**Myth 1: {topic} is too complex for regular people to understand**
**Reality:** The fundamentals are actually straightforward. The confusion comes from jargon and hype.

**Myth 2: {topic} will replace human expertise entirely**
**Reality:** It's a tool that augments human capabilities, not a replacement. Think of it like a calculator - powerful, but you still need to understand math.

**Myth 3: {topic} is either perfect or useless**
**Reality:** Like any technology, it has strengths and limitations. Understanding both helps you use it effectively.

## How It Actually Works

Let's break this down step-by-step:

**Step 1:** [First component explained]
**Step 2:** [Second component explained]
**Step 3:** [How they connect]

Here's a real example: {context[:300] if context else 'Imagine applying this to everyday situations like organizing information or making predictions based on patterns.'}

## Why It Matters

{topic} has practical applications that affect daily life:

- **In Healthcare:** [Example application]
- **In Education:** [Example application]
- **In Business:** [Example application]
- **In Your Life:** [Personal relevance]

Understanding the basics helps you make informed decisions about when and how to use these tools.

## Key Takeaways

- {topic} isn't magic - it's technology with specific capabilities and limitations
- Understanding fundamentals empowers you to use it effectively
- Many common fears or expectations are based on misconceptions
- The real power comes from combining human judgment with technical capability

## Keep Learning

This is just the beginning. As you encounter {topic.lower()} in real situations, you'll develop deeper intuition. Start by observing how it works, asking questions, and experimenting with simple applications.

The best way to learn? Hands-on experience with realistic expectations.

---

*Visual Learning Aids Below*
"""
    
    def _generate_infographic(self, config, context):
        """Generate infographic descriptions/data"""
        if not self.api_key:
            return self._default_infographics(config)
        
        import requests
        
        prompt = f"""Create 2-3 infographic concepts for educational content about: {config['topic']}

For each infographic, provide:
1. Title
2. Type (comparison, process flow, myth vs reality, key statistics, etc.)
3. Data/content to visualize
4. Description of visual layout

Format as JSON array:
[
  {{
    "title": "...",
    "type": "...",
    "content": ["point 1", "point 2", ...],
    "layout": "..."
  }}
]

Focus on concepts that simplify understanding and clarify misconceptions.
"""
        
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'anthropic/claude-3.5-sonnet',
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()['choices'][0]['message']['content']
                # Extract JSON from response
                import re
                json_match = re.search(r'\[.*\]', result, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                    
        except Exception as e:
            print(f"Infographic generation failed: {e}")
        
        return self._default_infographics(config)
    
    def _default_infographics(self, config):
        """Fallback infographic concepts"""
        topic = config['topic']
        return [
            {
                "title": f"How {topic} Works: Simple Breakdown",
                "type": "process flow",
                "content": [
                    "Input: Data or question goes in",
                    "Processing: System analyzes patterns",
                    "Output: Result or answer comes out"
                ],
                "layout": "Left-to-right flow diagram with icons"
            },
            {
                "title": f"{topic}: Myth vs Reality",
                "type": "comparison",
                "content": [
                    "MYTH: It's too complicated | REALITY: Core concepts are simple",
                    "MYTH: It's perfect | REALITY: Has specific strengths and limits",
                    "MYTH: Replaces humans | REALITY: Augments human capabilities"
                ],
                "layout": "Two-column comparison with checkmarks/X marks"
            },
            {
                "title": f"Key Facts About {topic}",
                "type": "statistics",
                "content": [
                    "Primary use cases",
                    "Current limitations",
                    "Future potential",
                    "How to get started"
                ],
                "layout": "Icon-based grid with brief explanations"
            }
        ]
    
    def _embed_infographic(self, draft, infographic_data):
        """Embed infographic descriptions in markdown"""
        if not infographic_data:
            return draft
        
        infographic_section = "\n\n---\n\n## Visual Guide\n\n"
        
        for i, graphic in enumerate(infographic_data, 1):
            infographic_section += f"### {graphic['title']}\n\n"
            infographic_section += f"*{graphic['type'].title()}*\n\n"
            
            if graphic.get('content'):
                for item in graphic['content']:
                    infographic_section += f"- {item}\n"
            
            infographic_section += f"\n*Visualization: {graphic.get('layout', 'Visual representation')}*\n\n"
        
        infographic_section += "\n---\n"
        
        # Insert before "Learn More" section or at end
        if "## Learn More" in draft or "## Keep Learning" in draft:
            return draft.replace("## Learn More", infographic_section + "## Learn More").replace("## Keep Learning", infographic_section + "## Keep Learning")
        else:
            return draft + infographic_section
    
    def _refine_for_clarity(self, draft, config):
        """Refine for maximum clarity"""
        if not self.api_key:
            return draft
        
        import requests
        
        prompt = f"""Review this educational content for clarity:
1. Simplify any remaining jargon
2. Improve analogies and examples
3. Ensure logical progression
4. Check that myths are clearly debunked
5. Verify takeaways are actionable
6. Make sure tone is {config['tone']} and encouraging

Article:
{draft}

Return improved version optimized for understanding.
"""
        
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'anthropic/claude-3.5-sonnet',
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"Clarity refinement failed: {e}")
        
        return draft
    
    def _humanize(self, draft):
        """Make educational content more conversational"""
        if not self.api_key:
            return draft
        
        import requests
        
        prompt = f"""Make this educational content sound more human and engaging:
1. Use more conversational language
2. Add occasional questions to engage reader
3. Include relatable examples
4. Vary sentence structure
5. Make it feel like a helpful explanation from a friend

Article:
{draft}

Return humanized version maintaining clarity and educational value.
"""
        
        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'anthropic/claude-3.5-sonnet',
                    'messages': [{'role': 'user', 'content': prompt}]
                },
                timeout=90
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"Humanization failed: {e}")
        
        return draft
