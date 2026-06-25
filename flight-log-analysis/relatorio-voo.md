# Relatório de Análise de Voo

**Arquivo:** `sitl_takeoff_rtl_2026-06-13.ulg`
**Ambiente:** Simulação PX4-SITL
**Duração total do log:** 106,0 s
**Versão de firmware:** 17956928
**Dropouts de log:** 0

---

## 1. Perfil do voo

O log cobre 106,0 segundos e descreve um ciclo simples de decolagem,
hover e retorno (takeoff / RTL), totalmente automático.

A aeronave passou a maior parte do registro parada no solo: do início
(t = 0,2 s) até t = 61,3 s ela permaneceu em **AUTO_LOITER** na referência de
solo (altitude inicial 0,0 m). A decolagem efetiva (**AUTO_TAKEOFF**) só
ocorreu em t = 61,3 s — ou seja, cerca de 61 s do log são de espera no solo,
e a janela realmente aérea é de aproximadamente 43 s (≈ t = 61,3 s a 105 s).

Na subida, a aeronave atingiu o ponto mais alto da trajetória em **2,8 m**,
com velocidade vertical de subida máxima de 0,93 m/s. Em t = 67,7 s ela
estabilizou novamente em **AUTO_LOITER**, mantendo um hover baixo (altitude
média de todo o log de apenas 0,66 m, coerente com um teste de hover de baixa
altura). Em t = 92,1 s iniciou o **AUTO_RTL**, descendo a no máximo 0,75 m/s,
e em t = 105,0 s voltou a **AUTO_LOITER**, encerrando praticamente pousada com
altitude final de 0,45 m (mínimo registrado de -0,25 m, dentro do ruído do
referencial de solo). A perna aérea foi suave: a aeronave nunca passou de
~2,8 m e as velocidades verticais ficaram bem abaixo de 1 m/s nos dois
sentidos.

---

## 2. Saúde dos subsistemas

- **Bateria — nominal.** A carga caiu de 98,9 % para 81,0 % (consumo de
  17,9 %) ao longo dos 106 s. A tensão permaneceu estável em 16,2 V do início
  ao fim, sem queda visível sob carga — comportamento esperado de um pack
  saudável (e típico do modelo de bateria do SITL). Sem sinais de sag de
  tensão ou de aeronave entrando em regime de baixa carga.

- **GPS — nominal.** Contagem de satélites constante em 10 (mínimo = máximo =
  média = 10,0). É um número sólido para fix 3D estável; o valor fixo e sem
  variação é característico do ambiente simulado.

- **Vibração — nominal.** Magnitude média de aceleração de 9,84 m/s²,
  praticamente colada na gravidade (≈ 9,81 m/s²), com desvio-padrão baixo de
  0,69 e **zero eventos de clipping** do acelerômetro. Indica medições limpas,
  sem ruído estrutural relevante.

- **Atitude — nominal.** Roll máximo absoluto de 9,2° e pitch máximo absoluto
  de 4,3°. São excursões pequenas e controladas, coerentes com um perfil de
  hover e RTL em condições calmas; nenhum indício de instabilidade ou correção
  agressiva.

---

## 3. Pontos de atenção

O resumo automático não detectou nenhum ponto de atenção
("metricas dentro de faixas tipicas para voo nominal"), e os números
confirmam isso: vibração limpa, GPS estável, bateria sem sag e atitude bem
comportada. **Foi um voo limpo.**

Como observações finas — não problemas, apenas pontos de acompanhamento dado
o contexto de simulação:

- **Perfil de baixa altitude.** O pico foi de apenas 2,8 m e a média de
  0,66 m. É consistente com um teste curto de hover, mas vale confirmar que
  esse era o objetivo do ensaio — não há aqui um envelope de voo amplo para
  avaliar desempenho em subida/cruzeiro.
- **Longa permanência no solo antes da decolagem.** ~61 s dos 106 s do log
  são AUTO_LOITER no solo. O consumo de 17,9 % de bateria deve ser lido contra
  os ~43 s realmente aéreos, e não contra a duração total, ao se estimar
  autonomia.
- **Tensão e satélites perfeitamente constantes.** Voltagem fixa em 16,2 V e
  10 satélites sem variação alguma são típicos do SITL; em voo real espera-se
  alguma flutuação, então essas métricas têm valor limitado para inferir
  comportamento de hardware embarcado.

---

## 4. Veredito

**Voo nominal:** decolagem, hover e RTL automáticos executados de forma limpa,
com todos os subsistemas em faixa, zero dropouts e nenhum clipping — não há
nada que demande investigação.
