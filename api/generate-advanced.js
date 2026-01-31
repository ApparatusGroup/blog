export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  handleGeneration(req, res);
}

async function handleGeneration(req, res) {
  try {
    const config = req.body || {};
    const topic = (config.topic || '').trim();

    if (!topic) {
      return res.status(400).json({ success: false, error: 'Topic is required' });
    }

    // Generate content
    const content = await generateContent(topic, config);
    
    // Create slug
    const slug = topic.toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '')
      .substring(0, 50);

    // Try to save to GitHub if token exists
    let saved = false;
    if (process.env.GITHUB_TOKEN) {
      try {
        await commitToGitHub(slug, content, topic);
        saved = true;
      } catch (err) {
        console.error('GitHub save failed:', err.message);
      }
    }

    return res.status(200).json({
      success: true,
      title: topic,
      slug: slug,
      saved: saved,
      message: saved ? 'Article published!' : 'Article generated (GitHub save disabled)'
    });

  } catch (error) {
    console.error('Handler error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Generation failed'
    });
  }
}

async function generateContent(topic, config) {
  const apiKey = process.env.OPENROUTER_API_KEY;
  
  if (!apiKey) {
    return createTemplate(topic);
  }

  const writers = {
    tech: 'Fast-paced tech news. Latest AI and innovation. Engaging, active voice, short paragraphs.',
    journalism: 'Long-form investigative analysis. Cite sources. Balanced, thorough, critical perspective.',
    educational: 'Simplifies complex topics. Clear explanations, analogies, myth-busting.'
  };

  const style = writers[config.writer] || writers.tech;
  const tone = config.tone || 'professional';
  const length = config.length || 'medium';

  const wordCounts = { short: 600, medium: 1200, long: 2000, comprehensive: 3000 };
  const targetWords = wordCounts[length] || 1200;

  const prompt = `Write a ${targetWords}-word article about "${topic}".

Style: ${style}
Tone: ${tone}

Requirements:
- Use natural, human language (avoid AI clichés)
- Vary sentence structure and paragraph length
- Include specific details and examples
- Format with Markdown headings
- Do NOT use phrases like "In conclusion", "It's important to note", "In today's world"`;

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
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 4000,
      temperature: 0.7
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const data = await response.json();
  const content = data.choices?.[0]?.message?.content;

  if (!content) {
    throw new Error('No content from API');
  }

  return content;
}

function createTemplate(topic) {
  return `# ${topic}

## Introduction

This article explores ${topic}, examining recent developments and key implications in the field.

## Key Points

${topic} encompasses several important dimensions:

- **Current landscape**: Rapidly evolving with new innovations
- **Impact**: Significant implications for stakeholders
- **Future direction**: Expected growth and transformation

## Analysis

${topic} represents an area of ongoing development. Key considerations include the opportunities it presents alongside the challenges that need addressing.

## Conclusion

As ${topic} continues to develop, staying informed about trends and developments in this space remains valuable for anyone interested in the field.`;
}

async function commitToGitHub(slug, content, topic) {
  const token = process.env.GITHUB_TOKEN;
  const now = new Date();
  const date = now.toISOString().split('T')[0];
  const timestamp = now.toISOString();
  
  const frontmatter = `---
title: ${topic}
date: ${date}
timestamp: ${timestamp}
---

`;

  const fullContent = frontmatter + content;
  const path = `public/posts/${slug}.md`;
  
  // Get existing file SHA if it exists
  let sha = null;
  try {
    const getRes = await fetch(
      `https://api.github.com/repos/ApparatusGroup/blog/contents/${path}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    if (getRes.ok) {
      sha = (await getRes.json()).sha;
    }
  } catch (e) {
    // File doesn't exist yet
  }

  // Upload file
  const body = {
    message: `Add article: ${topic}`,
    content: Buffer.from(fullContent).toString('base64'),
    ...(sha ? { sha } : {})
  };

  const response = await fetch(
    `https://api.github.com/repos/ApparatusGroup/blog/contents/${path}`,
    {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    }
  );

  if (!response.ok) {
    throw new Error(`GitHub error: ${response.status}`);
  }
}
