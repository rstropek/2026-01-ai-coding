# Claude Code — Session Handling Demo

## Setup

```bash
# Verify Claude Code is installed
claude --version

# Create a scratch project
mkdir ~/demo-sessions && cd ~/demo-sessions
git init
echo "# Demo" > README.md
git add . && git commit -m "init"
```

## 1. Starting a Session

```bash
# Start interactive REPL
claude

# Start REPL with an initial prompt
claude "explain this project"

# Non-interactive / print mode — runs the prompt and exits
claude -p "List all .py files and what they do"

# With system prompt override
claude --system-prompt "You are a senior Python engineer called Snakie. Be concise."
# Ask e.g. "Who are you?"
```

## 2. Tools — Restricting and Pre-approving

### 2a. Permission Error Demo

By default, Claude asks for confirmation before writing files. In non-interactive `-p` mode there is no TTY to approve the prompt — so Claude will refuse:

```bash
# ❌ Fails — Claude needs write permission but can't prompt in -p mode
claude -p "Create a hello.py that prints Hello, World"
```

### 2b. Pre-approving tools with `--allowedTools`

`--allowedTools` marks specific tools as pre-approved (no prompt), without disabling everything else.

```bash
# ✅ Write is pre-approved — Claude creates the file without asking
claude --allowedTools "Edit(*.py)" -p "Create a hello.py that prints Hello, World"

# Verify
cat hello.py && python hello.py
```

**Demo contrast — Write allowed but Bash not pre-approved:**

```bash
# Claude creates the file but will prompt/fail when trying to run it
claude --allowedTools "Edit(*.py)" -p "Create hello.py and run it to verify output"

# ✅ Add Bash to let Claude also verify its own output
claude --allowedTools "Edit(*.py),Bash" -p "Create hello.py and run it to verify output"
```

### 2c. Skip all permissions (YOLO mode)

```bash
# ✅ Bypasses every confirmation — use only in trusted/CI environments
claude --dangerously-skip-permissions -p "Create a hello.py that prints Hello, World"
```

> `--dangerously-skip-permissions` grants everything.

### 2d. Configure permissions

* [Available tools](https://code.claude.com/docs/en/settings#tools-available-to-claude)
* [Configure permissions](https://code.claude.com/docs/en/permissions)
* [Claude settings](https://code.claude.com/docs/en/settings)

## 3. Stopping / Exiting a Session

```bash
# From inside the interactive REPL:
/exit
# or Ctrl+D

# Sessions are persisted automatically — no explicit save step needed
```

## 4. Resuming / Continuing a Session

```bash
# Continue the most recent conversation (interactive)
claude -c

# Continue most recent, non-interactively
claude -c -p "What did I just say?"

# Resume a specific session — shows interactive picker if no ID given
claude -r

# Resume a specific session by ID
claude -r <session-id>
```

## 5. Forking a Session

Did Forking branches the conversation at its current state into a new session, leaving the original intact. Use `--fork-session` together with `-r`.

```bash
# Fork the current state of a session into a new session
claude -r "abc123-def456" --fork-session
# → spawns a new session ID

# Continue each branch independently
claude -r "def456" "Add error handling and retries"
claude -r "ghi789" "Add error handling and retries"
```

## 6. Session State on Disk

Sessions are stored locally per project:

```bash
# Sessions live under ~/.claude/projects/
ls ~/.claude/projects/

# Each project directory contains JSONL conversation files
# The session ID maps to a file in the relevant project folder
```

## 7. Worktree

```bash
# Start a new Claude session in a separate worktree
claude --worktree feature-responsive

# Will create an isolated worktree (branch has same name)
# and start a new Claude session in it.

claude --worktree
# Will auto-generate a worktree/branch name
```

Note: Worktree cleanup is done automatically when you exit the session.
