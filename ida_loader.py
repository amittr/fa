import subprocess
import binascii
import tempfile
import sys
import os

import hjson
import click

import ida_kernwin
import ida_bytes
import ida_name
import idautils
import ida_pro
import idaapi
import idc

from fa import fainterp

TEMP_SIG_FILENAME = os.path.join(tempfile.gettempdir(), 'fa_tmp_sig.sig')
IS_BE = '>' if idaapi.get_inf_structure().is_be() else '<'


def open_file(filename):
    if sys.platform == "win32":
        try:
            os.startfile(filename)
        except Exception as error_code:
            if error_code[0] == 1155:
                os.spawnl(os.P_NOWAIT,
                          os.path.join(os.environ['WINDIR'],
                                       'system32', 'Rundll32.exe'),
                          'Rundll32.exe SHELL32.DLL, OpenAs_RunDLL {}'
                          .format(filename))
            else:
                print("other error")
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


class StringParsingException(Exception):
    pass


class String(object):
    ASCSTR = ["C",
              "Pascal",
              "LEN2",
              "Unicode",
              "LEN4",
              "ULEN2",
              "ULEN4"]

    def __init__(self, xref, addr):
        type_ = idc.get_str_type(addr)
        if type_ < 0 or type_ >= len(String.ASCSTR):
            raise StringParsingException()

        string = str(ida_bytes.get_strlit_contents(addr, 0xffff, type_))

        self.xref = xref
        self.addr = addr
        self.type = type_
        self.string = string

    def get_bytes_for_find(self):
        retval = ''
        if self.ASCSTR[self.type] == 'C':
            for c in self.string + '\x00':
                retval += '{:02x} '.format(ord(c))
        else:
            raise Exception("not yet supported string")
        return retval


def create_signature_ppc32(start, end, inf, verify=True):
    signature = []
    opcode_size = 4
    first = True

    command = 'find-bytes --or' if not verify else 'verify-bytes'

    for ea in range(start, end, opcode_size):
        mnemonic = idc.print_insn_mnem(ea)
        if mnemonic in ('lis', 'lwz', 'bl') or mnemonic.startswith('b'):
            pass
        else:
            b = binascii.hexlify(idc.get_bytes(ea, opcode_size))
            signature.append('{} {}'.format(command, b))
            if first:
                first = False
                command = 'verify-bytes'

        signature.append('offset {}'.format(opcode_size))

    signature.append('offset {}'.format(start - end))

    return signature


def create_signature_arm(start, end, inf, verify=True):
    """
    Create a signature for ARM processors.
    :param int start: Function's start address.
    :param int end: Function's end address.
    :param inf: IDA info object.
    :param bool verify: True of only verification required.
    False if searching is required too.
    :return: Signature steps to validate the function
    :rtype: list
    """
    instructions = []
    ea = start
    while ea < end:
        mnemonic = idc.print_insn_mnem(ea)
        opcode_size = idautils.DecodeInstruction(ea).size
        # Skip memory accesses and branches.
        if mnemonic not in \
                ('LDR', 'STR', 'BL', 'B', 'BLX', 'BX', 'BXJ'):
            command = 'find-bytes --or' \
                if not verify and ea == start else 'verify-bytes'
            instructions.append('{} {}'.format(
                command,
                binascii.hexlify(idc.get_bytes(ea, opcode_size)))
            )
        ea += opcode_size
        instructions.append('offset {}'.format(opcode_size))

    instructions.append('offset {}'.format(start - end))
    return instructions


SIGNATURE_CREATION_BY_ARCH = {
    'PPC': create_signature_ppc32,
    'ARM': create_signature_arm,
}


def find_function_strings(func_ea):
    end_ea = idc.find_func_end(func_ea)
    if end_ea == idaapi.BADADDR:
        return []

    strings = []
    for line in idautils.Heads(func_ea, end_ea):
        refs = idautils.DataRefsFrom(line)
        for ref in refs:
            try:
                strings.append(String(line, ref))
            except StringParsingException:
                continue

    return strings


def find_function_code_references(func_ea):
    end_ea = idc.find_func_end(func_ea)
    if end_ea == idaapi.BADADDR:
        return []

    results = []
    for line in idautils.Heads(func_ea, end_ea):
        refs = list(idautils.CodeRefsFrom(line, 1))
        if len(refs) > 1:
            results.append(refs[1])

    return results


