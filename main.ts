import { copyFileSync, mkdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = fileURLToPath(new URL('./entry.png', import.meta.url));
const destination = join(process.env.MAKEFUN_OUTPUT_DIR || '/output', 'entry.png');
mkdirSync(dirname(destination), { recursive: true });
// The output directory may already contain the source image itself.
if (resolve(source) !== resolve(destination)) {
  copyFileSync(source, destination);
}
