-- Neovim 0.11+. Built-in features keep this usable on fresh SSH hosts.
vim.g.mapleader = "\\"
vim.g.maplocalleader = "\\"

local opt = vim.opt
opt.number = true
opt.relativenumber = true
opt.cursorline = true
opt.showmode = false
opt.laststatus = 3
opt.signcolumn = "yes"
opt.termguicolors = true
opt.background = "dark"
opt.scrolloff = 5
opt.sidescrolloff = 5
opt.linebreak = true
opt.listchars = { tab = ">>", nbsp = "~" }
opt.expandtab = true
opt.tabstop = 4
opt.shiftwidth = 4
opt.softtabstop = 4
opt.ignorecase = true
opt.smartcase = true
opt.incsearch = true
opt.hlsearch = true
opt.splitbelow = true
opt.splitright = true
opt.mouse = "a"
opt.undofile = true
opt.history = 8192
opt.timeoutlen = 1000
opt.ttimeoutlen = 100
opt.completeopt = { "menu", "menuone", "noselect" }
opt.wildmode = "longest:full,full"
opt.shortmess:append("I")
opt.joinspaces = false
vim.cmd.colorscheme("habamax")

-- Use the system clipboard where a provider is available. SSH hosts without a
-- provider keep normal registers without startup errors.
if vim.fn.has("clipboard") == 1 then
  opt.clipboard = "unnamedplus"
end
if vim.fn.executable("rg") == 1 then
  opt.grepprg = "rg --vimgrep --smart-case"
  opt.grepformat = "%f:%l:%c:%m"
end

local map = vim.keymap.set
map("n", "Q", "<Nop>")
map("n", "<C-j>", "<C-w>j", { desc = "Move to lower window" })
map("n", "<C-k>", "<C-w>k", { desc = "Move to upper window" })
map("n", "<C-h>", "<C-w>h", { desc = "Move to left window" })
map("n", "<C-l>", "<C-w>l", { desc = "Move to right window" })
map("n", "<C-n>", function()
  vim.wo.relativenumber = not vim.wo.relativenumber
end, { desc = "Toggle relative line numbers" })
map("n", "<Esc>", "<Cmd>nohlsearch<CR>", { desc = "Clear search highlight" })
map("n", "<leader>n", "<Cmd>Lexplore<CR>", { desc = "Toggle file browser" })
map("n", "<leader>f", "<Cmd>Explore<CR>", { desc = "Browse current file's directory" })
map("n", "<leader>b", "<Cmd>ls<CR>:buffer ", { desc = "Switch buffer" })
map("n", ";", "<Cmd>ls<CR>:buffer ", { desc = "Switch buffer" })
map("n", "<leader>u", "<Cmd>undolist<CR>", { desc = "Show undo history" })
map("n", "<leader>d", function()
  vim.b.movement_by_display_lines = not vim.b.movement_by_display_lines
end, { desc = "Toggle movement by display lines" })
for _, key in ipairs({ "j", "k", "0", "$" }) do
  map({ "n", "x" }, key, function()
    if vim.b.movement_by_display_lines and vim.v.count == 0 then
      return "g" .. key
    end
    return key
  end, { expr = true })
end

vim.g.netrw_banner = 0
vim.g.netrw_liststyle = 3
vim.g.netrw_winsize = 25

local group = vim.api.nvim_create_augroup("Dotfiles", { clear = true })
vim.api.nvim_create_autocmd({ "VimEnter", "WinEnter", "BufWinEnter" }, {
  group = group,
  callback = function()
    vim.wo.cursorline = true
  end,
})
vim.api.nvim_create_autocmd("WinLeave", {
  group = group,
  callback = function()
    vim.wo.cursorline = false
  end,
})

-- Filetype settings are buffer-local; opening YAML must not change Go/Make.
vim.api.nvim_create_autocmd("FileType", {
  group = group,
  pattern = { "lua", "javascript", "javascriptreact", "typescript", "typescriptreact", "json", "yaml", "ruby", "scala", "gitolite" },
  callback = function()
    vim.bo.expandtab = true
    vim.bo.tabstop = 2
    vim.bo.shiftwidth = 2
    vim.bo.softtabstop = 2
  end,
})
vim.api.nvim_create_autocmd("FileType", {
  group = group,
  pattern = { "go", "make", "gitconfig" },
  callback = function(event)
    local width = event.match == "gitconfig" and 4 or 8
    vim.bo.expandtab = false
    vim.bo.tabstop = width
    vim.bo.shiftwidth = width
    vim.bo.softtabstop = 0
  end,
})
local spell_filetypes = { gitcommit = true, hgcommit = true, markdown = true, text = true, tex = true, plaintex = true }
vim.api.nvim_create_autocmd("FileType", {
  group = group,
  callback = function(event)
    vim.opt_local.spell = spell_filetypes[event.match] == true
  end,
})
vim.filetype.add({ filename = { Makefrag = "make" } })

-- Use bundled/locally installed parsers; unsupported filetypes keep syntax
-- highlighting. Language servers can be enabled in the local config below.
vim.api.nvim_create_autocmd("FileType", {
  group = group,
  callback = function(event)
    pcall(vim.treesitter.start, event.buf)
  end,
})
vim.diagnostic.config({ severity_sort = true, float = { border = "rounded" } })
vim.api.nvim_create_autocmd("LspAttach", {
  group = group,
  callback = function(event)
    local client = vim.lsp.get_client_by_id(event.data.client_id)
    if client and client:supports_method("textDocument/completion") then
      vim.lsp.completion.enable(true, client.id, event.buf, { autotrigger = true })
    end
  end,
})

-- Machine-local plugins, language servers, and overrides.
local local_config = vim.fn.expand("~/.nvim_local.lua")
if vim.fn.filereadable(local_config) == 1 then
  dofile(local_config)
end
