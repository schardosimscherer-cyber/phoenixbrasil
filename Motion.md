# Motion: regras de estúdio da Phoenix Brasil

Regras para todo vídeo animado da Phoenix Brasil. Valem para qualquer pessoa, ou o Claude, que for criar ou editar um vídeo em `marketing/`.

## Contrato de render

- Todo vídeo é uma função pura do tempo: `window.render(t)` desenha o quadro exato do instante `t`.
- Nada de transição CSS, `setTimeout`, `requestAnimationFrame` ou estado guardado entre quadros. Ruído e aleatoriedade só com semente fixa.
- Exportar com `node render.js` (Playwright + ffmpeg), H.264 `yuv420p`, CRF 16 a 17, 30 fps, 1080×1920.

## Visual

- **Proibido o óbvio:** título centralizado sobre degradê, tudo entrando com fade/blur, rótulos de canto e bordas de moldura, brilho em elementos de interface, partículas genéricas.
- Uma fonte de destaque, uma fonte de interface e uma cor de destaque.
  - **Pastel (marca/site):** DM Serif Display + Poppins · fundo `#F8F6F2`, texto `#111`, destaque em blocos pastel (`#EDD9D2`, `#D6E5D8`, `#D2DCE8`, `#EDE8D6`).
  - **TV (anúncio):** Poppins 700 + Poppins 400 · fundo `#0B0B0D`, texto branco, destaque laranja `#E07B39` (o mesmo do comercial na TV).
- A cada 2 a 4 segundos, algo novo acontece na tela.
- O gancho já está visível no quadro 0. Nada de tela vazia no começo.
- **Áreas seguras (Reels/TikTok):** conteúdo importante entre y 220 e 1480, e x 72 e 960. O rodapé e a lateral direita ficam cobertos pela interface.
- Texto legível no celular: mínimo de 44 px em textos de apoio e 28 px em avisos legais.
- Fênix: usar `bird_ink.png` em fundo claro e `bird_white.png` em fundo escuro.

## Som

- A trilha e os efeitos são sintetizados em código, a menos que alguém forneça uma trilha.
- Tudo cai na grade de batidas medida (`beats.json` / BPM fixo). Cortes e "hits" acontecem na batida.
- Graves com harmônicos: alto-falante de celular não reproduz abaixo de cerca de 150 Hz.
- Loudness final: **-14 LUFS**, pico de -1 dBTP.

## Conteúdo e conformidade

- Afirmações aprovadas pela empresa: atende negativados no Crédito CLT; nunca pede valor antecipado; até 90 dias para a 1ª parcela (conforme a instituição); +20 bancos; +5.000 clientes; Nix atende 24h; especialistas em horário comercial.
- Sem promessas como "aprovação garantida", "dinheiro fácil" ou "melhor taxa do mercado".
- Simulações mostradas são fictícias e marcadas como "Simulação ilustrativa".
- Prints de clientes: apagar nome, telefone, CPF e foto, e ter autorização.

## Revisar antes de mostrar qualquer coisa

1. Renderizar um quadro por batida em uma folha de contato e **olhar**.
2. Dar nota de 1 a 10 em: gancho nos primeiros 2s, leitura no tamanho do celular, qualidade do movimento, variedade, fidelidade à marca e sincronia com o som.
3. Corrigir os 3 piores problemas. Repetir até todas as notas estarem em 8 ou mais.
4. Só então fazer o render completo.
