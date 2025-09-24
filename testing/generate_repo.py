#!/usr/bin/env python3

# GPT CONTRIBUTED SCRIPT
# DIDN'T NEED MUCH MOD

import os
import random
import string
import subprocess
from pathlib import Path

REPO_DIR = "random_git_repo"
MAX_FILES = 400
MAX_FILE_SIZE_KB = 50
NUM_COMMITS = 200
BRANCH_PROB = 0.2
TAG_PROB = 0.1
DELETE_PROB = 0.1
MOVE_PROB = 0.1

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def random_filename():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8)) + ".txt"

def random_content(max_kb=50):
    size = random.randint(1, max_kb) * 1024
    return os.urandom(size)

def create_file(path):
    with open(path, "wb") as f:
        f.write(random_content(MAX_FILE_SIZE_KB))

def modify_file(path):
    with open(path, "a") as f:
        f.write(f"\nRandom edit {random.randint(0, 1_000_000)}")

# Initialize repo
if os.path.exists(REPO_DIR):
    subprocess.run(f"rm -rf {REPO_DIR}", shell=True)
os.makedirs(REPO_DIR)
os.chdir(REPO_DIR)
run("git init")

files = []

# Initial random files
for _ in range(MAX_FILES//2):
    f = random_filename()
    create_file(f)
    files.append(f)

run("git add .")
run('git commit -m "Initial random commit"')

for i in range(NUM_COMMITS):
    # Randomly add new file
    if random.random() < 0.5:
        f = random_filename()
        create_file(f)
        files.append(f)
        run(f"git add {f}")

    # Randomly modify files
    for f in files:
        if random.random() < 0.5:
            modify_file(f)
            run(f"git add {f}")

    # Randomly delete a file
    if files and random.random() < DELETE_PROB:
        i=i+1
        f = random.choice(files)
        run(f'git commit -m "Random commit {i+1}"')
        run(f"git rm {f}")
        files.remove(f)

    # Randomly rename a file
    if files and random.random() < MOVE_PROB:
        f = random.choice(files)
        new = random_filename()
        os.rename(f, new)
        files[files.index(f)] = new
        run(f"git add -A")

    # Commit changes
    run(f'git commit -m "Random commit {i+1}"')

    # Randomly create a branch
    if random.random() < BRANCH_PROB:
        branch = f"branch_{i+1}"
        run(f"git checkout -b {branch}")
        # Make a small change on branch
        if files:
            f = random.choice(files)
            modify_file(f)
            run(f"git add {f}")
            run(f'git commit -m "Branch {branch} commit"')
        run("git checkout master")
        run(f"git merge {branch} -m 'Merge {branch}'")

    # Randomly tag commit
    if random.random() < TAG_PROB:
        tag = f"v0.{i+1}"
        run(f"git tag {tag}")

    if random.randint(1,10) <=2:
        run("git gc")

# Done
print("Random git repository generated.")
run("git log --oneline --graph --all --decorate")
