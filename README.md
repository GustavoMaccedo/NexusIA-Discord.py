# Nexusia

A Nexusia é uma IA de conversa feita do zero, em Python, que mora no Discord. Ela não usa ChatGPT, Claude, Gemini nem nenhum modelo pronto. A rede neural foi escrita aqui no projeto com PyTorch, começou com pesos aleatórios e aprende com os próprios dados de treino.

Como ela funciona, em poucas palavras: gente conversa no canal, o bot observa e responde com o modelo próprio, as conversas elegíveis viram exemplos de treino, e de tempos em tempos um ciclo treina um modelo candidato, avalia e promove se ele estiver melhor. Se piorar, o sistema rejeita e mantém o atual.

## Do que você precisa

* Python 3.11 ou mais novo
* Uma conta no Discord com permissão de criar aplicativos
* Um banco Postgres (recomendo o Neon, que tem plano gratuito) ou SQLite para testes locais
* CPU com uns 2 GB de RAM livre para treinar o modelo pequeno. Sem GPU dá para rodar, só é mais lento

## Instalando

```bash
pip install -r requirements.txt -r requirements-training.txt -r requirements-dev.txt
cp .env.example .env
```

Depois abra o `.env` e preencha pelo menos `DISCORD_TOKEN` e `DATABASE_URL`. O `.env` nunca vai para o git, pode confiar.

## Configurando o bot no Discord

1. Crie um aplicativo em discord.com/developers/applications e marque como bot
2. Na aba Bot, ligue a intent privilegiada **Message Content Intent**
3. Copie o token para `DISCORD_TOKEN` no `.env`
4. Convide o bot para o seu servidor com permissão de ler e enviar mensagens
5. No `.env`, coloque o ID do canal de conversa em `CHAT_CHANNEL_ID`

## Ligando

```bash
python scripts/inspect_environment.py
python scripts/initialize_project.py
python scripts/check_data_authorization.py
python -m discord_ai.bot.main
```

O primeiro script mostra se a máquina aguenta. O segundo cria as pastas, o corpus inicial e o banco. O terceiro confirma que a coleta de dados está desligada por padrão. O último liga o bot.

No canal configurado, é só falar que ela responde, sem comando. Os comandos slash continuam existindo: `/ia` para conversar e ver o estado do modelo, `/feedback` para avaliar respostas, `/aprendizado` para ver a fila de treino, `/admin` para administração.

## Treinando o tokenizador e o modelo

O tokenizador é treinado do nosso próprio corpus, ninguém baixa vocabulário pronto:

```bash
python scripts/train_initial_model.py --corpus datasets/incoming --vocab 4000 --epochs 3 --batch 8
```

Isso treina o BPE, inicializa o Transformer do zero, treina prevendo o próximo token e salva o checkpoint com manifesto de origem em `checkpoints/active`. Para continuar de onde parou, use `scripts/resume_training.py`. Para avaliar num conjunto separado:

```bash
python scripts/evaluate_model.py
python scripts/generate_sample.py --prompt "Olá!"
```

## O ciclo de aprendizado contínuo

Quando a coleta está ligada (`DISCORD_TRAINING_INGESTION_ENABLED=true`), o fluxo é este: mensagem autorizada, validação e filtragem, fila de exemplos, lote de treino, versão candidata, avaliação independente, aprovação ou rejeição, e troca do modelo ativo. Rejeitou, volta sozinho para a versão estável.

```bash
bash scripts/continual_loop.sh
```

Cada ciclo respeita trava anti-dupla, nunca treina dentro do evento do Discord e nunca sobrescreve o único checkpoint bom.

## Backup e restauração

Copie `checkpoints/active` (modelo, manifesto e tokenizador) e o dump do banco para um lugar seguro. Para voltar, é só copiar de volta e conferir a origem no `meta.json`, que registra dataset, métricas e hashes.

## Privacidade

A coleta vem desligada de fábrica. Ligar a intent no portal do Discord não autoriza treino, é preciso ativar a flag no `.env` e avisar o servidor. IDs são pseudonimizados, filtros barram spam e comandos, e existe o comando de esquecimento para remover exemplos. Dado que já virou peso não tem como desaprender, então exclusão exige retreino, e isso está documentado no código.

## Estrutura do projeto

```text
discord_ai/bot/       bot Discord modular (cogs, serviços, banco)
discord_ai/model/     Transformer autoral (atenção, blocos, geração, checkpoint)
discord_ai/training/  corpus, dataset, treino, avaliação, promoção e rollback
scripts/              comandos de rotina (init, treino, avaliação, verificação)
tests/                testes unitários, de integração, do modelo e do treino
```

## Limitações honestas

Modelo pequeno em CPU aprende devagar e no começo gera texto estranho. Isso é medido com loss e perplexidade, não escondido. Treino grande pede horas de CPU e memória, então comece pequeno e cresça com calma. Corpus repetitivo demais vira decoreba, diversidade importa mais que tamanho.
