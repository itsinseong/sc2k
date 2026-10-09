#!/bin/zsh
# PaddleOCR 배치를 돌리고, Mac 여유 메모리 8% 미만이 30초(6번 연속) 이어지면 멈춘다. 모델 불러올 때의 순간 출렁임은 넘긴다.
# 끝난 달은 paddle/*.md로 남아서 다시 돌리면 이어간다.
S=${0:A:h}; cd ${S:h:h}/docs/research/읽기엔진시험_2026-10-09
caffeinate -i nice -n 15 ~/.venvs/paddleocr/bin/python $S/paddle_batch.py > paddle_batch.log 2>&1 &
pid=$!; low=0
while kill -0 $pid 2>/dev/null; do
  f=$(memory_pressure | awk '/free percentage/{gsub("%","",$5);print $5}')
  if [ "$f" -lt 8 ]; then low=$((low+1)); else low=0; fi
  if [ $low -ge 6 ]; then pkill -f paddle_batch.py; echo "$(date +%H:%M) 메모리 여유 ${f}%가 30초 이어져 멈춤" >> results.txt; break; fi
  sleep 5
done
