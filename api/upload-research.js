const { execSync, spawnSync } = require('child_process');
const path = require('path');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { title, content, userId } = req.body;

    if (!title || !content || !userId) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Create a temporary file with the research content
    const fs = require('fs');
    const date = new Date().toISOString().split('T')[0];
    
    const articleContent = `---
title: ${title}
date: ${date}
---

${content}
`;

    // Write directly using Python publisher
    const pythonScript = `
import sys
sys.path.insert(0, '.')
from src.publisher import Publisher

publisher = Publisher()
content = """${articleContent.replace(/"/g, '\\"')}"""
publisher.publish({'title': '${title.replace(/'/g, "\\'")}', 'markdown': """${content.replace(/"/g, '\\"')}"""})
print("Published successfully")
`;

    fs.writeFileSync('/tmp/publish_script.py', pythonScript);
    
    const candidates = [process.env.PYTHON_BINARY, 'python3', 'python'].filter(Boolean);
    let pythonBin = null;
    for (const candidate of candidates) {
      const check = spawnSync(candidate, ['-V']);
      if (!check.error) {
        pythonBin = candidate;
        break;
      }
    }

    if (!pythonBin) {
      return res.status(500).json({
        error: 'Python runtime not available. Set PYTHON_BINARY or deploy with a Python runtime.'
      });
    }

    execSync(`${pythonBin} /tmp/publish_script.py`, {
      cwd: process.cwd(),
      stdio: 'inherit'
    });

    fs.unlinkSync('/tmp/publish_script.py');

    res.status(200).json({ 
      success: true, 
      message: `Article "${title}" published successfully` 
    });
  } catch (error) {
    console.error('Error uploading research:', error);
    res.status(500).json({ 
      error: 'Failed to publish article', 
      details: error.message 
    });
  }
}
