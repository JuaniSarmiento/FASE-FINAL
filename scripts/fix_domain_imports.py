import os

def fix_imports(root_dir):
    print(f"Scanning {root_dir}...")
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix: ...shared -> src.domain.shared
                if "from ...shared" in content:
                    print(f"Fixing {filepath}")
                    new_content = content.replace("from ...shared", "from src.domain.shared")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == "__main__":
    fix_imports("src/domain")
