const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cookieParser = require('cookie-parser');
const crypto = require('crypto');
const config = require('./config.json');

// Service to run (dome or archive)
const SERVICE = process.env.SERVICE || 'dome';
const serviceConfig = config[SERVICE];

if (!serviceConfig) {
  console.error(`Invalid SERVICE: ${SERVICE}. Must be 'dome' or 'archive'`);
  process.exit(1);
}

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser(config.cookieSecret));

// Validate access code
function validateCode(code) {
  const normalized = code.trim().toUpperCase();
  return config.accessCodes.map(c => c.toUpperCase()).includes(normalized);
}

// Generate session token
function generateToken() {
  return crypto.randomBytes(32).toString('hex');
}

// Check if request has valid auth
function isAuthenticated(req) {
  // Check both signed (set by proxy) and unsigned (set by homepage) cookies
  return req.signedCookies.terrarium_auth === 'valid' ||
         req.cookies.terrarium_auth === 'valid';
}

// Login page HTML (matches your modal styling exactly)
const loginPageHTML = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${serviceConfig.title}</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: 'JetBrains Mono', 'Courier New', monospace;
      background: #000000;
      color: #ffffff;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }

    .overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.92);
      backdrop-filter: blur(8px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
      animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    .modal {
      position: relative;
      background: linear-gradient(135deg, #0a1929 0%, #000814 100%);
      border: 1px solid rgba(0, 255, 242, 0.3);
      max-width: 450px;
      width: 90%;
      padding: 2rem;
      animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow:
        0 0 60px rgba(0, 255, 242, 0.15),
        inset 0 0 40px rgba(0, 255, 242, 0.03);
    }

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    /* Corner Brackets */
    .corner {
      position: absolute;
      width: 20px;
      height: 20px;
      border: 2px solid #EBFA1D;
    }

    .corner-tl {
      top: -1px;
      left: -1px;
      border-right: none;
      border-bottom: none;
    }

    .corner-tr {
      top: -1px;
      right: -1px;
      border-left: none;
      border-bottom: none;
    }

    .corner-bl {
      bottom: -1px;
      left: -1px;
      border-right: none;
      border-top: none;
    }

    .corner-br {
      bottom: -1px;
      right: -1px;
      border-left: none;
      border-top: none;
    }

    .content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1rem;
    }

    .title {
      font-size: clamp(1rem, 3vw, 1.25rem);
      font-weight: 300;
      letter-spacing: 0.25em;
      color: #00FFF2;
      text-align: center;
      margin: 0;
      text-transform: uppercase;
    }

    .glitch-line {
      width: 60%;
      height: 1px;
      background: linear-gradient(
        90deg,
        transparent 0%,
        #00FFF2 20%,
        #EBFA1D 50%,
        #00FFF2 80%,
        transparent 100%
      );
      opacity: 0.6;
      animation: pulse 2s ease-in-out infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 0.3; }
      50% { opacity: 0.8; }
    }

    form {
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .input-wrapper {
      position: relative;
      width: 100%;
    }

    input {
      width: 100%;
      background: rgba(0, 0, 0, 0.5);
      border: 1px solid rgba(0, 255, 242, 0.3);
      color: #FFFFFF;
      font-family: 'JetBrains Mono', 'Courier New', monospace;
      font-size: 0.875rem;
      letter-spacing: 0.2em;
      padding: 0.875rem 1.25rem;
      text-align: center;
      outline: none;
      transition: all 0.3s ease;
      text-transform: uppercase;
    }

    input:focus {
      border-color: #00FFF2;
      box-shadow:
        0 0 20px rgba(0, 255, 242, 0.3),
        inset 0 0 20px rgba(0, 255, 242, 0.1);
    }

    input::placeholder {
      color: rgba(255, 255, 255, 0.3);
      letter-spacing: 0.15em;
    }

    input:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .input-border {
      position: absolute;
      top: -4px;
      left: -4px;
      right: -4px;
      bottom: -4px;
      border: 1px solid transparent;
      pointer-events: none;
      transition: border-color 0.3s ease;
    }

    input:focus + .input-border {
      border-color: rgba(235, 250, 29, 0.5);
    }

    .error {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      color: #FF3366;
      font-size: 0.875rem;
      letter-spacing: 0.1em;
      animation: shake 0.4s ease;
    }

    @keyframes shake {
      0%, 100% { transform: translateX(0); }
      25% { transform: translateX(-10px); }
      75% { transform: translateX(10px); }
    }

    .error-icon {
      font-size: 1.25rem;
      animation: blink 1s ease infinite;
    }

    @keyframes blink {
      0%, 50%, 100% { opacity: 1; }
      25%, 75% { opacity: 0.3; }
    }

    .submit-btn {
      position: relative;
      background: linear-gradient(135deg, rgba(75, 80, 45, 0.8) 0%, rgba(50, 60, 30, 0.9) 100%);
      border: 1px solid rgba(235, 250, 29, 0.4);
      color: #EBFA1D;
      font-family: 'JetBrains Mono', 'Courier New', monospace;
      font-size: 0.8125rem;
      font-weight: 400;
      letter-spacing: 0.15em;
      padding: 0.875rem 1.5rem;
      cursor: pointer;
      transition: all 0.3s ease;
      overflow: hidden;
      text-transform: uppercase;
    }

    .submit-btn:hover:not(:disabled) {
      background: linear-gradient(135deg, rgba(75, 80, 45, 1) 0%, rgba(50, 60, 30, 1) 100%);
      border-color: #EBFA1D;
      box-shadow:
        0 0 30px rgba(235, 250, 29, 0.3),
        inset 0 0 20px rgba(235, 250, 29, 0.1);
      transform: translateY(-2px);
    }

    .submit-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .btn-corner {
      position: absolute;
      width: 12px;
      height: 12px;
      border: 1px solid #EBFA1D;
      opacity: 0.6;
      transition: all 0.3s ease;
    }

    .btn-corner-tl {
      top: -1px;
      left: -1px;
      border-right: none;
      border-bottom: none;
    }

    .btn-corner-tr {
      top: -1px;
      right: -1px;
      border-left: none;
      border-bottom: none;
    }

    .btn-corner-bl {
      bottom: -1px;
      left: -1px;
      border-right: none;
      border-top: none;
    }

    .btn-corner-br {
      bottom: -1px;
      right: -1px;
      border-left: none;
      border-top: none;
    }

    .submit-btn:hover:not(:disabled) .btn-corner {
      opacity: 1;
      width: 16px;
      height: 16px;
    }

    .hint {
      font-size: 0.625rem;
      letter-spacing: 0.1em;
      color: rgba(255, 255, 255, 0.3);
      text-align: center;
      margin: 0;
      text-transform: uppercase;
    }

    .hidden {
      display: none;
    }

    @media (max-width: 768px) {
      .modal {
        padding: 1.5rem;
      }
      .title {
        font-size: 1rem;
      }
      input {
        font-size: 0.8125rem;
        padding: 0.75rem 1rem;
      }
      .submit-btn {
        padding: 0.75rem 1.25rem;
        font-size: 0.75rem;
      }
    }
  </style>
</head>
<body>
  <div class="overlay">
    <div class="modal">
      <!-- Corner Brackets -->
      <div class="corner corner-tl"></div>
      <div class="corner corner-tr"></div>
      <div class="corner corner-bl"></div>
      <div class="corner corner-br"></div>

      <!-- Content -->
      <div class="content">
        <h2 class="title">${serviceConfig.title}</h2>
        <div class="glitch-line"></div>

        <form id="authForm">
          <div class="input-wrapper">
            <input
              type="text"
              id="accessCode"
              placeholder="ENTER ACCESS CODE"
              maxlength="20"
              autocomplete="off"
              autofocus
            />
            <div class="input-border"></div>
          </div>

          <div id="errorMessage" class="error hidden">
            <span class="error-icon">⚠</span>
            <span id="errorText">INVALID ACCESS CODE</span>
          </div>

          <button type="submit" class="submit-btn" id="submitBtn">
            <span id="btnText">GRANT ACCESS</span>
            <div class="btn-corner btn-corner-tl"></div>
            <div class="btn-corner btn-corner-tr"></div>
            <div class="btn-corner btn-corner-bl"></div>
            <div class="btn-corner btn-corner-br"></div>
          </button>
        </form>

        <p class="hint">ENTER CLEARANCE CODE TO PROCEED</p>
      </div>
    </div>
  </div>

  <script>
    const form = document.getElementById('authForm');
    const input = document.getElementById('accessCode');
    const errorDiv = document.getElementById('errorMessage');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');

    // Auto-uppercase input
    input.addEventListener('input', (e) => {
      e.target.value = e.target.value.toUpperCase();
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();

      const code = input.value.trim();
      if (!code) return;

      // Show validating state
      submitBtn.disabled = true;
      btnText.textContent = 'VALIDATING...';
      errorDiv.classList.add('hidden');

      // Simulate delay for effect
      await new Promise(resolve => setTimeout(resolve, 600));

      try {
        const response = await fetch('/auth/validate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (data.success) {
          btnText.textContent = 'ACCESS GRANTED';
          await new Promise(resolve => setTimeout(resolve, 500));
          window.location.reload();
        } else {
          errorDiv.classList.remove('hidden');
          input.value = '';
          submitBtn.disabled = false;
          btnText.textContent = 'GRANT ACCESS';
          input.focus();
        }
      } catch (error) {
        errorDiv.classList.remove('hidden');
        document.getElementById('errorText').textContent = 'CONNECTION ERROR';
        submitBtn.disabled = false;
        btnText.textContent = 'GRANT ACCESS';
      }
    });
  </script>
</body>
</html>
`;

// Auth validation endpoint
app.post('/auth/validate', (req, res) => {
  const { code } = req.body;

  if (validateCode(code)) {
    // Set cookie with domain to share across all subdomains
    const domain = req.hostname.includes('mutatedterrarium.com')
      ? '.mutatedterrarium.com'
      : undefined;

    res.cookie('terrarium_auth', 'valid', {
      domain: domain,
      path: '/',
      httpOnly: true,
      maxAge: config.cookieMaxAge,
      sameSite: 'lax'
    });
    res.json({ success: true });
  } else {
    res.json({ success: false });
  }
});

// Logout endpoint (optional)
app.get('/auth/logout', (req, res) => {
  const domain = req.hostname.includes('mutatedterrarium.com')
    ? '.mutatedterrarium.com'
    : undefined;

  res.clearCookie('terrarium_auth', { domain: domain, path: '/' });
  res.redirect('/');
});

// Main handler
app.use((req, res, next) => {
  // Skip auth check for auth endpoints
  if (req.path.startsWith('/auth/')) {
    return next();
  }

  // Check authentication
  if (!isAuthenticated(req)) {
    return res.send(loginPageHTML);
  }

  // Authenticated - proxy to service
  const proxyOptions = {
    target: serviceConfig.targetUrl,
    changeOrigin: true,
    ws: true,
    onError: (err, req, res) => {
      console.error('Proxy error:', err);
      res.status(502).send('Service temporarily unavailable');
    }
  };

  // For Jarvis, rewrite all paths to /jarvis route (except Next.js assets)
  if (SERVICE === 'jarvis') {
    proxyOptions.pathRewrite = (path) => {
      // Don't rewrite Next.js assets, API routes, or other system paths
      if (path.startsWith('/_next/') ||
          path.startsWith('/api/') ||
          path.startsWith('/assets/') ||
          path.startsWith('/favicon')) {
        return path;  // Keep as-is
      }
      // Rewrite root to /jarvis
      if (path === '/') {
        return '/jarvis';
      }
      // Rewrite everything else to /jarvis/*
      return `/jarvis${path}`;
    };
    proxyOptions.onProxyReq = (proxyReq, req) => {
      console.log(`[Jarvis Proxy] ${req.method} ${req.path} → ${proxyReq.path}`);
    };
  }

  createProxyMiddleware(proxyOptions)(req, res, next);
});

const PORT = serviceConfig.port;
app.listen(PORT, () => {
  console.log(`✓ ${serviceConfig.serviceName} auth proxy running on port ${PORT}`);
  console.log(`  → Target: ${serviceConfig.targetUrl}`);
  console.log(`  → Access codes configured: ${config.accessCodes.length}`);
});
