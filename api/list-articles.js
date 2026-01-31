export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const token = process.env.GITHUB_TOKEN;
    const headers = token ? { Authorization: `Bearer ${token}` } : {};

    // Get list of files in public/posts
    const response = await fetch(
      'https://api.github.com/repos/ApparatusGroup/blog/contents/public/posts',
      { headers }
    );

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status}`);
    }

    const files = await response.json();
    
    // Filter for markdown files
    const mdFiles = files.filter(f => f.name.endsWith('.md'));
    
    // Fetch content of each markdown file to get frontmatter
    const articles = await Promise.all(
      mdFiles.slice(0, 50).map(async (file) => {
        try {
          const contentRes = await fetch(file.download_url);
          const content = await contentRes.text();
          
          // Parse frontmatter
          const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
          if (frontmatterMatch) {
            const frontmatter = frontmatterMatch[1];
            const titleMatch = frontmatter.match(/title:\s*["']?(.+?)["']?\s*$/m);
            const dateMatch = frontmatter.match(/date:\s*(\d{4}-\d{2}-\d{2})/);
            const timestampMatch = frontmatter.match(/timestamp:\s*(.+)$/m);
            
            return {
              title: titleMatch ? titleMatch[1].replace(/^"|"$/g, '') : file.name.replace('.md', ''),
              date: dateMatch ? dateMatch[1] : '',
              timestamp: timestampMatch ? timestampMatch[1] : '',
              slug: file.name.replace('.md', '')
            };
          }
          
          return null;
        } catch (err) {
          console.error('Error loading article:', file.name, err.message);
          return null;
        }
      })
    );

    // Filter out nulls and sort by timestamp (newest first)
    const validArticles = articles
      .filter(a => a !== null)
      .sort((a, b) => {
        const timeA = a.timestamp || a.date || '';
        const timeB = b.timestamp || b.date || '';
        return timeB.localeCompare(timeA);
      });

    return res.status(200).json({
      success: true,
      articles: validArticles,
      count: validArticles.length
    });

  } catch (error) {
    console.error('List articles error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Failed to list articles'
    });
  }
}
