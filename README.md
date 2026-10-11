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

## Configurando o arquivo .env

O `.env` é um arquivo de texto que guarda os segredos do projeto: tokens e senhas. Ele fica só na sua máquina. O `.gitignore` já vem configurado para o git ignorar esse arquivo, então ele nunca sobe para o GitHub. O que sobe é só o `.env.example`, que tem os mesmos campos vazios, como modelo.

Abra o `.env` num editor de texto e preencha campo por campo:

* `DISCORD_TOKEN`: o token do seu bot. Pegue em discord.com/developers/applications, clicando no seu aplicativo, aba Bot, botão Reset Token. Cole o valor depois do sinal de igual, sem aspas e sem espaços.
* `DATABASE_URL`: onde os dados do treino ficam guardados. Para começar simples, deixe o valor padrão do exemplo, que usa SQLite local e não precisa de nada externo: `sqlite+aiosqlite:///./nexusia.db`. Quando quiser Postgres (recomendo o Neon, plano gratuito), crie o banco no painel deles e cole a string de conexão trocando o usuário, a senha e o host pelos seus.
* `CHAT_CHANNEL_ID`: o ID numérico do canal onde o bot conversa sem comando. No Discord, ative o modo desenvolvedor (Configurações, Avançado), clique com o botão direito no canal e escolha Copiar ID do Canal.
* `TRAINER_BOT_IDS`: só preencha se você tiver um segundo bot treinador. Deixe vazio para uso normal.
* `DISCORD_TRAINING_INGESTION_ENABLED`: vem `false` de fábrica, que significa que nada do que é dito no servidor vira dado de treino. Só mude para `true` se você for o dono do servidor, avisar as pessoas e tiver base para isso.
* O resto (`MODEL_DIRECTORY`, `MAX_GENERATION_TOKENS` e os demais) já vem com valores sensatos. Só mexa se souber o que cada um faz.

Regras de segurança que valem sempre: nunca cole token em chat, issue ou print de tela. Se um token vazar, gere outro na hora no portal do Discord. Nunca edite o `.env.example` colocando valores reais, ele é público.

## Configurando o bot no Discord

1. Crie um aplicativo em discord.com/developers/applications e marque como bot
2. Na aba Bot, ligue a intent privilegiada **Message Content Intent**
3. Copie o token para `DISCORD_TOKEN` no `.env`, como explicado acima
4. Convide o bot para o seu servidor com permissão de ler e enviar mensagens
5. Confira se o `CHAT_CHANNEL_ID` no `.env` é o canal certo

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
