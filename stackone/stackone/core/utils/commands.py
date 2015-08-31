def get_cmd_copy_block_device_from_remote(node_username, node_address, source_file_path, source_disk_name):
    cmd = 'ssh ' + node_username + '@' + node_address + " 'dd if=" + source_file_path + " bs=4096k | gzip -c' | gzip -cd > " + source_disk_name
    return cmd

def get_cmd_copy_file_from_remote(node_username, node_address, file_dir, file_name):
    cmd = 'ssh ' + node_username + '@' + node_address + " 'cd " + file_dir + ' && tar -czSf - ' + file_name + "' | tar -xzf -"
    return cmd

def get_cmd_copy_spares_file_to_remote(node_username, node_address, src_filename, dest_dir):
    cmd = 'tar -cSzf - ' + src_filename + ' | ssh ' + node_username + '@' + node_address + " 'tar -xzf - -C " + dest_dir + "'"
    print '## cmd: ',
    print cmd
    return cmd

def get_cmd_dd(source_file_path, dest_file_path):
    cmd = 'dd if=' + source_file_path + ' bs=4096k of=' + dest_file_path
    return cmd

def get_cmd_cp(source_file_path, dest_file_path, options=None):
    if options is None:
        options = '-ar'
        #options = '-dr'
    cmd = 'cp ' + options + ' ' + source_file_path + ' ' + dest_file_path
    return cmd

def get_cmd_remove_dir(dir, options=None):
    if options is None:
        options = '-rf'
    cmd = 'rm ' + options + ' ' + dir
    return cmd

def get_cmd_kill_pid(pid, options=None):
    pid = str(pid)
    if options is None:
        options = '-9'
    cmd = 'kill ' + options + ' ' + pid
    return cmd

def get_cmd_kill_pid_file(pid_file, options=None):
    if options is None:
        options = '-9'
    cmd = 'kill ' + options + ' $(<' + pid_file + ')'
    return cmd

def get_cmd_move(source_file_path, dest_file_path, options=None):
    if options is None:
        options = ''
    cmd = 'mv ' + options + ' ' + source_file_path + ' ' + dest_file_path
    return cmd

