# Institucional v2: "Já pediu empréstimo e só te mostraram uma opção?"

A história do vídeo da Nix (mapa, bancos, chat, 24h), refeita segundo `/Motion.md`, em duas versões:
`phoenix-institucional-pastel.mp4` e `phoenix-institucional-orange.mp4` (49s, 1080×1920, 100 BPM, -14 LUFS).

| Batidas (0,6s) | Cena |
|---|---|
| 0–8 | Gancho: "Já pediu empréstimo e só te mostraram *uma opção?*" (visível no quadro 0) |
| 8–14 | "Na Phoenix Brasil, você recebe a *melhor.*" (a palavra troca de fonte, como a Nix comparando) |
| 14–24 | Mapa do Brasil acendendo · +5.000 clientes atendidos |
| 24–32 | +20 bancos parceiros · logos |
| 32–50 | "Quem compara é a Nix." · conversa às 03:12 · 20 bancos consultados · um único cartão com a melhor oferta |
| 50–56 | 24h por dia · especialistas em horário comercial |
| 56–66 | Post em colaboração com Sônia Abrão (Instagram) · 10,6 mil curtidas · "inclusive para quem está negativado" |
| 66–82 | Fênix · phoenixbrasil.com/clt · nunca pedimos valor antecipado · aviso legal |

`sonia_card.png` é um recorte do post real (cabeçalho da colaboração + vídeo), sem comentários nem nomes de terceiros.

```bash
export NODE_PATH=$(npm root -g)
node render.js preview theme=orange 0 13.2 27.6     # theme=pastel|orange
node render.js cues theme=pastel cues.json
python3 audio.py cues.json mix_raw.wav
ffmpeg -i mix_raw.wav -af loudnorm=I=-14:TP=-1:LRA=9 -ar 48000 mix.wav
node render.js video theme=orange silent.mp4 30
ffmpeg -i silent.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest saida.mp4
```
