import os
from pathlib import Path

def main():
    # get all markdown files in the ./book directory
    book_dir = './book'
    md_files = list(Path(book_dir).rglob('*.md'))
    for md_file in md_files:
        cmd = f'python -m linkcheckmd {md_file.as_posix()}'
        print(f"Checking links in {md_file.as_posix()}")
        # run command and print stdout and stderr
        result = os.popen(cmd).read()
        print(result)

if __name__ == "__main__":
    main()