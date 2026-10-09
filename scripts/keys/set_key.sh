#!/bin/zsh
# 키를 화면에 보이지 않게 입력받아 레포 루트 .env.local에 저장한다. 같은 이름 줄이 있으면 바꾼다.
# 사용: zsh scripts/keys/set_key.sh TYPESAFE_API_KEY
name=${1:-TYPESAFE_API_KEY}
f=${0:A:h:h:h}/.env.local
print -n "$name 값을 붙여 넣고 Enter (입력이 화면에 보이지 않습니다): "
read -rs key; echo
key=${key//[[:space:]]/}
if [ -z "$key" ]; then echo "비어 있어서 저장하지 않았습니다."; exit 1; fi
touch "$f"; chmod 600 "$f"
grep -v "^$name=" "$f" > "$f.tmp" 2>/dev/null; mv "$f.tmp" "$f"; chmod 600 "$f"
print -r -- "$name=$key" >> "$f"
echo "저장했습니다: $name (앞 4글자 ${key[1,4]}…, 길이 ${#key}자) → $f"
echo "이 창은 닫아도 됩니다."
