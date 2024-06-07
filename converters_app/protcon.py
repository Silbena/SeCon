import converters as conv

import os.path as path
import os

import io
import time


def log_strftime(t : time.struct_time):
    time_str = time.strftime("%H:%M:%S", t)
    return time_str


def log_info(msg : str):
    time_str = time.strftime("%H:%M:%S", time.localtime())
    print(f'[{time_str}][INFO] {msg}')


def log_error(msg : str):
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    time_str = time.strftime("%H:%M:%S",  time.localtime())
    print(f'{FAIL}[{time_str}][ERROR] {msg}{ENDC}')


def print_logs(file_name : str, ctx : conv.ConverterContext):
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    # print errors
    for entry in ctx.errors:
        location = f'{file_name}:{entry.line}'
        time_str = log_strftime(entry.time)

        err_str = f'[{time_str}][ERROR][{location}] {entry.msg}'
        print(f'{FAIL}{err_str}{ENDC}')

    # print warnings
    for entry in ctx.warnings:
        location = f'{file_name}:{entry.line}'
        time_str = log_strftime(entry.time)

        warn_str = f'[{time_str}][WARNING][{location}] {entry.msg}'     
        print(f'{WARNING}{warn_str}{ENDC}')


def convert_single_file(in_filename, out_filename):
    log_info(f'Converting {in_filename}->{out_filename}')

    out_buffer = io.StringIO()
    
    converter_key = conv.registry.getKey(in_filename, out_filename)
    
    converters = conv.registry.initRegistry()
    converter_class = converters[converter_key]
    if converter_class is None:
        log_error(f'Failed to find converter')
    
    converter_obj = converter_class()
    with open(in_filename, 'r') as f:
        ctx = conv.ConverterContext(out_buffer, f)
        converter_obj.convert(ctx)

    print_logs(in_filename, ctx)

    if len(ctx.errors) > 0:
        log_error(f'Failed with {len(ctx.errors)} error')
        return
        
    out_buffer.seek(0)
    
    with open(out_filename, 'w') as f:
        f.write(out_buffer.read())

def convert_directory(input_dir, output_dir, out_extension):
    if path.isdir(input_dir) == False:
        log_error('Input is not directory')
        return
    
    os.makedirs(output_dir, exist_ok=True)

    # pick converter
    conv_registry = conv.registry.initRegistry()

    files = os.listdir(input_dir)

    for file_name in files:
        out_path = os.path.join(output_dir, path.splitext(path.basename(file_name))[0] + out_extension)
        conv_key = conv.registry.getKey(file_name, out_path)
        converter_class = conv_registry[conv_key]
        
        if converter_class is None:
            log_error(f'Failed to find {out_extension} converter for {file_name}')

        input_path = path.join(input_dir, file_name)

        converter_instance = converter_class()
        
        with open(input_path, 'r') as f:
            ctx = conv.ConverterContext(io.StringIO(), f)
            converter_instance.convert(ctx)
        
        print_logs(input_path, ctx)
        if len(ctx.errors) > 0:
            continue # don't save to output file

        ctx.output.seek(0)

        with open(out_path, 'w') as f:
            f.write(ctx.output.read())
        


def main():
    convert_directory('input', 'output', '.tsv')

if __name__ == '__main__':
    main()