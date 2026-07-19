const http = require('http');
const https = require('https');

const PORT = 9642;
const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://localhost:11434';

// Parse URL
function fetchUrl(urlString) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlString);
    const client = url.protocol === 'https:' ? https : http;
    
    client.get(urlString, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve(null);
        }
      });
    }).on('error', reject);
  });
}

// Generate Prometheus metrics
async function generateMetrics() {
  let metrics = '';
  
  // Type hints
  metrics += '# HELP ollama_models_loaded Number of models currently loaded\n';
  metrics += '# TYPE ollama_models_loaded gauge\n';
  metrics += '# HELP ollama_model_size_bytes Size of loaded model in bytes\n';
  metrics += '# TYPE ollama_model_size_bytes gauge\n';
  metrics += '# HELP ollama_model_vram_bytes VRAM used by loaded model\n';
  metrics += '# TYPE ollama_model_vram_bytes gauge\n';
  metrics += '# HELP ollama_up Ollama service health (1=up, 0=down)\n';
  metrics += '# TYPE ollama_up gauge\n';
  
  try {
    // Check Ollama health
    const healthUrl = `${OLLAMA_HOST}/api/tags`;
    const tagsData = await fetchUrl(healthUrl);
    
    if (!tagsData) {
      metrics += 'ollama_up 0\n';
      return metrics;
    }
    
    metrics += 'ollama_up 1\n';
    
    // Count models
    const models = tagsData.models || [];
    metrics += `ollama_models_loaded ${models.length}\n`;
    
    // Model details
    for (const model of models) {
      const safeModel = model.name.replace(/[^a-zA-Z0-9_]/g, '_');
      
      if (model.size) {
        metrics += `ollama_model_size_bytes{model="${model.name}"} ${model.size}\n`;
      }
      
      // Try to get model details from ps endpoint
      try {
        const psData = await fetchUrl(`${OLLAMA_HOST}/api/ps`);
        if (psData && psData.models) {
          for (const runningModel of psData.models) {
            if (runningModel.name === model.name) {
              const vram = runningModel.size_vram || 0;
              metrics += `ollama_model_vram_bytes{model="${model.name}"} ${vram}\n`;
            }
          }
        }
      } catch (e) {
        // ps endpoint may not be available in all versions
      }
    }
    
    // Memory stats if available
    try {
      const psData = await fetchUrl(`${OLLAMA_HOST}/api/ps`);
      if (psData && psData.models && psData.models.length > 0) {
        const totalVram = psData.models.reduce((sum, m) => sum + (m.size_vram || 0), 0);
        metrics += `# HELP ollama_total_vram_bytes Total VRAM used by all models\n`;
        metrics += `# TYPE ollama_total_vram_bytes gauge\n`;
        metrics += `ollama_total_vram_bytes ${totalVram}\n`;
      }
    } catch (e) {
      // Ignore if ps endpoint unavailable
    }
    
  } catch (error) {
    console.error('Error collecting Ollama metrics:', error.message);
    metrics += 'ollama_up 0\n';
  }
  
  return metrics;
}

// HTTP server
const server = http.createServer(async (req, res) => {
  if (req.url === '/metrics') {
    try {
      const metrics = await generateMetrics();
      res.writeHead(200, { 'Content-Type': 'text/plain; version=0.0.4' });
      res.end(metrics);
    } catch (error) {
      console.error('Error generating metrics:', error);
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Error generating metrics\n');
    }
  } else if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('OK\n');
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found\n');
  }
});

server.listen(PORT, () => {
  console.log(`Ollama exporter listening on port ${PORT}`);
  console.log(`Ollama host: ${OLLAMA_HOST}`);
});
