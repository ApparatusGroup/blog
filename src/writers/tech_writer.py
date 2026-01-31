"""
Tech News Writer - Latest AI and emerging technology coverage
Fast-paced, engaging, highlights innovation and breakthroughs
"""
import os
from datetime import datetime

class TechWriter:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.style = "tech_news"
        
    def write(self, config):
        """
        Generate tech news article based on configuration
        
        Args:
            config: dict with topic, length, tone, focus, sources, etc.
        
        Returns:
            dict with title and markdown content
        """
        # Build context from sources
        context = self._build_context(config)
        
        # Generate initial draft
        draft = self._generate_draft(config, context)
        
        # Multi-pass editing if enabled
        if config.get('multiPass', True):
            draft = self._refine_draft(draft, config)
            
        # Humanize if enabled
        if config.get('humanize', True):
            draft = self._humanize(draft)
            
        # Extract title and content
        lines = draft.strip().split('\n')
        title = lines[0].replace('# ', '') if lines else config['topic']
        content = '\n'.join(lines[1:]).strip()
        
        return {
            'title': title,
            'markdown': content,
            'metadata': {
                'writer': 'tech',
                'generated_at': datetime.now().isoformat(),
                'word_count': len(content.split())
            }
        }
    
    def _build_context(self, config):
        """Aggregate all source materials"""
        context_parts = []
        
        # Raw text
        if config.get('rawText'):
            context_parts.append(f"Research Notes:\n{config['rawText']}")
        
        # Documents
        if config.get('documents'):
            for doc in config['documents']:
                context_parts.append(f"\n{doc['name']}:\n{doc['content']}")
        
        # Links (placeholder - would fetch in production)
        if config.get('links'):
            context_parts.append(f"\nReference Links: {', '.join(config['links'])}")
        
        return '\n\n'.join(context_parts)
    
    def _generate_draft(self, config, context):
        """Generate initial article draft"""
        if self.api_key:
            return self._generate_with_llm(config, context)
        else:
            return self._generate_template(config, context)
    
    def _generate_with_llm(self, config, context):
        """Use LLM for generation"""
        import requests
        
        # Word count mapping
        word_counts = {
            'short': '500-800 words',
            'medium': '1000-1500 words',
            'long': '2000-3000 words',
            'deep-dive': '3500+ words'
        }
        
        # Build comprehensive prompt
        prompt = f"""You are a tech news writer covering AI and emerging technology. Write a {config['tone']} article about: {config['topic']}

Article Requirements:
- Length: {word_counts.get(config['length'], 'medium length')}
- Focus: {config['focus']}
- Tone: {config['tone']}
- Style: Fast-paced, engaging tech journalism
- Highlight innovation, breakthroughs, and implications
- Use short paragraphs for readability
- Include relevant statistics or data points
- Write compelling headlines and subheadings

"""
        
        if context:
            prompt += f"\nSource Materials:\n{context}\n\nSynthesize the above sources into your article.\n"
        
        prompt += """
Output Format:
# [Compelling Headline]

[Opening paragraph with hook]

## [Subheading 1]

[Content with specific details, data, quotes]

## [Subheading 2]

[Continue with clear structure]

Write naturally - avoid AI clichés like "delve", "landscape", "realm", "tapestry". Use active voice and concrete examples.
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
            else:
                print(f"LLM error: {response.status_code}")
                return self._generate_template(config, context)
                
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._generate_template(config, context)
    
    def _generate_template(self, config, context):
        """Fallback template-based generation"""
        topic = config['topic']
        
        return f"""# {topic}: The Next Frontier in Technology

The technology landscape is experiencing a seismic shift with {topic.lower()}, marking one of the most significant developments in recent years. Industry leaders and researchers are racing to unlock its full potential.

## Breaking New Ground

Recent breakthroughs have accelerated progress beyond initial projections. Engineers and scientists are discovering applications that seemed impossible just months ago, fundamentally changing how we approach problem-solving in this domain.

## Market Impact and Industry Response

Major tech companies have invested heavily in this space, with billions of dollars flowing into research and development. Startups are emerging with innovative approaches, while established players are pivoting their strategies to stay competitive.

{context if context else ''}

## Technical Innovation

The underlying technology represents a paradigm shift. New architectures and methodologies are enabling capabilities that previous systems couldn't achieve, with performance improvements measured in orders of magnitude.

## Real-World Applications

From healthcare to finance, {topic.lower()} is demonstrating practical value across industries. Early adopters are reporting significant efficiency gains and new capabilities that were previously out of reach.

## Looking Ahead

As the technology matures, experts predict even more dramatic developments. The next 12-18 months will be critical as systems move from experimental to production-ready implementations.

The race is on, and the implications extend far beyond the tech sector. What we're witnessing is the early stages of a transformation that will reshape how we work, create, and solve complex challenges.
"""
    
    def _refine_draft(self, draft, config):
        """Multi-pass refinement"""
        if not self.api_key:
            return draft
        
        import requests
        
        refinement_prompt = f"""Review and improve this tech article. Ensure it:
1. Has a compelling, specific headline (not generic)
2. Opens with a strong hook
3. Includes concrete details and specifics
4. Uses varied sentence structure
5. Avoids AI writing patterns (generic transitions, overused words)
6. Maintains {config['tone']} tone throughout
7. Has logical flow between sections

Original Article:
{draft}

Return the improved version with the same markdown structure.
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
                    'messages': [{'role': 'user', 'content': refinement_prompt}]
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"Refinement failed: {e}")
        
        return draft
    
    def _humanize(self, draft):
        """Remove AI detection patterns"""
        if not self.api_key:
            return draft
        
        import requests
        
        humanize_prompt = f"""Make this article sound more human and less AI-generated:

1. Replace generic words: "delve", "landscape", "realm", "tapestry", "testament", "underscore"
2. Vary sentence openings (avoid repetitive starts)
3. Add occasional contractions where natural
4. Use more specific, concrete language
5. Include rhetorical questions sparingly
6. Make transitions more natural and conversational

Article:
{draft}

Return the humanized version maintaining all structure and key information.
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
                    'messages': [{'role': 'user', 'content': humanize_prompt}]
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"Humanization failed: {e}")
        
        return draft
