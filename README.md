# FA

## What is it?

FA stands for Firmware Analysis.
FA allows one to easily perform code exploration, symbol finding and 
other functionality with ease.

## Requirements

Supported IDA 7.x.

In your IDA's python directory, install:
* [keystone](http://www.keystone-engine.org/download/)
* capstone (`pip install capstone`)
* click (`pip install click`)
* hjson (`pip install hjson`)

For Testing:
* pytest
* idalink

## I wanna start using, but where do I start?

Before using, one must understand the terminology for: 
Projects, SIG files and Loaders.

So, grab a cup of coffee, listen to some [nice music](https://www.youtube.com/watch?v=5rrIx7yrxwQ), and please devote 
a few minutes of your time to reading this README.

### Projects

The "project" is kind of the namespace for different signatures.
For example, either: linux, linux_x86, linux_arm etc... are good 
project names that can be specified if you are working on either 
platforms. 

By dividing the signatures into such projects, Windows symbols for 
example won't be searched for Linux projects, which will result 
in a better directory organization layout, better performance and
less rate for false-positives. 

The signatures are located by default in the `signatures` directory.
If one wishes to use a different location, you may create `config.ini`
at FA's root with the following contents:

```ini
[global]
signatures_root = /a/b/c
```

### SIG format

The SIG format is a core feature of FA regarding symbol searching. Each
SIG file is residing within the project directory and is automatically search
when requested to generate the project's symbol list.

The format is Hjson based and is used to describe the algorithms for 
different symbols.
The algorithms are preformed *very linearly*, line by line, 
whereas each line can either extend or reduce the possible search
results.

Each line behaves like a shell command-line that gets the 
previous results as the input and outputs the next results
to the next line.

SIG syntax (single):
```hjson
{
    type: function/global/number
    name: name
    instructions : [
        # Available commands are listed below
        command1
        command2
    ]
}
```

User may also use his own python script files to perform 
the search. Just create a new `.py` file in your project 
directory and implement the `run(**kwargs)` method. Also, the project's
path is appended to python's `sys.path` so you may import
different your scripts from one another.

To view the list of available commands, [view the list below](#available-commands)

### Examples

#### Finding a global struct

```hjson
{
    type: global,
    name: g_awsome_global,
    instructions: [
            # find the byte sequence '11 22 33 44'
            find-bytes --or '11 22 33 44'

            # advance offset by 20
            offset 20

            # verify the current bytes are 'aa bb cc dd'
            verify-bytes 'aa bb cc dd'

            # go back by 20 bytes offset
            offset -20

            # set global name
            set-name g_awsome_global
	]
}
```

#### Find function by reference to string

```hjson
{
    type: function
    name: free
    instructions: [
            # search the string "free"
            find-str --or 'free' --null-terminated

            # goto xref
            xref

            # goto function's prolog
            function-start

            # reduce to the singletone with most xrefs to
            max-xrefs

            # set name and type
            set-name free
            set-type 'void free(void *block)'
	]
}
```

#### Finding several functions in a row

```hjson
{
    type: function
    name: cool_functions
    instructions: [
            # find string
            find-str --or 'init_stuff' --null-terminated

            # goto to xref
            xref
    
            # goto function start
            function-start

            # verify only one single result
            unique

            # iterating every 4-byte opcode            
            add-offset-range 0 80 4

            # if mnemonic is bl
            verify-operand bl

            # sort results
            sort

            # set first bl to malloc function
            single 0
            goto-ref --code 
            set-name malloc
            set-type 'void *malloc(unsigned int size)'

            # go back to the results from 4 commands ago 
            # (the sort results)
            back 4

            # rename next symbol :)
            single 1
            goto-ref --code
            set-name free
            set-type 'void free(void *block)'
	]
}
```

#### Python script to find a list of symbols

```python
from fa.commands.find_str import find_str 
from fa.commands.set_name import set_name
from fa.commands import utils

def run(**kwargs):
    # throw an exception if not running within ida context
    utils.verify_ida()

    # locate the global string
    results = find_str('hello world', null_terminated=True)
    if len(results) != 1:
        # no results
        return {}
    
    # set symbol name in idb
    set_name(results[0], 'g_hello_world_string')
    
    # return a dictionary of the found symbols
    return {'g_hello_world_string': results[0]}
```

#### Python script to automate SIG files interpretor

```python
TEMPLATE = '''
find-str '{unique_string}'
xref
function-start
unique
set-name '{function_name}'
'''

def run(**kwargs):
    results = {}
    interp = kwargs['interpretor']

    for function_name in ['func1', 'func2', 'func3']:
        instructions = TEMPLATE.format(unique_string=function_name, 
                                       function_name=function_name).split('\n')
        
        results[function_name] = interp.find_from_instructions_list(instructions)

    return results
```

#### Python script to set struct

```python
from fa.commands.set_type import set_type
from fa.commands import utils

TEMPLATE = '''
find-str '{unique_string}'
xref
'''

def run(**kwargs):
    interp = kwargs['interpretor']

    utils.add_const('CONST7', 7)
    utils.add_const('CONST8', 8)

    foo_e = utils.FaEnum('foo_e')
    foo_e.add_value('val2', 2)
    foo_e.add_value('val1', 1)
    foo_e.update_idb()

    special_struct_t = utils.FaStruct('special_struct_t')
    special_struct_t.add_field('member1', 'const char *', size=4)
    special_struct_t.add_field('member2', 'const char *', size=4, offset=0x20)
    special_struct_t.update_idb()

    for function_name in ['unique_magic1', 'unique_magic2']:
        instructions = TEMPLATE.format(unique_string=function_name, 
                                       function_name=function_name).split('\n')
        
        results = interp.find_from_instructions_list(instructions)
        for ea in results:
            # the set_type can receive either a string, FaStruct
            # or FaEnum :-)
            set_type(ea, special_struct_t)

    return {}
```

### Aliases

Each command can be "alias"ed using the file 
found in `fa/commands/alias` or in `<project_root>/alias`

Syntax for each line is as follows: `alias_command = command`
For example:
```
ppc32-verify = keystone-verify-opcodes --bele KS_ARCH_PPC KS_MODE_PPC32
```

Project aliases have higher priority.

### Loaders

Loaders are the entry point into running FA. Currently only IDA loader exists, 
but in the future we'll possibly add Ghidra and other tools.

#### IDA

Go to: `File->Script File... (ALT+F7)` and select `ida_loader.py`.

You should get a nice prompt inside the output window welcoming you
into using FA. Also, a quick usage guide will also be printed so you 
don't have to memorize everything.

A QuickStart Tip:

`Ctrl+6` to select your project, then `Ctrl+7` to find all its defined symbols.


You can also run IDA in script mode just to extract symbols using:

```sh
ida -S"ida_loader.py <project-name> --symbols-file=/tmp/symbols.txt" foo.idb
```



### Available commands

#### back

```
usage: back amount

goes back in history of search results to those returned
from a previous command

positional arguments:
  amount    amount of command results to go back by
```

#### add-offset-range
```
usage: add-offset-range [-h] start end step

adds a python-range of offsets, to the current search results

positional arguments:
  start
  end
  step

optional arguments:
  -h, --help  show this help message and exit
```

#### aligned
```
usage: aligned [-h] value

reduces the list to only those aligned to a specific value

positional arguments:
  value

optional arguments:
  -h, --help  show this help message and exit
```

#### clear
```
usage: clear [-h]

clears the current search results

optional arguments:
  -h, --help  show this help message and exit
```

#### find-bytes
```
usage: find-bytes [-h] [--or] hex_str

expands the search results by the given bytes set

positional arguments:
  hex_str

optional arguments:
  -h, --help  show this help message and exit
  --or
```

#### find-bytes-ida
```
usage: find-bytes-ida [-h] [--or] expression

expands the search results by an ida-bytes expression (Alt+B)

positional arguments:
  expression

optional arguments:
  -h, --help  show this help message and exit
  --or
```

#### find-str
```
usage: find-str [-h] [--or] [--null-terminated] hex_str

expands the search results by the given string

positional arguments:
  hex_str

optional arguments:
  -h, --help         show this help message and exit
  --or
  --null-terminated
```

#### function-end
```
usage: function-end [-h] [--not-unique]

goto function's end

optional arguments:
  -h, --help    show this help message and exit
  --not-unique
```

#### function-lines
```
usage: function-lines [-h]

get all function lines

optional arguments:
  -h, --help  show this help message and exit
```

#### function-start
```
usage: function-start [-h] [--not-unique]

goto function's prolog

optional arguments:
  -h, --help    show this help message and exit
  --not-unique
```

#### goto-ref
```
usage: goto-ref [-h] [--code] [--data]

goto reference

optional arguments:
  -h, --help  show this help message and exit
  --code      include code references
  --data      include data references
```

keystone-engine module not installed
#### keystone-find-opcodes
```
usage: keystone-find-opcodes [-h] [--bele] [--or] arch mode code

use keystone to search for the supplied opcodes

positional arguments:
  arch        keystone architecture const (evaled)
  mode        keystone mode const (evald)
  code        keystone architecture const (opcodes to compile)

optional arguments:
  -h, --help  show this help message and exit
  --bele      figure out the endianity from IDA instead of explicit mode
  --or        mandatory. expands search results
```

keystone-engine module not installed
#### keystone-verify-opcodes
```
usage: keystone-verify-opcodes [-h] [--bele] [--until UNTIL] arch mode code

use keystone-engine to verify the given results match the supplied code

positional arguments:
  arch           keystone architecture const (evaled)
  mode           keystone mode const (evald)
  code           keystone architecture const (opcodes to compile)

optional arguments:
  -h, --help     show this help message and exit
  --bele         figure out the endianity from IDA instead of explicit mode
  --until UNTIL  keep going onwards opcode-opcode until verified
```

#### locate
```
usage: locate [-h] name

goto label by name

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
```

#### max-xrefs
```
usage: max-xrefs [-h]

get the result with most xrefs pointing at it

optional arguments:
  -h, --help  show this help message and exit
```

#### most-common
```
usage: most-common [-h]

get the result appearing the most in the result-set

optional arguments:
  -h, --help  show this help message and exit
```

#### name-literal
```
usage: name-literal [-h]

convert into a literal

optional arguments:
  -h, --help  show this help message and exit
```

#### offset
```
usage: offset [-h] offset

advance by a given offset

positional arguments:
  offset

optional arguments:
  -h, --help  show this help message and exit
```

#### print
```
usage: print [-h]

prints the current search results

optional arguments:
  -h, --help  show this help message and exit
```

#### set-name
```
usage: set-name [-h] name

set name in disassembler

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
```

#### set-type
```
usage: set-type [-h] type_str

sets the type in the disassembler

positional arguments:
  type_str

optional arguments:
  -h, --help  show this help message and exit
```

#### single
```
usage: single [-h] index

reduces the result list into a singleton

positional arguments:
  index       get item by an index

optional arguments:
  -h, --help  show this help message and exit
```

#### sort
```
usage: sort [-h]

performs a python-sort on the current result list

optional arguments:
  -h, --help  show this help message and exit
```

#### trace
```
usage: trace [-h]

sets a pdb breakpoint

optional arguments:
  -h, --help  show this help message and exit
```

#### unique
```
usage: unique [-h]

verifies the result-list contains a single value

optional arguments:
  -h, --help  show this help message and exit
```

#### verify-bytes
```
usage: verify-bytes [-h] [--until UNTIL] hex_str

reduces the search list to those matching the given bytes

positional arguments:
  hex_str

optional arguments:
  -h, --help     show this help message and exit
  --until UNTIL  keep advancing by a given size until a match
```

#### verify-name
```
usage: verify-name [-h] name

verifies the given name appears in result set

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
```

#### verify-operand
```
usage: verify-operand [-h] [--op0 OP0] [--op1 OP1] [--op2 OP2] name

verifies the given opcode's operands

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
  --op0 OP0
  --op1 OP1
  --op2 OP2
```

#### verify-ref
```
usage: verify-ref [-h] [--code] [--data] name

verifies a given reference exists to current result set

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
  --code      include code references
  --data      include data references
```

#### verify-str
```
usage: verify-str [-h] [--until UNTIL] [--null-terminated] hex_str

reduces the search list to those matching the given string

positional arguments:
  hex_str

optional arguments:
  -h, --help         show this help message and exit
  --until UNTIL      keep advancing by a given size until a match
  --null-terminated
```

#### xref
```
usage: xref [-h]

goto xrefs pointing at current search results

optional arguments:
  -h, --help  show this help message and exit
```

#### xrefs-to
```
usage: xrefs-to [-h] [--function-start] [--or] [--and] [--name NAME]
                [--bytes BYTES]

search for xrefs pointing at given parameter

optional arguments:
  -h, --help        show this help message and exit
  --function-start  goto function prolog for each xref
  --or              expand the current result set
  --and             reduce the current result set
  --name NAME       parameter as label name
  --bytes BYTES     parameter as bytesv
```
