#!/usr/bin/python

import sys
import os
import time

config_dir = os.path.expanduser('~') + '/.config/ssstatus/'

def print_help():
    print('Super Simple Status')
    print('usage: ssstatus [command]')
    print('')
    print('set "<your status>"  - set the body of your status, it will automatically be split into lines')
    print('setlength <length>   - set the maximum length of a status line (default 80 characters)')
    print('clear                - sets the status to an empty string')
    print('show                 - outputs the current status line (defualt line 1)')
    print('up                   - scrolls the current line down the status')
    print('down                 - scrolls the current line up the status')
    print('setup                - sets up ssstatus configuration at ~/.config/ssstatus (will overwrite current configuration)')

def clamp(value, smallest, largest):
    return max(smallest, min(value, largest))

def log(string):
    with open(config_dir + 'log', 'a') as log_file:
        log_file.write(string + '\n')

def import_config_int(name, default):
    value = default
    search = name + "="

    with open(config_dir + 'config', 'r') as config_file:
        config_text = config_file.read()

        if search in config_text:
            in_value = config_text[config_text.find(search)+len(search):].split()[0]
            try:
                in_value = int(in_value)
                value = in_value
            except ValueError:
                log('error in {} configuration, using default value'.format(name))
        else:
            log('{} configuration not found, using default value'.format(name))
    return value

def import_config_value(name, default):
    value = default
    search = name + "="

    with open(config_dir + 'config', 'r') as config_file:
        config_text = config_file.read()

        if search in config_text:
            value = config_text[config_text.find(search)+len(search):].split()[0]
        else:
            log('{} configuration not found, using default value'.format(name))
    return value

def export_config_values(**kwparams):
    with open(config_dir + 'config', 'r') as config_file:
        old_config = config_file.read()
    new_config = ''

    if 'max_length' in kwparams:
        new_config += "max_length={}\n".format(kwparams['max_length'])
    else:
        new_config += "max_length={}\n".format(import_config_value('max_length', '80'))
    
    if 'current_line' in kwparams:
        new_config += "current_line={}\n".format(kwparams['current_line'])
    else:
        new_config += "current_line={}\n".format(import_config_value('current_line', '1'))
    
    if 'total_lines' in kwparams:
        new_config += "total_lines={}\n".format(kwparams['total_lines'])
    else:
        new_config += "total_lines={}\n".format(import_config_value('total_lines', '1'))

    with open(config_dir + 'config', 'w') as config_file:
        config_file.write(new_config)

def import_status():
    with open(config_dir + 'status', 'r') as status_file:
        status_text = status_file.read()
    return status_text

def export_status(status):
    with open(config_dir + 'status', 'w') as status_file:
        status_file.write(status)

def setup():
    with open(config_dir + 'status', 'w+') as status_file:
        status_file.write('setup complete\n')
    with open(config_dir + 'config', 'w+') as config_file:
        config_file.write('max_length=80\ncurrent_line=1\ntotal_lines=1\n')
    with open(config_dir + 'log', 'w+') as log_file:
        log_file.write('log file created\n')

def format_status(unformatted, max_line_length):
    formatted=''
    next_append=''
    for line in filter(None, unformatted.split('\n')):
        words = line.split()
        word_count = len(words)
        for index, word in enumerate(words):
            next_append += (word + ' ')
            if (index+1 < word_count) and (len(next_append + words[index+1] + ' ') > max_line_length):
                formatted += (next_append + '\n').replace(' \n', '\n')
                next_append = ''      
        formatted += (next_append + '\n').replace(' \n', '\n')
        next_append = ''
    return formatted


def set_status(input_text, max_line_length):
    new_status = format_status(input_text, max_line_length)
    total_lines = len(new_status.split('\n'))-1
    current_line = 1

    export_status(new_status)
    export_config_values(current_line=current_line, total_lines=total_lines)


def print_status():
    current_line = import_config_int('current_line', 1)
    total_lines = import_config_int('total_lines', 1)
    status = import_status()
    if total_lines < 2:
        arrows = '      '
    elif current_line == 1:
        arrows = ' \\/   '
    elif current_line == total_lines:
        arrows = '    /\\'
    else:
        arrows = ' \\/ /\\'
    print(status.split('\n')[current_line-1] + arrows)

def set_max_length(new_length):
    max_length = clamp(new_length, 1, 10000)
    export_config_values(max_length=max_length)
    set_status(import_status(), max_length)

def set_current_line(new_current_line):
    total_lines = import_config_int('total_lines', 1)
    current_line = clamp(new_current_line, 1, total_lines)
    export_config_values(current_line=current_line)

def line_up():
    set_current_line(import_config_int('current_line', 1)-1)

def line_down():
    set_current_line(import_config_int('current_line', 1)+1)

if not os.path.exists(config_dir):
    os.makedirs(config_dir)
while os.path.isfile(config_dir + 'lock'):
    time.sleep(0.1)
lockfile = open(config_dir + 'lock', 'w+')
lockfile.close()

if len(sys.argv) > 2:
    if   sys.argv[1] == 'set':
        set_status(sys.argv[2], import_config_int('max_length', 80))
    elif sys.argv[1] == 'setlength':
        try:
            new_length = int(sys.argv[2])
            set_max_length(new_length)
        except ValueError:
            print('input must be an integer')
    else:
        print_help()
elif len(sys.argv) > 1:
    if   sys.argv[1] == 'clear':
        set_status('', 10)
    elif sys.argv[1] == 'show':
        print_status()
    elif sys.argv[1] == 'up':
        line_up()
    elif sys.argv[1] == 'down':
        line_down()
    elif sys.argv[1] == 'setup':
        setup()
    else:
        print_help()
else:
    print_help()

os.remove(config_dir + 'lock')
