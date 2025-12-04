import express from 'express';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);
const app = express();
const PORT = 3001;

// Enable CORS for local development
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// Check if a tmux session exists
async function checkTmuxSession(sessionName) {
  try {
    await execAsync(`tmux has-session -t ${sessionName} 2>/dev/null`);
    return true;
  } catch {
    return false;
  }
}

// Check if a process is running
async function checkProcess(processName) {
  try {
    const { stdout } = await execAsync(`pgrep -f "${processName}"`);
    return stdout.trim().length > 0;
  } catch {
    return false;
  }
}

// Status endpoint
app.get('/api/status', async (req, res) => {
  try {
    const statuses = await Promise.all([
      // Services
      checkTmuxSession('terrarium-dome').then(active => ({
        name: 'Dome',
        active,
        type: 'service'
      })),
      checkTmuxSession('terrarium-engine').then(active => ({
        name: 'Engine',
        active,
        type: 'service'
      })),
      checkTmuxSession('terrarium-portal').then(active => ({
        name: 'Portal',
        active,
        type: 'service'
      })),
      checkTmuxSession('terrarium-bridge').then(active => ({
        name: 'Bridge',
        active,
        type: 'service'
      })),
      checkTmuxSession('terrarium-archive').then(active => ({
        name: 'Archive',
        active,
        type: 'service'
      })),

      // Bots (check if scheduler is running)
      checkProcess('scheduler.py').then(active => ({
        name: 'Cassia',
        active,
        type: 'bot'
      })),
      checkProcess('scheduler.py').then(active => ({
        name: 'Sage',
        active,
        type: 'bot'
      })),
      checkProcess('scheduler.py').then(active => ({
        name: 'Freya',
        active,
        type: 'bot'
      })),
      checkProcess('scheduler.py').then(active => ({
        name: 'Nigella',
        active,
        type: 'bot'
      })),
      checkProcess('scheduler.py').then(active => ({
        name: 'Nyx',
        active,
        type: 'bot'
      })),
      checkProcess('scheduler.py').then(active => ({
        name: 'Anya',
        active,
        type: 'bot'
      })),
      checkTmuxSession('terrarium-portal').then(active => ({
        name: 'Casper',
        active,
        type: 'bot'
      })),
      checkProcess('scheduler.py').then(active => ({
        name: 'Pepper',
        active,
        type: 'bot'
      })),
      checkProcess('scheduler.py').then(active => ({
        name: 'Luci',
        active,
        type: 'bot'
      })),
    ]);

    res.json(statuses);
  } catch (error) {
    console.error('Error checking status:', error);
    res.status(500).json({ error: 'Failed to check system status' });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.listen(PORT, () => {
  console.log(`🌿 Terrarium Status Monitor running on port ${PORT}`);
});
