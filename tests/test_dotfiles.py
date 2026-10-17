"""Integration checks in temporary home directories; requires pexpect and Zsh."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

import pexpect


REPO = Path(__file__).resolve().parents[1]
ZSH = shutil.which("zsh")
BASH = shutil.which("bash")


class DotfilesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-test-")
        self.addCleanup(self.temp.cleanup)
        self.user_dir = Path(self.temp.name)
        self.env = dict(os.environ)
        for key in ("ZDOTDIR", "BASH_ENV", "ENV", "TMUX", "STY", "EDITOR", "VISUAL", "DOTFILES_KEYTIMEOUT"):
            self.env.pop(key, None)
        self.env.update(
            HOME=str(self.user_dir),
            XDG_CONFIG_HOME=str(self.user_dir / "config"),
            XDG_DATA_HOME=str(self.user_dir / "data"),
            XDG_STATE_HOME=str(self.user_dir / "state"),
            XDG_CACHE_HOME=str(self.user_dir / "cache"),
            TERM="xterm-256color",
            NVIM_LOG_FILE=str(self.user_dir / "nvim.log"),
            DOTFILES_TEST_REPO=str(REPO),
        )

    def link_shell(self, plugins=True):
        for name in ("bashrc", "bash_profile", "bash", "inputrc", "zshrc"):
            (self.user_dir / ("." + name)).symlink_to(REPO / name)
        (self.user_dir / ".dotfiles").symlink_to(REPO)
        for name in ("shell", "zsh"):
            if plugins:
                (self.user_dir / ("." + name)).symlink_to(REPO / name)
            else:
                shutil.copytree(REPO / name, self.user_dir / ("." + name), ignore=shutil.ignore_patterns("plugins"))
        if not plugins:
            plugin_dir = self.user_dir / ".zsh/plugins"
            plugin_dir.mkdir()
            shutil.copy(REPO / "zsh/plugins/spectrum.zsh", plugin_dir)

    def run_process(self, args, **kwargs):
        return subprocess.run(args, cwd=self.user_dir, env=self.env, capture_output=True, text=True, timeout=20, **kwargs)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "")


@unittest.skipUnless(ZSH, "zsh is required")
class PasteTests(DotfilesTest):
    def setUp(self):
        super().setUp()
        self.link_shell()
        (self.user_dir / ".zshrc_local_after").write_text(r'''
PROMPT='TEST> '
RPROMPT=''
_test_capture() {
    print -r -- "$KEYMAP" > "$HOME/captured.mode"
    print -rn -- "$BUFFER" > "$HOME/captured.text"
    BUFFER=''
    zle .accept-line
}
zle -N _test_capture
bindkey -M viins '^G' _test_capture
bindkey -M vicmd '^G' _test_capture
bindkey -M emacs '^G' _test_capture
''')

    def paste(self, payload, *, delayed_start=False, delayed_end=False, stray_end=False, command_mode=False, emacs=False):
        if emacs:
            with (self.user_dir / ".zshrc_local_after").open("a") as config:
                config.write("bindkey -e\n")
        child = pexpect.spawn(ZSH, ["-d", "-i"], env=self.env, cwd=self.user_dir, encoding="utf-8", timeout=10)
        self.addCleanup(child.close, force=True)
        child.delaybeforesend = 0
        child.expect_exact("TEST> ")
        self.assertNotIn("command not found", child.before)
        if command_mode:
            child.send("\x1b")
            time.sleep(0.5)
        if not stray_end:
            if delayed_start:
                child.send("\x1b")
                time.sleep(0.08)
                child.send("[200~")
            else:
                child.send("\x1b[200~")
        child.send(payload)
        if delayed_end:
            child.send("\x1b")
            time.sleep(0.08)
            child.send("[201~")
        else:
            child.send("\x1b[201~")
        # Confirm typing still inserts text after the paste.
        child.send("!\x07")
        child.expect_exact("\x1b[?2004l")
        deadline = time.monotonic() + 5
        while not (self.user_dir / "captured.text").exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertEqual((self.user_dir / "captured.text").read_text(), payload + "!")
        self.assertIn((self.user_dir / "captured.mode").read_text().strip(), ("main", "viins", "emacs"))
        self.assertFalse((self.user_dir / "should-not-exist").exists())

    def test_normal_paste(self):
        self.paste("echo hello")

    def test_ssh_delayed_start_marker(self):
        self.paste("echo hello", delayed_start=True)

    def test_ssh_delayed_end_marker(self):
        self.paste("echo hello", delayed_end=True)

    def test_orphan_end_marker_does_not_change_case_or_mode(self):
        self.paste("echo hello", stray_end=True)

    def test_paste_from_command_mode_returns_to_insert_mode(self):
        self.paste("echo hello", command_mode=True)

    def test_multiline_and_control_characters_are_literal(self):
        self.paste("touch ~/should-not-exist\necho 'café 日本語'\t# $HOME ~ `date`\x1bX")

    def test_local_emacs_mode_override(self):
        self.paste("echo hello", emacs=True)


class ShellTests(DotfilesTest):
    def test_path_helpers_preserve_literal_names_and_do_not_duplicate(self):
        for shell in (BASH, ZSH):
            with self.subTest(shell=shell):
                result = self.run_process([shell, "-fc", r'''
source "$DOTFILES_TEST_REPO/shell/functions.sh"
target='/tmp/has spaces "quotes" [glob] back\slash'
PATH="/bin:$target:/usr/bin:$target"
path_prepend "$target"
[[ $PATH == "$target:/bin:/usr/bin" ]] || exit 1
path_append "$target"
[[ $PATH == "/bin:/usr/bin:$target" ]] || exit 2
path_remove "$target"
[[ $PATH == /bin:/usr/bin ]] || exit 3
PATH=':/bin::/usr/bin:'
path_remove /bin
[[ $PATH == ::/usr/bin: ]] || exit 4
'''])
                self.assert_success(result)

    def test_directory_helpers_handle_spaces_and_failure(self):
        (self.user_dir / "a b/c d").mkdir(parents=True)
        for shell in (BASH, ZSH):
            with self.subTest(shell=shell):
                result = self.run_process([shell, "-fc", r'''
source "$DOTFILES_TEST_REPO/shell/aliases.sh"
jump "$HOME/a b/c d/file.txt" || exit 1
[[ $PWD == "$HOME/a b/c d" ]] || exit 2
up 01 || exit 3
[[ $PWD == "$HOME/a b" ]] || exit 4
up invalid 2>/dev/null && exit 5
[[ $PWD == "$HOME/a b" ]] || exit 6
cdgr 2>/dev/null && exit 7
[[ $PWD == "$HOME/a b" ]] || exit 8
mcd "$HOME/new dir" || exit 9
[[ $PWD == "$HOME/new dir" ]] || exit 10
'''])
                self.assert_success(result)

    def test_noninteractive_startup_is_quiet(self):
        self.link_shell()
        for shell, rc in ((BASH, "bashrc"), (ZSH, "zshrc")):
            with self.subTest(shell=shell):
                result = self.run_process([shell, "-fc", 'source "$DOTFILES_TEST_REPO/' + rc + '"; printf ready'])
                self.assert_success(result)
                self.assertEqual(result.stdout, "ready")

    def test_zsh_starts_without_optional_plugins_or_term(self):
        self.link_shell(plugins=False)
        self.env.pop("TERM")
        result = self.run_process([ZSH, "-d", "-ic", "print -r -- ready"])
        self.assert_success(result)
        self.assertEqual(result.stdout, "ready\n")

    def test_editor_override_and_local_path_survive(self):
        self.env["EDITOR"] = "custom-editor"
        result = self.run_process([ZSH, "-fc", r'''
source "$DOTFILES_TEST_REPO/shell/functions.sh"
source "$DOTFILES_TEST_REPO/shell/bootstrap.sh"
source "$DOTFILES_TEST_REPO/shell/bootstrap.sh"
[[ $EDITOR == custom-editor && $VISUAL == custom-editor ]] || exit 1
[[ ${#${(M)path:#$HOME/.local/bin}} -eq 1 ]] || exit 2
'''])
        self.assert_success(result)

    def test_prompt_cleanup_and_existing_hook(self):
        self.link_shell()
        result = self.run_process([ZSH, "-dfc", r'''
precmd() { print -r -- original-hook; }
source "$HOME/.zsh/prompt.zsh"
source "$HOME/.zsh/prompt.zsh"
precmd
[[ ${#${(M)precmd_functions:#_dotfiles_prompt_precmd}} -eq 1 ]] || exit 1
RCMD() { print -r -- right-prompt; }
for i in {1..10}; do
    _dotfiles_prompt_precmd
    _dotfiles_prompt_precmd
    async_prompt_complete "$_PROMPT_ASYNC_FD"
    [[ $RPROMPT == right-prompt && -z ${_PROMPT_ASYNC_FD:-} ]] || exit 2
done
[[ -z $(zle -F) ]] || exit 3
print -r -- stderr-still-open >&2
'''])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr, "stderr-still-open\n")
        self.assertEqual(result.stdout, "original-hook\n")


class IntegrationTests(DotfilesTest):
    @unittest.skipUnless((REPO / ".dotbot/bin/dotbot").exists(), "initialize the .dotbot submodule")
    def test_install_links_twice_and_honors_xdg_config_home(self):
        command = [str(REPO / ".dotbot/bin/dotbot"), "-d", str(REPO), "-c", str(REPO / ".install.conf.yaml"), "--only", "link"]
        for _ in range(2):
            self.assert_success(self.run_process(command))
        self.assertEqual((self.user_dir / ".zshrc").resolve(), REPO / "zshrc")
        self.assertEqual((self.user_dir / "config/nvim").resolve(), REPO / "nvim")
        self.assertFalse((self.user_dir / ".vimrc").exists())

    @unittest.skipUnless((REPO / ".dotbot/bin/dotbot").exists(), "initialize the .dotbot submodule")
    def test_install_preserves_existing_claude_settings(self):
        settings = self.user_dir / ".claude/settings.json"
        settings.parent.mkdir()
        settings.write_text('{"theme": "dark"}\n')
        result = self.run_process([str(REPO / ".dotbot/bin/dotbot"), "-d", str(REPO), "-c", str(REPO / ".install.conf.yaml"), "--only", "link"])
        self.assert_success(result)
        self.assertFalse(settings.is_symlink())
        self.assertEqual(settings.read_text(), '{"theme": "dark"}\n')

    @unittest.skipUnless(shutil.which("nvim"), "Neovim is required")
    def test_neovim_filetypes_shortcuts_and_local_override(self):
        (self.user_dir / ".nvim_local.lua").write_text("vim.g.dotfiles_local_loaded = true\n")
        script = self.user_dir / "test.lua"
        script.write_text(r'''
assert(vim.g.dotfiles_local_loaded)
assert(vim.fn.maparg('<C-j>', 'n') ~= '')
vim.cmd('edit sample.yaml')
assert(vim.bo.shiftwidth == 2 and vim.bo.expandtab)
vim.cmd('edit main.go')
assert(vim.bo.shiftwidth == 8 and not vim.bo.expandtab)
vim.cmd('edit Makefrag')
assert(vim.bo.filetype == 'make' and not vim.bo.expandtab)
vim.cmd('edit sample.md')
assert(vim.wo.spell)
vim.cmd('edit main.go')
assert(not vim.wo.spell)
vim.cmd('edit sample.txt')
assert(vim.bo.shiftwidth == 4)
assert(vim.v.errmsg == '', vim.v.errmsg)
vim.cmd('qa!')
''')
        result = self.run_process([shutil.which("nvim"), "--headless", "-u", str(REPO / "nvim/init.lua"), "-l", str(script)])
        self.assert_success(result)

    def test_vercmp_validates_expressions_on_modern_python(self):
        for expression, code in (("1.9 < 2.4 <= 3", 0), ("2.9 < 2.9a", 0), ("3 < 2", 1), ("oops", 2), ("1 < 2 <", 2), ("1 < 2 ?? 3", 2)):
            with self.subTest(expression=expression):
                result = self.run_process([sys.executable, "-S", str(REPO / "bin/vercmp")], input=expression + "\n")
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)

    def test_tmx_matches_exactly_and_cleans_only_its_own_session(self):
        fake_bin = self.user_dir / "bin"
        fake_bin.mkdir()
        fake_tmux = fake_bin / "tmux"
        fake_tmux.write_text('''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
with Path(os.environ['HOME'], 'tmux-calls').open('a') as log:
    log.write(json.dumps(sys.argv[1:]) + '\\n')
if sys.argv[1] == 'has-session':
    sys.exit(int(os.environ.get('MISSING_SESSION', '0')))
if sys.argv[1] == 'display-message':
    print('$1')
if sys.argv[1] == 'new-session' and '-P' in sys.argv:
    print('$9')
''')
        fake_tmux.chmod(0o755)
        self.env['PATH'] = str(fake_bin) + os.pathsep + self.env['PATH']
        import json
        result = self.run_process([BASH, str(REPO / 'bin/tmx'), 'work space'])
        self.assert_success(result)
        calls = [json.loads(line) for line in (self.user_dir / 'tmux-calls').read_text().splitlines()]
        self.assertEqual(calls[0], ['has-session', '-t', '=work space'])
        self.assertEqual(calls[-2:], [['attach-session', '-t', '$9'], ['kill-session', '-t', '$9']])
        self.assertEqual(sum(call[0] == 'kill-session' for call in calls), 1)
        self.env['TMUX'] = 'existing-client'
        result = self.run_process([BASH, str(REPO / 'bin/tmx'), 'work'])
        self.assert_success(result)
        calls = [json.loads(line) for line in (self.user_dir / 'tmux-calls').read_text().splitlines()]
        self.assertEqual(calls[-1], ['switch-client', '-t', '=work'])

    @unittest.skipUnless(shutil.which("tmux"), "tmux is required")
    def test_tmux_config_loads(self):
        socket = str(self.user_dir / "tmux.sock")
        command = [shutil.which("tmux"), "-S", socket]
        try:
            result = self.run_process(command + ["-f", str(REPO / "tmux.conf"), "new-session", "-d", "-s", "test", "sleep 30"])
            self.assert_success(result)
            result = self.run_process(command + ["show-options", "-sv", "escape-time"])
            self.assert_success(result)
            self.assertEqual(result.stdout.strip(), "100")
        finally:
            self.run_process(command + ["kill-server"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