class IdaLoader(fainterp.FaInterp):
    def __init__(self):
        super(IdaLoader, self).__init__()

    def create_symbol(self):
        """
        Create a temporary symbol signature from the current function on the
        IDA screen.
        """
        self.log('creating temporary signature')
        func_start = idc.get_func_attr(idc.get_screen_ea(), idc.FUNCATTR_START)
        func_end = idc.get_func_attr(idc.get_screen_ea(), idc.FUNCATTR_END)

        signature = {
            'name': idc.get_func_name(idc.get_screen_ea()),
            'type': 'function',
            'instructions': []
        }

        # first try adding references to strings
        strings = find_function_strings(func_start)
        code_references = find_function_code_references(func_start)

        strings_addr_set = set()
        code_references_set = set()

        for s in strings:
            if s.addr not in strings_addr_set:
                # link each string ref only once
                strings_addr_set.add(s.addr)
                signature['instructions'].append(
                    'xrefs-to --or --function-start '
                    '--bytes "{}"'.format(s.get_bytes_for_find())
                )

        for ea in code_references:
            name = idc.get_name(ea, ida_name.GN_VISIBLE)
            if (name != idc.BADADDR) and \
                    not (name.startswith('loc_')) and \
                    not (name.startswith('sub_')) and \
                    (ea not in code_references_set):
                # link each string ref only once
                code_references_set.add(ea)
                signature['instructions'].append(
                    'xrefs-to --or --function-start '
                    '--name "{}"'.format(name)
                )

        inf = idaapi.get_inf_structure()
        proc_name = inf.procName

        if proc_name not in SIGNATURE_CREATION_BY_ARCH:
            if len(signature) == 0:
                self.log('failed to create signature')
                return

        signature['instructions'] += SIGNATURE_CREATION_BY_ARCH[proc_name](
            func_start, func_end, inf, verify=len(signature) != 0
        )

        with open(TEMP_SIG_FILENAME, 'w') as f:
            hjson.dump(signature, f, indent=4)

        self.log('Signature created at {}'.format(TEMP_SIG_FILENAME))
        return TEMP_SIG_FILENAME

    def extended_create_symbol(self):
        filename = self.create_symbol()
        open_file(filename)

    def find_symbol(self):
        """
        Find the last create symbol signature.
        :return:
        """

        with open(TEMP_SIG_FILENAME) as f:
            sig = hjson.load(f)

        results = self.find_from_sig_json(sig, decremental=True)

        for address in results:
            self.log('Search result: 0x{:x}'.format(address))
        self.log('Search done')

        if len(results) == 1:
            # if remote sig has a proper name, but current one is not
            if not sig['name'].startswith('sub_') and \
                    idc.get_func_name(results[0]).startswith('sub_'):
                if ida_kernwin.ask_yn(1, 'Only one result has been found. '
                                         'Rename?') == 1:
                    idc.set_name(results[0], str(sig['name']), idc.SN_CHECK)

    def prompt_save_signature(self):
        with open(TEMP_SIG_FILENAME) as f:
            sig = hjson.load(f)

        if ida_kernwin.ask_yn(1, 'Are you sure you want '
                                 'to save this signature?') != 1:
            return

        self.save_signature(sig)

    @staticmethod
    def extract_all_user_names(filename=None):
        output = ''

        for ea, name in idautils.Names():
            if '_' in name:
                if name.split('_')[0] in ('def', 'sub', 'loc', 'jpt'):
                    continue
            flags = ida_bytes.get_full_flags(ea)
            if idc.hasUserName(flags):
                output += '{} = 0x{:08x};\n'.format(name, ea)

        print(output)

        if filename is not None:
            with open(filename, 'w') as f:
                f.write(output)

    def symbols(self, output_file_path=None):
        super(IdaLoader, self).symbols(output_file_path=output_file_path)
        IdaLoader.extract_all_user_names(output_file_path)

    def set_input(self, input_):
        self._endianity = '>' if idaapi.get_inf_structure().is_be() else '<'
        self._input = input_
        self.reload_segments()

    def reload_segments(self):
        # memory searches will use IDA's API instead
        # which is much faster
        return


fa_instance = None


@click.command()
@click.argument('signatures_root', default='.')
@click.argument('project_name', default='test-project-ida')
@click.option('--symbols-file', default=None)
def main(signatures_root, project_name, symbols_file=None):
    global fa_instance

    IdaLoader.log('''
    ---------------------------------
    FA Loaded successfully

    Quick usage:
    fa_instance.set_project(project_name) # select project name
    print(fa_instance.list_projects()) # prints available projects
    print(fa_instance.find(symbol_name)) # searches for the specific symbol
    fa_instance.symbols() # searches for the symbols in the current project

    HotKeys:
    Ctrl-6: Set current project
    Ctrl-7: Search project symbols
    Ctrl-8: Create temporary signature
    Ctrl-Shift-8: Create temporary signature and open an editor
    Ctrl-9: Find temporary signature
    Ctrl-0: Prompt for adding a new permanent signature
    ---------------------------------''')
    fa_instance = IdaLoader()
    fa_instance.set_input('ida')
    fa_instance.set_signatures_root(signatures_root)
    fa_instance.set_project(project_name)

    idaapi.add_hotkey('Ctrl-6', fa_instance.interactive_set_project)
    idaapi.add_hotkey('Ctrl-7', fa_instance.symbols)
    idaapi.add_hotkey('Ctrl-8', fa_instance.create_symbol)
    idaapi.add_hotkey('Ctrl-Shift-8', fa_instance.extended_create_symbol)
    idaapi.add_hotkey('Ctrl-9', fa_instance.find_symbol)
    idaapi.add_hotkey('Ctrl-0', fa_instance.prompt_save_signature)

    if symbols_file is not None:
        fa_instance.set_signatures_root('')
        fa_instance.symbols(symbols_file)
        ida_pro.qexit(0)


if __name__ == '__main__':
    main(standalone_mode=False, args=idc.ARGV[1:])
