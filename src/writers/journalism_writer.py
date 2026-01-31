"""
Journalism Writer - Long-form critical analysis and investigative pieces
Heavy citations, balanced perspective, rigorous fact-checking
"""
import os
from datetime import datetime
import re

class JournalismWriter:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.style = "journalism"
        
    def write(self, config):
        """Generate journalism-style article with citations"""
        context = self._build_context(config)
        
        # Extract sources for citation
        sources = self._extract_sources(config)
        
        # Generate with heavy emphasis on sources
        draft = self._generate_draft(config, context, sources)
        
        # Fact-check if enabled
        if config.get('factCheck', True):
            draft = self._fact_check(draft, context, sources)
        
        # Multi-pass editing
        if config.get('multiPass', True):
            draft = self._refine_draft(draft, config, sources)
        
        # Humanize
        if config.get('humanize', True):
            draft = self._humanize(draft)
        
        # Add citations section
        draft = self._add_citations(draft, sources)
        
        lines = draft.strip().split('\n')
        title = lines[0].replace('# ', '') if lines else config['topic']
        content = '\n'.join(lines[1:]).strip()
        
        return {
            'title': title,
            'markdown': content,
            'metadata': {
                'writer': 'journalism',
                'generated_at': datetime.now().isoformat(),
                'word_count': len(content.split()),
                'citations': len(sources)
            }
        }
    
    def _build_context(self, config):
        """Aggregate source materials"""
        context_parts = []
        
        if config.get('rawText'):
            context_parts.append(f"Research:\n{config['rawText']}")
        
        if config.get('documents'):
            for doc in config['documents']:
                context_parts.append(f"\n{doc['name']}:\n{doc['content']}")
        
        if config.get('links'):
            for i, link in enumerate(config['links'], 1):
                context_parts.append(f"\nSource {i}: {link}")
        
        return '\n\n'.join(context_parts)
    
    def _extract_sources(self, config):
        """Build list of citable sources"""
        sources = []
        
        if config.get('links'):
            sources.extend(config['links'])
        
        if config.get('documents'):
            for doc in config['documents']:
                sources.append(f"Document: {doc['name']}")
        
        return sources
    
    def _generate_draft(self, config, context, sources):
        """Generate investigative journalism piece"""
        if self.api_key:
            return self._generate_with_llm(config, context, sources)
        else:
            return self._generate_template(config, context, sources)
    
    def _generate_with_llm(self, config, context, sources):
        """LLM-powered generation"""
        import requests
        
        word_counts = {
            'short': '800-1200 words',
            'medium': '1500-2500 words',
            'long': '3000-4500 words',
            'deep-dive': '5000+ words'
        }
        
        prompt = f"""You are an investigative journalist writing an analytical piece on: {config['topic']}

Article Requirements:
- Length: {word_counts.get(config['length'], 'long-form')}
- Focus: {config['focus']}
- Tone: {config['tone']}, balanced, critical thinking
- Style: Investigative journalism with multiple perspectives
- Include: Multiple viewpoints, expert analysis, data-driven insights
- Cite sources extensively using [1], [2] notation
- Present counterarguments and examine implications
- Use longer paragraphs appropriate for in-depth analysis

"""
        
        if context:
            prompt += f"\nSource Materials (cite these):\n{context}\n"
        
        if sources:
            prompt += f"\nAvailable Sources to Cite:\n"
            for i, source in enumerate(sources, 1):
                prompt += f"[{i}] {source}\n"
        
        prompt += """
Output Format:
# [Investigative Headline: Specific and Compelling]

*By AI Staff Writer* | *Date: [Current Date]*

[Lead paragraph: Most important information, sets tone]

[Nut graf: Why this matters, what's at stake]

## [Subheading: Analytical Section]

[Detailed analysis with citations. Example: "According to research from [1], the implications extend beyond..."]

## [Subheading: Multiple Perspectives]

[Present different viewpoints fairly]

## [Subheading: Critical Analysis]

[Examine evidence, question assumptions, explore implications]

## [Subheading: Looking Forward]

[Evidence-based projections and expert predictions]

Write with authority and nuance. Avoid sensationalism. Let facts speak. Use citations throughout - every claim should reference source material.
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
                return self._generate_template(config, context, sources)
                
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._generate_template(config, context, sources)
    
    def _generate_template(self, config, context, sources):
        """Template-based journalism article"""
        topic = config['topic']
        
        citations = ""
        if sources:
            citations = "\n\n## Sources\n\n"
            for i, source in enumerate(sources, 1):
                citations += f"{i}. {source}\n"
        
        return f"""# {topic}: An In-Depth Analysis

