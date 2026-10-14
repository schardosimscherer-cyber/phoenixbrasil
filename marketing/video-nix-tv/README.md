# Vídeo da Nix com a cena "Como visto na TV" (A Tarde é Sua, com Sônia Abrão)

`phoenix-nix-sonia-abrao.mp4`: vertical 1080×1920, 46s, efeitos sonoros normalizados em -14 LUFS.

É o mesmo vídeo institucional da Nix com uma cena de autoridade (4,6s–10s) logo depois do gancho. `tv.png` é um quadro do comercial da Phoenix Brasil no programa.

```bash
export NODE_PATH=$(npm root -g)
node cues.js && python3 sfx.py cues.json sfx_raw.wav
ffmpeg -i sfx_raw.wav -af loudnorm=I=-14:TP=-1:LRA=11 -ar 48000 sfx.wav
node render.js video silent.mp4 30
ffmpeg -i silent.mp4 -i sfx.wav -c:v copy -c:a aac -b:a 192k -shortest saida.mp4
```
