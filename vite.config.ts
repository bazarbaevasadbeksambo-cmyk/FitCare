import { defineConfig, loadEnv, type Plugin, type ViteDevServer } from 'vite';
import react from '@vitejs/plugin-react';
import basicSsl from '@vitejs/plugin-basic-ssl';

// HTTPS=1 npm run dev → self-signed HTTPS so the camera works on a phone in the same Wi‑Fi.
const https = process.env.HTTPS === '1';

// Runs api/coach.ts inside the Vite dev server, so `npm run dev` works without the Vercel CLI.
function devApi(): Plugin {
  return {
    name: 'fitcare-dev-api',
    configureServer(server: ViteDevServer) {
      server.middlewares.use('/api/coach', async (req, res) => {
        let raw = '';
        for await (const chunk of req) raw += chunk;
        const mod = await server.ssrLoadModule('/api/coach.ts');
        const shimReq = Object.assign(req, { body: raw ? safeJson(raw) : undefined });
        const shimRes = Object.assign(res, {
          status(code: number) {
            res.statusCode = code;
            return shimRes;
          },
          json(data: unknown) {
            res.setHeader('Content-Type', 'application/json');
            res.end(JSON.stringify(data));
            return shimRes;
          },
        });
        try {
          await mod.default(shimReq, shimRes);
        } catch (e) {
          console.error(e);
          res.statusCode = 500;
          res.end('{"error":"dev api crashed"}');
        }
      });
    },
  };
}

function safeJson(s: string) {
  try {
    return JSON.parse(s);
  } catch {
    return s;
  }
}

export default defineConfig(({ mode }) => {
  // Expose .env (incl. ANTHROPIC_API_KEY) to the dev API only — never via import.meta.env (no VITE_ prefix).
  Object.assign(process.env, loadEnv(mode, process.cwd(), ''));
  return {
    plugins: [react(), devApi(), ...(https ? [basicSsl()] : [])],
    test: { environment: 'node', include: ['src/**/*.test.ts', 'api/**/*.test.ts'] },
  };
});
