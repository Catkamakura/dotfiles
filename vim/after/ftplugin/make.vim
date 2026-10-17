setlocal noexpandtab tabstop=8 shiftwidth=8 softtabstop=0
let b:undo_ftplugin = get(b:, 'undo_ftplugin', '') . '|setlocal expandtab< tabstop< shiftwidth< softtabstop<'
