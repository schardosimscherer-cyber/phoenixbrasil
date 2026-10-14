# Vídeo institucional: Nix, a IA da Phoenix Brasil

`phoenix-nix-institucional.mp4`: vertical 1080×1920, 41s, 30fps, com efeitos sonoros sincronizados.

Cenas: gancho → mapa do Brasil (+5.000 clientes) → +20 bancos parceiros → chat da Nix simulando bancos às 03:12 → 24h por dia → CTA phoenixbrasil.com/clt.

A conversa e os valores do chat são fictícios ("Simulação ilustrativa").

## Como gerar de novo

```bash
export NODE_PATH=$(npm root -g)
node render.js preview 3.5 9.8 27.5        # quadros de teste
node cues.js                                # lista de sons sincronizados -> cues.json
python3 sfx.py cues.json sfx.wav            # sintetiza os efeitos (numpy)
node render.js video silent.mp4 30
ffmpeg -i silent.mp4 -i sfx.wav -c:v copy -c:a aac -b:a 192k -shortest saida.mp4
```

Mapa: contornos dos estados de `codeforamerica/click_that_hood` (brazil-states.geojson), simplificados em `br_paths.js`.
