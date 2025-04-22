import os

def print_tree(start_path='.', prefix=''):
    files = sorted(os.listdir(start_path))
    entries = [f for f in files if not f.startswith('.')]  # Skip hidden files

    for index, name in enumerate(entries):
        path = os.path.join(start_path, name)
        connector = '├── ' if index < len(entries) - 1 else '└── '
        print(prefix + connector + name)
        if os.path.isdir(path):
            extension = '│   ' if index < len(entries) - 1 else '    '
            print_tree(path, prefix + extension)

if __name__ == '__main__':
    print("📂 Project Structure:\n")
    print_tree('.')
