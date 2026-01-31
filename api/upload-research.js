export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Construct full URL for fetch (required in serverless environment)
    const host = req.headers.host || 'blog-mu-opal-43.vercel.app';
    const protocol = host.includes('localhost') ? 'http' : 'https';
    const target = ${protocol}://System.Management.Automation.Internal.Host.InternalHost/api/upload-research-python;
    
    const response = await fetch(target, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body || {})
    });

    const text = await response.text();
    res.status(response.status).send(text);
  } catch (error) {
    console.error('Error proxying upload-research:', error);
    res.status(500).json({
      error: 'Failed to reach Python publish endpoint',
      details: error.message
    });
  }
}
