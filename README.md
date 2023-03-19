(This version is not complete)

# TeenyISC

Teeny.I.S.C or Teeny Instruction set computer is my own IA designed for
learning

The instruction set is as compact as possible
It consists of

- `jmp` `jz` `jc`
- `hlt` `nop`
- `add` `sub` `nand` `copy`
- `movx`
- `rloadrl` `rstorerl` `loadrl` `storerl`
- `rloadi` `loadi`

This implementation doesn't concern itself with the implementation of the IA as it would be physically for now

This project provides a simulation, assembler, disassembler. All 3 are
currently under development but are ready for use. However before using
you will have to put togather your simulation by assembling the components
in python (CLI and utilities in works).

## Architecture

Tisc has a very basic architecture which is not designed with real world
usage in mind.

### Registers
TISC is a register machine with 6 developer accessible register which are
further divided into 4 standard and 2 result registers.

|     | 0   | 1   |
| :-- | :-- | :-- |
| 00  | x   | y   |
| 01  | z   | w   |
| 10  | rl  | rh  |
| 11  | ipl | iph |

x's register code is `000`, y's is `001` and so on, the last two registers
can not be accessed.

x, y, z, w are standard registers, note how these registers can be
addressed using 2 bits only

### Pins

The TISC CPU defines a 16 bit address bus, a seperate 8 bit pin
and an extra `r` pin which maybe used as the 17th address bit or
as it was intended to be used, that is as a selector between ROM and RAM.
The `r` pin is directly controlled by the programmer by specifying the
`r` pin state in the IO instructions
At maximum, the first tisc version (this one) can only address 128 KiB
memory

### ALU

The Arithmetic and Logic unit is a small part with only 4 capabilities,
copying, adding, substractinga and nand-(ing).
ALU opcodes are
```json
{
    "add": 0,
    "sub": 1,
    "nand": 2,
    "copy": 3,
}
```

### Instructions

- #### jmp
  The `jmp` instruction has the following format
  `0000010 [offset LSB] [offset MSB]` it is a relative jump with the
  address being stored in little endian
- #### jz
  The `jz` instruction is written as `0001010 [offset LSB] [offset MSB]`
  It jumps only if the *last executed ALU* instruction resulted in a zero.
- #### jc
  Written as `0010010 [offset LSB] [offset MSB]` It jumps only if the
  *last executed ALU* instruction resulted in a carry/borrow
- #### hlt
  HALT stops the machine, written as `00001111`
- #### nop
  No operation, simply increment instruction pointer.
- #### add
  add two register contents and store the result in first register.
  `0100xxyy` `xx` is the 2 bit register code for the first register
  while `yy` is the register for the second register
- #### sub
  Subtract two register contents and store result in first register.
  Written as `0101xxyy`
- #### nand
  nand two register's content and store in first register. written as
  `0110xxyy`
- #### copy
  copy 2nd register's `yy` value into first register `xx`. Written as
  `01110000`
- #### movx
  Swap two register's contents. written as `10xxxyyyy` `xxx`, `yyy` are 2 3bit register codes for 2 registers invluding the result registers
- #### (r)loadrl
  `rloadrl` or `loadrl` loads the memory pointed to by the rl-rh
  register pair into the specified register. Written as `110xxx0r` `xxx` is the 3 bit register code, `r` is the `r` pin output.
- #### (r)storerl
  `rstorerl` or `storerl` stores the value in the specified register to
  the location described by rl-rh register pair. Written as `111xxx0r` `xxx` is the 3 bit register code, `r` is the `r` pin output.
- #### (r)loadi
  `rloadi` or `loadi`
  Loads the value from the instruction pointer, typically from program
  memory into the specified register. Written as `110xxx1r` `xxx` is the
  3 bit register code, `r` is the `r` pin output.

### TASM

TASM, TeenyASM is a lightweight extremely primitive assembly for TISC.
Syntax will be documented here *soon*

### DISTASM

DISTASM is the disassebler for compiler TASM memory files, currently it
gives only a rudimentary output

### tasmc.bitfield

This is a submodule specific to Tasm, it simplifies packing of bits into python integers

## License

This software is released free of charge without any warranties or
guaranties. The author reserves all rights. (For now)