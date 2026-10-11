#!/usr/bin/env bash
# Loop de aprendizado contínuo: people talk -> watch ingere -> ciclo treina/promove.
# Roda UM ciclo por invocação; agende via cron/systemd ou chame com sleep.
# Trava anti-dupla via arquivo PID (flock não existe neste FS).
# Resultado do último ciclo em logs/continual_last.json.
set -u
cd "$(dirname "$0")/.."
LOCK=./checkpoints/.continual.lock
mkdir -p logs checkpoints/candidates
if [ -f "$LOCK" ]; then
  OLDPID=$(cut -d' ' -f1 "$LOCK" 2>/dev/null || echo "")
  if [ -n "$OLDPID" ] && kill -0 "$OLDPID" 2>/dev/null; then
    echo '{"status":"busy"}'
    exit 0
  fi
fi
echo "$$" > "$LOCK"
INTERVAL="${TRAINING_INTERVAL:-3600}"
OUT="checkpoints/candidates/continual-$(date +%Y%m%d-%H%M%S)"
RES=$(PYTHONPATH=. nice -n 10 python3 -u scripts/continual_train.py \
  --min-new "${CONTINUAL_MIN_NEW:-50}" --max-new 500 --rehearsal 200 \
  --lr 1e-4 --steps-cap 300 --batch 8 --seq 64 --out "$OUT" 2>>logs/continual.log)
echo "$RES" | tail -1 > logs/continual_last.json
echo "$RES" | tail -1
rm -f "$LOCK"
