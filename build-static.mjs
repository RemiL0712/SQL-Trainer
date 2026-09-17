import { mkdir, copyFile } from 'node:fs/promises';

await mkdir('public', { recursive: true });
for (const name of ['index.html', 'app.js', 'lesson-guide.js', 'style.css', 'lesson-guide.css', 'favicon.svg']) {
  await copyFile(name, `public/${name}`);
}
