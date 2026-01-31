export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { slug } = req.body || {};
    if (!slug) {
      return res.status(400).json({ success: false, error: 'Slug is required' });
    }

    const token = process.env.GITHUB_TOKEN;
    if (!token) {
      return res.status(400).json({ success: false, error: 'GitHub token not configured' });
    }

    // Delete markdown file
    try {
      await deleteFile(token, `public/posts/${slug}.md`);
    } catch (err) {
      console.error('Error deleting markdown:', err.message);
    }

    // Delete HTML file
    try {
      await deleteFile(token, `public/posts/${slug}.html`);
    } catch (err) {
      console.error('Error deleting HTML:', err.message);
    }

    // Trigger redeployment
    const deployHook = process.env.VERCEL_DEPLOY_HOOK;
    if (deployHook) {
      try {
        await fetch(deployHook, { method: 'POST' });
      } catch (e) {
        console.error('Deploy hook failed:', e.message);
      }
    }

    return res.status(200).json({
      success: true,
      message: `Article "${slug}" deleted successfully`
    });

  } catch (error) {
    console.error('Delete error:', error);
    return res.status(500).json({
      success: false,
      error: error.message || 'Delete failed'
    });
  }
}

async function deleteFile(token, path) {
  // Get file SHA first
  const getRes = await fetch(
    `https://api.github.com/repos/ApparatusGroup/blog/contents/${path}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );

  if (!getRes.ok) {
    throw new Error(`File not found: ${path}`);
  }

  const fileData = await getRes.json();

  // Delete file
  const deleteRes = await fetch(
    `https://api.github.com/repos/ApparatusGroup/blog/contents/${path}`,
    {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: `Delete article: ${path}`,
        sha: fileData.sha
      })
    }
  );

  if (!deleteRes.ok) {
    throw new Error(`GitHub delete failed: ${deleteRes.status}`);
  }
}
