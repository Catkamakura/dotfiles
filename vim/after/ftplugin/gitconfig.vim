setlocal noexpandtab tabstop=4 shiftwidth=4 softtabstop=0
let b:undo_ftplugin = get(b:, 'undo_ftplugin', '') . '|setlocal expandtab< tabstop< shiftwidth< softtabstop<'
