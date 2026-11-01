import fs from 'node:fs/promises';
import { ArcadeRenderer } from '../.arcade/dist/pacman-contribution-graph.min.js';

// Use the renderer directly: no upstream Action telemetry or score reporting.
await fs.mkdir('dist', { recursive: true });
await new Promise((resolve, reject) => {
  let output = '';
  const timeout = setTimeout(() => reject(new Error('Pac-Man generation timed out')), 600000);
  const renderer = new ArcadeRenderer({
    game: 'pacman',
    platform: 'github',
    username: 'gustavo-brandao',
    gameTheme: 'github-dark',
    playerStyle: 'opportunistic',
    showMonthLabels: true,
    githubSettings: { accessToken: process.env.GITHUB_TOKEN },
    svgCallback: svg => { output = svg; },
    gameOverCallback: async () => {
      clearTimeout(timeout);
      try {
        if (!output.includes('<svg')) throw new Error('Pac-Man returned no SVG');
        await fs.writeFile('dist/pacman-contribution-graph-dark.svg', output);
        resolve();
      } catch (error) { reject(error); }
    },
    pointsIncreasedCallback: () => {},
  });
  renderer.start().catch(error => { clearTimeout(timeout); reject(error); });
});
