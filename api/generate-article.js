const { execSync } = require('child_process');

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { topic, userId } = req.body;

    if (!topic || !userId) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Verify user is authenticated (in production, verify Firebase token)
    // For now, we'll trust the userId from the request

    // Add topic to config/topics.txt temporarily
    const fs = require('fs');
    const topicsPath = './config/topics.txt';
    const currentTopics = fs.readFileSync(topicsPath, 'utf-8');
    fs.writeFileSync(topicsPath, topic);

    // Run the pipeline
    console.log(`Generating article for topic: ${topic}`);
    execSync('python3 -m venv .venv && .venv/bin/python -m src.main', {
      cwd: process.cwd(),
      stdio: 'inherit'
    });

    // Restore original topics
    fs.writeFileSync(topicsPath, currentTopics);

    res.status(200).json({ 
      success: true, 
      message: `Article for "${topic}" generated successfully` 
    });
  } catch (error) {
    console.error('Error generating article:', error);
    res.status(500).json({ 
      error: 'Failed to generate article', 
      details: error.message 
    });
  }
}
