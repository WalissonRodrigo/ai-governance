# RTK - Rust Token Killer

**Usage**: Token-optimized CLI proxy (60-90% savings on dev operations)

## Installation

### Quick Install (Linux/macOS)

```bash
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/master/install.sh | sh
```

### Homebrew (macOS/Linux)

```bash
brew install rtk-ai/tap/rtk
```

### Cargo (universal — requires Rust)

```bash
cargo install --git https://github.com/rtk-ai/rtk rtk
```

### Pre-built Binaries (Windows/Linux/macOS)

The installer (`install.sh`) automatically downloads the latest binary from [GitHub releases](https://github.com/rtk-ai/rtk/releases) based on your platform and architecture:

- **macOS**: `rtk-x86_64-apple-darwin.tar.gz` / `rtk-aarch64-apple-darwin.tar.gz`
- **Linux**: `rtk-x86_64-unknown-linux-musl.tar.gz` / `rtk-aarch64-unknown-linux-gnu.tar.gz`
- **Windows**: `rtk-x86_64-pc-windows-msvc.zip` / `rtk-aarch64-pc-windows-msvc.zip`

Download manual: [GitHub releases](https://github.com/rtk-ai/rtk/releases)

**Windows users**: Extract `rtk.exe` to a directory in your PATH (e.g., `C:\Users\<you>\.local\bin`). Run from Command Prompt, PowerShell, or Windows Terminal — do not double-click the `.exe`.

### Post-Install: Activate Hook

```bash
rtk init -g    # Installs PreToolUse hook in Claude Code settings.json
```

## Verification

```bash
rtk --version         # Should show: rtk X.Y.Z
rtk gain              # Should show savings dashboard (not "command not found")
which rtk             # Verify correct binary
```

⚠️ **Name collision**: If `rtk gain` fails but `rtk --version` works, you may have `reachingforthejack/rtk` (Rust Type Kit) installed instead. Fix:

```bash
cargo uninstall rtk
cargo install --git https://github.com/rtk-ai/rtk rtk
rtk gain              # Verify correct RTK
```

## Meta Commands (always use rtk directly)

```bash
rtk gain              # Show token savings analytics
rtk gain --history    # Show command usage history with savings
rtk discover          # Analyze Claude Code history for missed opportunities
rtk proxy <cmd>       # Execute raw command without filtering (for debugging)
```

## Hook-Based Usage

All other commands are automatically rewritten by the Claude Code hook.
Example: `git status` → `rtk git status` (transparent, 0 tokens overhead)

Refer to CLAUDE.md for full command reference.
