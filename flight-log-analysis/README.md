# Analise de Log de Voo por IA

Prova de conceito de analise automatizada de logs de voo usando IA (Claude),
no contexto do projeto Jacto Drones OS v0.1.

## Motivacao

A analise manual de logs de voo e a **Dor 1** do projeto: na operacao real da
parceira, identificar a causa-raiz de um comportamento observado em ensaio
leva de **1 a 3 dias**. Esta PoC demonstra como uma camada de IA pode reduzir
essa analise de dias para segundos, lendo um log de voo bruto e produzindo um
relatorio de diagnostico em linguagem natural.

## Arquitetura

O fluxo tem duas etapas desacopladas:

```
log.ulg  ──[extract_flight_summary.py]──►  resumo.json  ──[analyze_flight.py]──►  relatorio
 (23 MB)        extracao + reducao          (poucas KB)        analise por IA       (texto)
```

1. **Extrator** (`extract_flight_summary.py`): le o ULog (formato PX4), extrai
   os campos relevantes (altitude, atitude, vibracao, bateria, GPS, fases de
   voo), reduz mais de 200 mil amostras de telemetria a um resumo estruturado
   com estatisticas e deteccao automatica de pontos de atencao. Saida: JSON.

2. **Analisador** (`analyze_flight.py`): envia o resumo a IA (Claude), que atua
   como analista senior de telemetria e produz um relatorio em quatro secoes:
   perfil do voo, saude dos subsistemas, pontos de atencao e veredito.

A separacao em duas etapas e deliberada: a extracao e deterministica e barata
(roda sem IA), e so o resumo enxuto vai para a IA. Isso controla custo e evita
enviar o log bruto de 23 MB para o modelo.

## Uso

```bash
# Instalar dependencias
pip install -r requirements.txt

# Etapa 1: extrair o resumo do log
python extract_flight_summary.py caminho/do/voo.ulg --out resumo.json

# Etapa 2: analisar com IA
python analyze_flight.py resumo.json --out relatorio.md
```

A autenticacao da IA usa a variavel de ambiente `ANTHROPIC_API_KEY`.

## Pontos de atencao detectados automaticamente

O extrator ja sinaliza condicoes que merecem olhar humano, antes mesmo da IA:

- Clipping no acelerometro (vibracao excessiva)
- Desvio padrao de aceleracao acima do tipico
- Inclinacao (roll/pitch) acima de 30 graus em voo nominal
- Bateria final abaixo de 20%
- Menos de 6 satelites GPS
- Altitude final muito acima da referencia (deteccao de pouso)

## Integracao com a esteira

Esta PoC roda como script standalone, mas foi desenhada para integrar a
esteira de CI da mesma forma que os demais workflows de IA do projeto: o job
de testes SITL gera o log, e a analise por IA roda como etapa subsequente,
anexando o relatorio aos artefatos do pipeline.

## Restricoes

Codigo desenvolvido com log sintetico de simulacao PX4-SITL. Nao processa
dados reais ou proprietarios da Jacto Drones, em conformidade com as
restricoes do TAPI do projeto.
