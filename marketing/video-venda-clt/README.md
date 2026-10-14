# Vídeo de venda: Crédito CLT (Pastel e TV)

Segue as regras de `/Motion.md`. Um único `index.html` gera os dois estilos:

- `phoenix-venda-clt-pastel.mp4`: identidade do site (creme, DM Serif, blocos pastel).
- `phoenix-venda-clt-tv.mp4`: identidade do comercial da TV (preto, Poppins Bold, laranja).

30,6s · 1080×1920 · 100 BPM · trilha e efeitos sintetizados em código (`audio.py`) · -14 LUFS.

## Roteiro (em batidas de 0,6s)

| Batidas | Cena |
|---|---|
| 0–4 | Gancho: "Nome negativado? Com carteira assinada, você ainda pode ter crédito." + selo "Como visto na TV" |
| 4–12 | Empréstimo pessoal sem garantia chega a 17% ao mês (riscado) |
| 12–20 | Pegue hoje, comece a pagar em até 90 dias · desconto na folha · mesmo negativado |
| 20–28 | A Nix compara +20 bancos · logos dos parceiros · "a melhor oferta pra você" |
| 28–36 | A Tarde é Sua com Sônia Abrão · +5.000 clientes · nunca pedimos depósito antecipado |
| 36–51 | Fênix · phoenixbrasil.com/clt · Nix online 24h · aviso legal |

## Gerar de novo

```bash
export NODE_PATH=$(npm root -g)
node render.js preview theme=tv 0 2.1 9.9           # quadros de teste (theme=pastel|tv)
node render.js cues theme=pastel cues.json          # grade de sons
python3 audio.py cues.json mix_raw.wav
ffmpeg -i mix_raw.wav -af loudnorm=I=-14:TP=-1:LRA=9 -ar 48000 mix.wav
node render.js video theme=tv silent.mp4 30
ffmpeg -i silent.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest saida.mp4
```
