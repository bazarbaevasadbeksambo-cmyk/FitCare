// Copies the MediaPipe wasm runtime from node_modules into public/ so it's served locally (no CDN).
// Only the files FilesetResolver actually loads: SIMD build + non-SIMD fallback for older browsers.
import { copyFileSync, existsSync, mkdirSync } from 'node:fs';

const src = 'node_modules/@mediapipe/tasks-vision/wasm';
const dst = 'public/mediapipe/wasm';
const files = ['vision_wasm_internal.js', 'vision_wasm_internal.wasm', 'vision_wasm_nosimd_internal.js', 'vision_wasm_nosimd_internal.wasm'];

if (existsSync(src)) {
  mkdirSync(dst, { recursive: true });
  for (const f of files) copyFileSync(`${src}/${f}`, `${dst}/${f}`);
}
