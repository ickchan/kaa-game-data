#!/usr/bin/env python3
"""生成 manifest.json：包含版本号和所有输出文件的 md5/size。"""
import argparse, hashlib, json, os
from pathlib import Path

def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sha', required=True, help='gakumasu-diff commit SHA')
    parser.add_argument('--sprites-dir', required=True, help='sprites 根目录（包含 idol_cards/ skill_cards/ drinks/）')
    parser.add_argument('--db', required=True, help='game.db 路径')
    parser.add_argument('--output', required=True, help='manifest.json 输出路径')
    args = parser.parse_args()

    files = {}

    # game.db
    files['game.db'] = {'md5': md5(args.db), 'size': os.path.getsize(args.db)}

    # sprites
    for category in ('idol_cards', 'skill_cards', 'drinks'):
        cat_dir = Path(args.sprites_dir) / category
        if cat_dir.exists():
            for f in sorted(cat_dir.iterdir()):
                if f.suffix == '.png':
                    key = f'{category}/{f.name}'
                    files[key] = {'md5': md5(str(f)), 'size': f.stat().st_size}

    manifest = {'version': args.sha, 'files': files}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as fp:
        json.dump(manifest, fp, indent=2, ensure_ascii=False)
    print(f'manifest.json 写入完成，共 {len(files)} 个文件')

if __name__ == '__main__':
    main()
