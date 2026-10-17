setlocal expandtab tabstop=2 softtabstop=2 shiftwidth=2
let b:undo_ftplugin = get(b:, 'undo_ftplugin', '') . '|setlocal expandtab< tabstop< softtabstop< shiftwidth<'
