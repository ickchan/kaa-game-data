import os, sys, json

def main():
    sha = sys.argv[1]
    notes = f'gakumasu-diff commit: {sha}'
    skipped_path = os.path.join('output', 'skipped_assets.json')

    if os.path.exists(skipped_path):
        with open(skipped_path, encoding='utf-8') as f:
            skipped = json.load(f)
        notes += f'\n\n## Skipped Assets ({len(skipped)})\n\n'
        notes += 'These assets are referenced in game master data but not yet available on the game CDN.\n'
        notes += 'They will be included in a future build when the CDN is updated.\n\n'
        notes += '| Asset ID | Reference |\n| --- | --- |\n'
        for item in skipped:
            notes += f"| {item['id']} | {item['refId']} |\n"

    with open('release_notes.md', 'w', encoding='utf-8') as f:
        f.write(notes)
    print(notes)

if __name__ == '__main__':
    main()
