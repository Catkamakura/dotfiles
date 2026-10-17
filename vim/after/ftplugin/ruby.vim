setlocal expandtab tabstop=2 shiftwidth=2 softtabstop=2 autoindent
let b:undo_ftplugin = get(b:, 'undo_ftplugin', '') . '|setlocal expandtab< tabstop< shiftwidth< softtabstop< autoindent<'
