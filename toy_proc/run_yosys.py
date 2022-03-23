#!/usr/bin/env python3
# helper tool to run yosys, generating appropriate yosys script
# python, rather than bash, since commandline arguments etc
# so much more convenenient in python
import argparse
import os
from collections import deque


def run(args):
    with open('build/yosys.tcl', 'w') as f:
        for file in args.in_verilog:
            f.write(f"read_verilog -sv {file}\n")
        if not os.path.exists('build/netlist'):
            os.makedirs('build/netlist')
        if args.top_module:
            f.write(f'hierarchy -top {args.top_module}')
        f.write(f"""
delete t:$assert
write_verilog build/netlist/0.v
flatten
write_verilog build/netlist/1.v
synth
write_verilog build/netlist/2.v
techmap;
write_verilog build/netlist/3.v
# ltp
dfflibmap -liberty {args.cell_lib}
write_verilog build/netlist/4.v
abc -liberty {args.cell_lib}
""")
        if not args.no_cells:
            f.write("""
write_verilog build/netlist/5.v
clean
write_verilog build/netlist/6.v
""")
        f.write("""
write_rtlil build/rtlil.rtl
write_verilog build/netlist.v
ltp
sta
stat
""")
        if args.show:
            f.write('show\n')
    if os.system('yosys -s build/yosys.tcl') != 0:
        raise Exception("Failed")
    # os.system('subl build/rtlil.rtl')
    # os.system('subl build/netlist.v')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-verilog', type=str, nargs='+', required=True, help='path to verilog file')
    parser.add_argument(
        '--top-module', type=str, help='top module name, only needed if more than one module.')
    parser.add_argument('--show', action='store_true', help='show xdot on the result')
    parser.add_argument('--no-cells', action='store_true', help='stop after dfflibmap')
    parser.add_argument(
        '--cell-lib', type=str, default='tech/osu018/osu018_stdcells.lib',
        help='e.g. path to osu018_stdcells.lib')
    args = parser.parse_args()
    args.in_verilog = deque(args.in_verilog)
    for additional in ['src/assert_ignore.sv', 'src/op_const.sv', 'src/const.sv']:
        if additional not in args.in_verilog:
            args.in_verilog.appendleft(additional)
    print(args.in_verilog)

    run(args)
