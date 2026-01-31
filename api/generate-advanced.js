/**
 * Advanced Article Generation API
 * Handles multi-source, multi-writer article generation with quality controls
 */

const fs = require('fs');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const contentLength = Number(req.headers['content-length'] || 0);
  const maxBytes = 3 * 1024 * 1024; // 3MB safety limit for serverless payloads
  if (contentLength > maxBytes) {
    return res.status(413).json({
      error: 'Payload too large. Reduce total document size or number of sources and try again.'
    });
  }

  const config = req.body || {};

  try {
    const target = process.env.ADVANCED_PY_ENDPOINT || '/api/generate-advanced-python';
    const response = await fetch(target, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    const text = await response.text();
    res.status(response.status).send(text);
  } catch (error) {
    console.error('Advanced generation proxy error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to reach Python generation endpoint',
      details: error.message
    });
  }
};
