# Vídeo: Crédito CLT (Phoenix Brasil)

`phoenix-credito-clt.mp4`: vídeo vertical 1080×1920, 32s, 30fps, para Reels/TikTok.

O vídeo é gerado a partir de `index.html` (animação controlada pela função `render(t)`) e `render.js` (Playwright + ffmpeg).

```bash
NODE_PATH=$(npm root -g) node render.js preview 2.6 12.5 31   # quadros de teste
NODE_PATH=$(npm root -g) node render.js video saida.mp4 30   # vídeo completo
```

Para criar variações, edite os textos em `index.html` e renderize de novo.
