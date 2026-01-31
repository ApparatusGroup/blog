/**
 * Advanced Article Generation API
 * Handles multi-source, multi-writer article generation with quality controls
 */

const { spawn } = require('child_process');
const path = require('path');
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

  const {
    topic,
    writer = 'tech',
    length = 'medium',
    tone = 'professional',
    focus = 'overview',
    links = [],
    documents = [],
    rawText = '',
    multiPass = true,
    factCheck = true,
    humanize = true,
    userId
  } = req.body;

  if (!topic) {
    return res.status(400).json({ error: 'Topic is required' });
  }

  console.log(`Advanced generation: ${writer} writer for "${topic}"`);

  // Create temporary config file
  const configPath = path.join('/tmp', `writer-config-${Date.now()}.json`);
  const config = {
    topic,
    writer,
    length,
    tone,
    focus,
    links,
    documents,
    rawText,
    multiPass,
    factCheck,
    humanize,
    userId
  };

  try {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

    // Run advanced writer (use platform-appropriate python binary)
    const isWindows = process.platform === 'win32';
    const pythonBin = process.env.PYTHON_BINARY || (isWindows ? 'python' : 'python3');
    const pythonProcess = spawn(pythonBin, [
      path.join(process.cwd(), 'src', 'advanced_writer.py'),
      configPath
    ], {
      env: {
        ...process.env,
        PYTHONPATH: process.cwd()
      }
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
      console.log(data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error(data.toString());
    });

    pythonProcess.on('close', (code) => {
      // Cleanup
      try {
        fs.unlinkSync(configPath);
      } catch (e) {
        console.error('Failed to cleanup config file:', e);
      }

      if (code === 0) {
        // Parse output for article title
        const lines = output.split('\n');
        const successLine = lines.find(line => line.includes('Published:'));
        const title = successLine 
          ? successLine.replace('Published:', '').trim()
          : topic;

        res.status(200).json({
          success: true,
          title,
          message: 'Article generated and published successfully'
        });
      } else {
        console.error('Python process failed:', errorOutput);
        res.status(500).json({
          success: false,
          error: errorOutput || 'Generation failed'
        });
      }
    });

  } catch (error) {
    console.error('Advanced generation error:', error);
    
    // Cleanup on error
    try {
      if (fs.existsSync(configPath)) {
        fs.unlinkSync(configPath);
      }
    } catch (e) {
      // Ignore cleanup errors
    }

    res.status(500).json({
      success: false,
      error: error.message
    });
  }
};