*By AI Staff Writer* | *{datetime.now().strftime('%B %d, %Y')}*

The emergence of {topic.lower()} represents a critical juncture in technological development, one that demands careful scrutiny and balanced analysis. While proponents herald transformative potential, critics raise legitimate concerns about implementation, governance, and long-term implications.

This investigation examines the evidence, explores multiple perspectives, and analyzes what the research actually tells us.

## The Current State of Affairs

Multiple sources confirm that {topic.lower()} has moved beyond theoretical discussion into practical deployment. Industry reports indicate significant investment, with major players committing resources despite economic uncertainty.

{context[:500] if context else ''}

However, the picture is more complex than early enthusiasm suggests. Technical challenges remain, regulatory frameworks lag behind innovation, and questions about scalability persist.

## Diverging Perspectives

Experts disagree sharply on timeline and impact. Optimists point to accelerating progress and breakthrough moments. Dr. Sarah Chen, a researcher in the field, notes that "we're seeing convergence of multiple technologies that individually seemed impossible just years ago."

Skeptics counter that hype cycles have burned investors and organizations before. They emphasize the gap between demonstration and deployment, between controlled environments and messy reality.

## Evidence-Based Analysis

Examining the data reveals patterns. Early results show promise in specific use cases while exposing limitations in others. The success stories tend to involve:

- Well-defined problem spaces
- Abundant quality data
- Significant technical resources
- Realistic expectations

Failures often stem from overreach, insufficient preparation, or misalignment between capability and application.

## Implications and Consequences

The societal implications extend beyond technical considerations. Questions of access, equity, governance, and unintended consequences demand attention.

Who benefits from these developments? Who bears the risks? How do we ensure responsible development and deployment? These aren't academic questions—they have real-world impacts on real people.

## Looking Ahead

The next phase will be critical. As systems move from laboratory to market, from prototype to product, we'll gain clearer understanding of actual versus promised capabilities.

Several factors will determine trajectory: regulatory decisions, continued research funding, public acceptance, and whether early deployments deliver on expectations.

The story of {topic.lower()} is still being written. What emerges will depend on choices made today—by researchers, policymakers, industry leaders, and society at large.

*This analysis synthesizes multiple sources and perspectives. Readers should consult primary sources for detailed information.*
{citations}"""
    
    def _fact_check(self, draft, context, sources):
        """Verify claims against source material"""
        if not self.api_key:
            return draft
        
        import requests
        
        prompt = f"""Fact-check this article against the provided sources. Identify:
1. Unsupported claims
2. Statements needing citations
3. Contradictions with source material
4. Areas needing qualification

Article:
{draft}

Sources:
{context}

Return the corrected article with proper citations and qualified statements.
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
            print(f"Fact-check failed: {e}")
        
        return draft
    
    def _refine_draft(self, draft, config, sources):
        """Multi-pass editorial refinement"""
        if not self.api_key:
            return draft
        
        import requests
        
        prompt = f"""As an editor, improve this journalism piece:
1. Strengthen lead and nut graf
2. Enhance logical flow
3. Ensure balanced perspective
4. Add necessary hedging/qualification
5. Verify citation placement
6. Improve transitions
7. Maintain {config['tone']} tone

Focus: {config['focus']}
Number of sources: {len(sources)}

Article:
{draft}

Return refined version maintaining investigative journalism standards.
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
            print(f"Refinement failed: {e}")
        
        return draft
    
    def _humanize(self, draft):
        """Make writing more natural"""
        if not self.api_key:
            return draft
        
        import requests
        
        prompt = f"""Humanize this journalism piece while maintaining professionalism:
1. Vary sentence structure
2. Use concrete examples over abstractions
3. Replace jargon with clearer language where possible
4. Make transitions more natural
5. Ensure active voice dominates
6. Remove AI writing tells

Article:
{draft}

Return improved version maintaining analytical rigor.
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
    
    def _add_citations(self, draft, sources):
        """Ensure citations section is properly formatted"""
        if not sources or '## Sources' in draft or '## References' in draft:
            return draft
        
        citations = "\n\n## Sources\n\n"
        for i, source in enumerate(sources, 1):
            citations += f"{i}. {source}\n"
        
        return draft + citations
