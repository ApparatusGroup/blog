/**
 * Advanced Article Generation API
 * Self-contained Node.js implementation using OpenRouter API
 */

export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const config = req.body || {};
  const topic = (config.topic || '').trim();

  if (!topic) {
    return res.status(400).json({ success: false, error: 'Topic is required' });
  }

  const apiKey = process.env.OPENROUTER_API_KEY;
  
  // Writer configurations
  const writers = {
    tech: {
      name: 'Tech News Writer',
      style: 'Fast-paced tech journalism. Engaging, highlights innovation. Use active voice, short paragraphs.',
      wordTarget: getWordTarget(config.length)
    },
    journalism: {
      name: 'Investigative Journalist', 
      style: 'Long-form critical analysis. Cite sources inline, balanced perspective, thorough research.',
      wordTarget: getWordTarget(config.length)
    },
    educational: {
      name: 'Educational Writer',
      style: 'Simplifies complex topics. Clear explanations, use analogies, myth-busting approach.',
      wordTarget: getWordTarget(config.length)
    }
  };

  const writer = writers[config.writer] || writers.tech;
  const tone = config.tone || 'professional';
  const focus = config.focus || 'overview';

  // Build source context from uploaded materials
  let sourceContext = '';
  if (config.sources) {
    const { documents = [], links = [], rawText = '' } = config.sources;
    
    if (documents.length > 0) {
      sourceContext += '\n\n## Uploaded Documents:\n';
      documents.forEach((doc, i) => {
        sourceContext += `\n### Document ${i + 1}: ${doc.name}\n${doc.content}\n`;
      });
    }
    
    if (links.length > 0) {
      sourceContext += '\n\n## Reference Links:\n';
      links.forEach(link => {
        sourceContext += `- ${link}\n`;
      });
    }
    
    if (rawText.trim()) {
      sourceContext += `\n\n## Additional Notes:\n${rawText}\n`;
    }
  }

  const systemPrompt = `You are the ${writer.name}. Writing style: ${writer.style}

Guidelines:
- Tone: ${tone}
- Focus: ${focus}
- Target length: ${writer.wordTarget} words
- Write in a human, natural voice - avoid AI-sounding phrases
- Do NOT use phrases like "In conclusion", "It's important to note", "In today's world"
- Vary sentence structure and paragraph length
- Use specific examples and concrete details
- Format in clean Markdown with proper headings`;

  const userPrompt = `Write an article about: ${topic}
${sourceContext ? `\nUse these source materials for research and context:${sourceContext}` : ''}

Create a well-researched, engaging article that sounds authentically human.`;

  try {
    let content;
    
    if (apiKey) {
      // Use OpenRouter API
      const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'https://blog-mu-opal-43.vercel.app',
          'X-Title': 'Blog Generator'
        },
        body: JSON.stringify({
          model: 'anthropic/claude-3.5-sonnet',
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
          ],
          max_tokens: 4000,
          temperature: 0.7
        })
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`OpenRouter API error: ${response.status} - ${errorData}`);
      }

      const data = await response.json();
      content = data.choices?.[0]?.message?.content;
      
      if (!content) {
        throw new Error('No content returned from API');
      }
    } else {
      // Fallback template when no API key
      content = generateTemplate(topic, writer, config);
    }

    // Generate slug and frontmatter
    const slug = topic.toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
      .substring(0, 50);
    
    const date = new Date().toISOString().split('T')[0];
    const safeTitle = topic.includes(':') ? `"${topic}"` : topic;
    
    const fullContent = `---
title: ${safeTitle}
date: ${date}
author: ${writer.name}
tags: [${config.writer || 'tech'}, ${focus}]
---

${content}`;

    // For now, just return success - actual file writing would need a different approach
    return res.status(200).json({
      success: true,
      title: topic,
      slug: slug,
      content: fullContent,
      message: 'Article generated successfully. Note: File saving requires additional setup.'
    });

  } catch (error) {
    console.error('Generation error:', error);
    return res.status(500).json({
      success: false,
      error: 'Failed to generate article',
      details: error.message
    });
  }
}

function getWordTarget(length) {
  const targets = {
    short: '500-800',
    medium: '1000-1500',
    long: '2000-2500',
    comprehensive: '3000+'
  };
  return targets[length] || targets.medium;
}

function generateTemplate(topic, writer, config) {
  return `# ${topic}

*Generated by ${writer.name}*

## Introduction

This article explores the topic of ${topic}, providing insights and analysis based on the latest developments in the field.

## Key Points

The subject of ${topic} encompasses several important aspects that deserve attention:

1. **Current State**: The landscape continues to evolve rapidly with new innovations emerging regularly.

2. **Implications**: These developments have significant implications for various stakeholders.

3. **Future Outlook**: Experts anticipate continued growth and evolution in this space.

## Analysis

When examining ${topic}, it's essential to consider both the opportunities and challenges it presents. The technology and ideas driving this field are constantly advancing, creating new possibilities while also raising important questions.

## Conclusion

${topic} represents a fascinating area of development that will likely continue to shape our world in meaningful ways. Staying informed about these trends is valuable for anyone interested in technology and innovation.

---

*Note: This is a template article. For AI-generated content with full research capabilities, please configure your OpenRouter API key in your Vercel environment variables.*`;
}
