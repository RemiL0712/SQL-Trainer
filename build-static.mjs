import { mkdir, copyFile } from 'node:fs/promises';

await mkdir('public', { recursive: true });
for (const name of ['index.html', 'app.js', 'style.css', 'favicon.svg']) {
  await copyFile(name, `public/${name}`);
}
