# FA Command List
Below is the list of available commands:
- [stop-if-empty](#stop-if-empty)
- [add](#add)
- [add-offset-range](#add-offset-range)
- [align](#align)
- [and](#and)
- [append](#append)
- [back](#back)
- [back-to-checkpoint](#back-to-checkpoint)
- [checkpoint](#checkpoint)
- [clear](#clear)
- [find](#find)
- [find-bytes](#find-bytes)
- [find-bytes-ida](#find-bytes-ida)
- [find-immediate](#find-immediate)
- [find-str](#find-str)
- [function-end](#function-end)
- [function-lines](#function-lines)
- [function-start](#function-start)
- [goto-ref](#goto-ref)
- [keystone-find-opcodes](#keystone-find-opcodes)
- [keystone-verify-opcodes](#keystone-verify-opcodes)
- [locate](#locate)
- [make-code](#make-code)
- [make-comment](#make-comment)
- [make-function](#make-function)
- [make-literal](#make-literal)
- [make-unknown](#make-unknown)
- [max-xrefs](#max-xrefs)
- [min-xrefs](#min-xrefs)
- [most-common](#most-common)
- [offset](#offset)
- [verify-operand](#verify-operand)
- [or](#or)
- [print](#print)
- [run](#run)
- [set-const](#set-const)
- [set-enum](#set-enum)
- [set-name](#set-name)
- [set-struct-member](#set-struct-member)
- [set-type](#set-type)
- [single](#single)
- [sort](#sort)
- [trace](#trace)
- [unique](#unique)
- [verify-aligned](#verify-aligned)
- [verify-bytes](#verify-bytes)
- [verify-name](#verify-name)
- [verify-ref](#verify-ref)
- [verify-segment](#verify-segment)
- [verify-single](#verify-single)
- [verify-str](#verify-str)
- [xref](#xref)
- [xrefs-to](#xrefs-to)
## stop-if-empty
```
builtin interpreter command. 
stops parsing current SIG if current resultset is empty
```
## add
```
usage: add [-h] value

add an hard-coded value into resultset

EXAMPLE:
    results = []
    -> add 80
    result = [80]

positional arguments:
  value

optional arguments:
  -h, --help  show this help message and exit
```
## add-offset-range
```
usage: add-offset-range [-h] start end step

adds a python-range to resultset

EXAMPLE:
    result = [0, 0x200]
    -> add-offset-range 0 4 8
    result = [0, 4, 8, 0x200, 0x204, 0x208]

positional arguments:
  start
  end
  step

optional arguments:
  -h, --help  show this help message and exit
```
## align
```
usage: align [-h] value

align results to given base (round-up)

EXAMPLE:
    results = [0, 2, 4, 6, 8]
    -> align 4
    results = [0, 4, 4, 8, 8]

positional arguments:
  value

optional arguments:
  -h, --help  show this help message and exit
```
## and
```
usage: and [-h] cmd [cmd ...]

intersect with another command's resultset

EXAMPLE:
    results = [80]
    -> and offset 0
    results = [80]

EXAMPLE #2:
    results = [80]
    -> and offset 1
    results = []

positional arguments:
  cmd         command

optional arguments:
  -h, --help  show this help message and exit
```
## append
```
usage: append [-h] cmd [cmd ...]

append results from another command

positional arguments:
  cmd         command

optional arguments:
  -h, --help  show this help message and exit
```
## back
```
usage: back [-h] amount

go back to previous result-set

EXAMPLE:
    find-bytes --or 01 02 03 04
    results = [0, 0x100, 0x200]

    find-bytes --or 05 06 07 08
    results = [0, 0x100, 0x200, 0x300, 0x400]

    -> back -3
    results = [0, 0x100, 0x200]

positional arguments:
  amount      amount of command results to go back by

optional arguments:
  -h, --help  show this help message and exit
```
## back-to-checkpoint
```
usage: back-to-checkpoint [-h] name

go back to previous result-set saved by 'checkpoint' command.

EXAMPLE:
    results = [0, 4, 8]
    checkpoint foo

    find-bytes --or 12345678
    results = [0, 4, 8, 10, 20]

    -> back-to-checkpoint foo
    results = [0, 4, 8]

positional arguments:
  name        name of checkpoint in history to go back to

optional arguments:
  -h, --help  show this help message and exit
```
## checkpoint
```
usage: checkpoint [-h] name

save current result-set as a checkpoint.
You can later restore the result-set using 'back-to-checkpoint'

EXAMPLE:
    results = [0, 4, 8]
    -> checkpoint foo

    find-bytes --or 12345678
    results = [0, 4, 8, 10, 20]

    back-to-checkpoint foo
    results = [0, 4, 8]

positional arguments:
  name        name of checkpoint to use

optional arguments:
  -h, --help  show this help message and exit
```
## clear
```
usage: clear [-h]

clears the current result-set

EXAMPLE:
    results = [0, 4, 8]
    -> clear
    results = []

optional arguments:
  -h, --help  show this help message and exit
```
## find
```
usage: find [-h] name

find another symbol defined in other SIG files

positional arguments:
  name        symbol name

optional arguments:
  -h, --help  show this help message and exit
```
## find-bytes
```
usage: find-bytes [-h] hex_str

expands the result-set with the occurrences of the given bytes

EXAMPLE:
    0x00000000: 01 02 03 04
    0x00000004: 05 06 07 08

    results = []
    -> find-bytes 01020304
    result = [0]

    -> find-bytes 05060708
    results = [0, 4]

positional arguments:
  hex_str

optional arguments:
  -h, --help  show this help message and exit
```
## find-bytes-ida
```
usage: find-bytes-ida [-h] expression

expands the result-set with the occurrences of the given bytes
expression in "ida bytes syntax"

EXAMPLE:
    0x00000000: 01 02 03 04
    0x00000004: 05 06 07 08

    results = []
    -> find-bytes-ida '01 02 03 04'
    result = [0]

    -> find-bytes-ida '05 06 ?? 08'
    results = [0, 4]

positional arguments:
  expression

optional arguments:
  -h, --help  show this help message and exit
```
## find-immediate
```
usage: find-immediate [-h] expression

expands the result-set with the occurrences of the given
immediate in "ida immediate syntax"

EXAMPLE:
    0x00000000: ldr r0, =0x1234
    0x00000004: add r0, #2 ; 0x1236

    results = []
    -> find-immediate 0x1236
    result = [4]

positional arguments:
  expression

optional arguments:
  -h, --help  show this help message and exit
```
## find-str
```
usage: find-str [-h] [--null-terminated] hex_str

expands the result-set with the occurrences of the given
string

EXAMPLE:
    0x00000000: 01 02 03 04
    0x00000004: 05 06 07 08
    0x00000008: 30 31 32 33 -> ASCII '0123'

    results = []
    -> find-str '0123'

    result = [8]

positional arguments:
  hex_str

optional arguments:
  -h, --help         show this help message and exit
  --null-terminated
```
## function-end
```
usage: function-end [-h]

goto function's end

EXAMPLE:
    0x00000000: push {r4-r7, lr} -> function's prolog
    ...
    0x000000f0: push {r4-r7, pc} -> function's epilog

    results = [0]
    -> function-end
    result = [0xf0]

optional arguments:
  -h, --help  show this help message and exit
```
## function-lines
```
usage: function-lines [-h] [--after]

get all function's lines

EXAMPLE:
    0x00000000: push {r4-r7, lr} -> function's prolog
    0x00000004: mov r1, r0
    ...
    0x000000c0: mov r0, r5
    ...
    0x000000f0: push {r4-r7, pc} -> function's epilog

    results = [0xc0]
    -> function-lines
    result = [0, 4, ..., 0xc0, ..., 0xf0]

optional arguments:
  -h, --help  show this help message and exit
  --after     include only function lines which occur after currentresultset
```
## function-start
```
usage: function-start [-h] [cmd [cmd ...]]

goto function's start

EXAMPLE:
    0x00000000: push {r4-r7, lr} -> function's prolog
    ...
    0x000000f0: pop {r4-r7, pc} -> function's epilog

    results = [0xf0]
    -> function-start
    result = [0]
    
EXAMPLE 2:
    0x00000000: push {r4-r7, lr} -> function's prolog
    ...
    0x000000f0: pop {r4-r7, pc} -> function's epilog

    results = []
    -> function-start arm-find-all 'pop {r4-r7, pc}'
    result = [0]

positional arguments:
  cmd         command

optional arguments:
  -h, --help  show this help message and exit
```
## goto-ref
```
usage: goto-ref [-h] [--code] [--data]

goto reference

EXAMPLE:
    0x00000000: ldr r0, =0x12345678

    results = [0]
    -> goto-ref --data
    results = [0x12345678]

optional arguments:
  -h, --help  show this help message and exit
  --code      include code references
  --data      include data references
```
## keystone-find-opcodes
```
usage: keystone-find-opcodes [-h] [--bele] [--or] arch mode code

use keystone to search for the supplied opcodes

EXAMPLE:
    0x00000000: push {r4-r7, lr}
    0x00000004: mov r0, r1

    results = []
    -> keystone-find-opcodes --bele KS_ARCH_ARM KS_MODE_ARM 'mov r0, r1;'
    result = [4]

positional arguments:
  arch        keystone architecture const (evaled)
  mode        keystone mode const (evald)
  code        keystone architecture const (opcodes to compile)

optional arguments:
  -h, --help  show this help message and exit
  --bele      figure out the endianity from IDA instead of explicit mode
  --or        mandatory. expands search results
```
## keystone-verify-opcodes
```
usage: keystone-verify-opcodes [-h] [--bele] [--until UNTIL] arch mode code

use keystone to verify the result-set matches the given
opcodes

EXAMPLE:
    0x00000000: push {r4-r7, lr}
    0x00000004: mov r0, r1

    results = [0, 4]
    -> keystone-verify-opcodes --bele KS_ARCH_ARM KS_MODE_ARM 'mov r0, r1'
    result = [4]

positional arguments:
  arch           keystone architecture const (evaled)
  mode           keystone mode const (evald)
  code           keystone architecture const (opcodes to compile)

optional arguments:
  -h, --help     show this help message and exit
  --bele         figure out the endianity from IDA instead of explicit mode
  --until UNTIL  keep going onwards opcode-opcode until verified
```
## locate
```
usage: locate [-h] name

goto symbol by name

EXAMPLE:
    0x00000000: main:
    0x00000000:     mov r0, r1
    0x00000004: foo:
    0x00000004:     bx lr

    results = [0, 4]
    -> locate foo
    result = [4]

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
```
## make-code
```
usage: make-code [-h]

convert into a code block

optional arguments:
  -h, --help  show this help message and exit
```
## make-comment
```
usage: make-comment [-h] comment

add comment for given addresses

EXAMPLE:
    0x00000200: 01 02 03 04
    0x00000204: 30 31 32 33

    results = [0x200]
    -> make-comment 'bla bla'
    results = [0x200]

    0x00000200: 01 02 03 04 ; bla bla
    0x00000204: 30 31 32 33

positional arguments:
  comment     comment string

optional arguments:
  -h, --help  show this help message and exit
```
## make-function
```
usage: make-function [-h]

convert into a function

optional arguments:
  -h, --help  show this help message and exit
```
## make-literal
```
usage: make-literal [-h]

convert into a literal

optional arguments:
  -h, --help  show this help message and exit
```
## make-unknown
```
usage: make-unknown [-h]

convert into an unknown block

optional arguments:
  -h, --help  show this help message and exit
```
## max-xrefs
```
usage: max-xrefs [-h]

get the result with most xrefs pointing at it

optional arguments:
  -h, --help  show this help message and exit
```
## min-xrefs
```
usage: min-xrefs [-h]

get the result with least xrefs pointing at it

optional arguments:
  -h, --help  show this help message and exit
```
## most-common
```
usage: most-common [-h]

get the result appearing the most in the result-set

EXAMPLE:
    results = [0, 4, 4, 8, 12]
    -> most-common
    result = [4]

optional arguments:
  -h, --help  show this help message and exit
```
## offset
```
usage: offset [-h] offset

advance the result-set by a given offset

EXAMPLE:
    results = [0, 4, 8, 12]
    -> offset 4
    result = [4, 8, 12, 16]

positional arguments:
  offset

optional arguments:
  -h, --help  show this help message and exit
```
## verify-operand
```
usage: verify-operand [-h] [--op0 OP0] [--op1 OP1] [--op2 OP2] name

reduce the result-set to those matching the given instruction

EXAMPLE #1:
    0x00000000: mov r0, r1
    0x00000004: mov r1, r2
    0x00000008: push {r4}

    results = [0, 2, 4, 6, 8]
    -> verify-operand mov
    results = [0, 4]

EXAMPLE #2:
    0x00000000: mov r0, r1
    0x00000004: mov r1, r2
    0x00000008: push {r4}

    results = [0, 2, 4, 6, 8]
    -> verify-operand mov --op1 2
    results = [4]

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
  --op0 OP0
  --op1 OP1
  --op2 OP2
```
## or
```
usage: or [-h] cmd [cmd ...]

unite with another command's resultset

EXAMPLE:
    results = [80]
    -> or offset 0
    results = [80]

EXAMPLE #2:
    results = [80]
    -> or offset 1
    results = [80, 81]

positional arguments:
  cmd         command

optional arguments:
  -h, --help  show this help message and exit
```
## print
```
usage: print [-h]

prints the current result-set (for debugging)

optional arguments:
  -h, --help  show this help message and exit
```
## run
```
usage: run [-h] name

run another SIG file

positional arguments:
  name        SIG filename

optional arguments:
  -h, --help  show this help message and exit
```
## set-const
```
usage: set-const [-h] name

define a const value

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
```
## set-enum
```
usage: set-enum [-h] enum_name enum_key

define an enum value

positional arguments:
  enum_name
  enum_key

optional arguments:
  -h, --help  show this help message and exit
```
## set-name
```
usage: set-name [-h] name

set symbol name

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
```
## set-struct-member
```
usage: set-struct-member [-h] struct_name member_name member_type

add a struct member

positional arguments:
  struct_name
  member_name
  member_type

optional arguments:
  -h, --help   show this help message and exit
```
## set-type
```
usage: set-type [-h] type_str

sets the type in the disassembler

positional arguments:
  type_str

optional arguments:
  -h, --help  show this help message and exit
```
## single
```
usage: single [-h] index

peek a single result from the result-set (zero-based)

EXAMPLE:
    results = [0, 4, 8, 12]
    -> single 2
    result = [8]

positional arguments:
  index       result index

optional arguments:
  -h, --help  show this help message and exit
```
## sort
```
usage: sort [-h]

performs a sort on the current result-set

EXAMPLE:
    results = [4, 12, 0, 8]
    -> sort
    result = [0, 4, 8 ,12]

optional arguments:
  -h, --help  show this help message and exit
```
## trace
```
usage: trace [-h]

sets a pdb breakpoint

optional arguments:
  -h, --help  show this help message and exit
```
## unique
```
usage: unique [-h]

make the resultset unique

EXAMPLE:
    results = [0, 4, 8, 8, 12]
    -> unique
    result = [0, 4, 8, 12]

optional arguments:
  -h, --help  show this help message and exit
```
## verify-aligned
```
usage: verify-aligned [-h] value

leave only results fitting required alignment

EXAMPLE:
    results = [0, 2, 4, 6, 8]
    -> verify-aligned 4
    results = [0, 4, 8]

positional arguments:
  value

optional arguments:
  -h, --help  show this help message and exit
```
## verify-bytes
```
usage: verify-bytes [-h] [--until UNTIL] hex_str

reduce the result-set to those matching the given bytes

EXAMPLE:
    0x00000000: 01 02 03 04
    0x00000004: 05 06 07 08

    results = [0, 2, 4, 6, 8]
    -> verify-bytes '05 06 07 08'
    results = [4]

positional arguments:
  hex_str

optional arguments:
  -h, --help     show this help message and exit
  --until UNTIL  keep advancing by a given size until a match
```
## verify-name
```
usage: verify-name [-h] name

verifies the given name appears in result set

positional arguments:
  name

optional arguments:
  -h, --help  show this help message and exit
```
## verify-ref
```
usage: verify-ref [-h] [--code] [--data] [--name NAME]

verifies a given reference exists to current result set

optional arguments:
  -h, --help   show this help message and exit
  --code       include code references
  --data       include data references
  --name NAME  symbol name
```
## verify-segment
```
usage: verify-segment [-h] name

reduce the result-set to those in the given segment name

EXAMPLE:
    .text:0x00000000 01 02 03 04
    .text:0x00000004 30 31 32 33

    .data:0x00000200 01 02 03 04
    .data:0x00000204 30 31 32 33

    results = [0, 0x200]
    -> verify-segment .data
    results = [0x200]

positional arguments:
  name        segment name

optional arguments:
  -h, --help  show this help message and exit
```
## verify-single
```
usage: verify-single [-h]

verifies the result-list contains a single value

EXAMPLE #1:
    results = [4, 12, 0, 8]
    -> unique
    result = []

EXAMPLE #2:
    results = [4]
    -> unique
    result = [4]

optional arguments:
  -h, --help  show this help message and exit
```
## verify-str
```
usage: verify-str [-h] [--until UNTIL] [--null-terminated] hex_str

reduce the result-set to those matching the given string

EXAMPLE:
    0x00000000: 01 02 03 04
    0x00000004: 30 31 32 33 -> ascii '0123'

    results = [0, 2, 4]
    -> verify-str '0123'
    results = [4]

positional arguments:
  hex_str

optional arguments:
  -h, --help         show this help message and exit
  --until UNTIL      keep advancing by a given size until a match
  --null-terminated
```
## xref
```
usage: xref [-h]

goto xrefs pointing at current search results

optional arguments:
  -h, --help  show this help message and exit
```
## xrefs-to
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
  --bytes BYTES     parameter as bytes
```
