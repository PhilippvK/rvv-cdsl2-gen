# Inspired by: https://github.com/chipsalliance/t1/blob/master/v/script/inst_v.py

# import copy
import json

# import math

fun3 = {
    "line0": {
        "V": "000",
        "X": "100",
        "I": "011",
    },
    "line1": {
        "V": "010",
        "X": "110",
    },
    "line2": {
        "V": "001",
        "F": "101",
    },
}

extend_encode = {
    "vs1": {
        "VWXUNARY0": {
            "00000": "vmv.x.s",
            "10000": "vpopc",
            "10001": "vfirst",
        },
        "VXUNARY0": {
            "00010": "vzext.vf8",
            "00011": "vsext.vf8",
            "00100": "vzext.vf4",
            "00101": "vsext.vf4",
            "00110": "vzext.vf2",
            "00111": "vsext.vf2",
        },
        "VWFUNARY0": {
            "00000": "vfmv.f.s",
        },
        "VFUNARY0": {
            # single-width converts
            "00000": "vfcvt.xu.f.v",
            "00001": "vfcvt.x.f.v",
            "00010": "vfcvt.f.xu.v",
            "00011": "vfcvt.f.x.v",
            "00110": "vfcvt.rtz.xu.f.v",
            "00111": "vfcvt.rtz.x.f.v",
            # widening converts
            "01000": "vfwcvt.xu.f.v",
            "01001": "vfwcvt.x.f.v",
            "01010": "vfwcvt.f.xu.v",
            "01011": "vfwcvt.f.x.v",
            "01100": "vfwcvt.f.f.v",
            "01110": "vfwcvt.rtz.xu.f.v",
            "01111": "vfwcvt.rtz.x.f.v",
            # narrowing converts
            "10000": "vfncvt.xu.f.w",
            "10001": "vfncvt.x.f.w",
            "10010": "vfncvt.f.xu.w",
            "10011": "vfncvt.f.x.w",
            "10100": "vfncvt.f.f.w",
            "10101": "vfncvt.rod.f.f.w",
            "10110": "vfncvt.rtz.xu.f.w",
            "10111": "vfncvt.rtz.x.f.w",
        },
        "VFUNARY1": {
            "00000": "vfsqrt.v",
            "00100": "vfsqrt7.v",
            "00101": "vfrec7.v",
            "10000": "vfclass.v",
        },
        "VMUNARY0": {
            "00001": "vmsbf",
            "00010": "vmsof",
            "00011": "vmsif",
            "10000": "viota",
            "10001": "vid",
        },
    },
    "vs2": {"VRXUNARY0": {"00000": "vmv.s.x"}, "VRFUNARY0": {"00000": "vfmv.s.f"}},
}
sp_inst = ["100111", "", "", "I", "vmv<nr>r"]
opList = [
    "and",
    "or",
    "xor",
    "xnor",
    "add",
    "sub",
    "adc",
    "sbc",
    "slt",
    "sle",
    "sgt",
    "sge",
    "seq",
    "sne",
    "max",
    "min",
    "sl",
    "sr",
    "mul",
    "div",
    "rem",
    "ma",
    "ms",
    "slide",
    "rgather",
    "merge",
    "mv",
    "clip",
    "compress",
    "sum",
]
mul_list = ["mul", "ma", "ms"]
div_list = ["div", "rem"]
add_list = ["add", "sub", "slt", "sle", "sgt", "sge", "max", "min", "seq", "sne", "adc", "sbc", "sum"]
logic_list = ["and", "or", "xor", "xnor"]
shift_list = ["sr", "sl"]
other_list = ["slide", "rgather", "merge", "mv", "clip", "compress"]
ffo_list = ["vfirst", "vmsbf", "vmsof", "vmsif"]


def res_gen():
    with open("inst.txt", "r") as fd:
        res = {
            "line0": [sp_inst],
            "line1": [],
            "line2": [],
        }
        for i in fd.readlines():
            if "|===" in i:
                break
            sp = [s.strip(" ").strip("\n") for s in i.split("|")]
            line0 = sp[1:6]
            line1 = sp[6:10]
            line2 = sp[10:]
            if line0[-1] == "":
                ...
            elif line0[0] == "":
                print("code miss: ", sp)
            else:
                res["line0"].append(line0)

            if line1[-1] == "":
                ...
            elif line1[0] == "":
                print("code miss: ", line1)
            else:
                res["line1"].append(line1)

            if line2[-1] == "":
                ...
            elif line2[0] == "":
                print("code miss: ", line2)
            else:
                res["line2"].append(line2)
    return res


def dump_inst():
    with open("inst_list.json", "w") as fd:
        json.dump(res_gen(), fd, indent=2)


def load_res():
    with open("inst_list.json", "r") as fd:
        res = json.load(fd)
        return res


def b2s(b):
    return "1" if b else "0"


def inst_parse():
    fd = open("output.core_desc", "w")
    res = load_res()
    count = 0
    end_count = 0
    for fun_3 in ["line0", "line1", "line2"]:
        # print("fun_3", fun_3)
        for i in res[fun_3]:
            # print("  i", i)
            count += 1
            c_op = False
            j_list = []
            for j in opList:
                if j in i[-1]:
                    j_list.append(j)
                    c_op = True
            # print("  c_op", c_op)
            if not c_op:
                # print("  if not")
                v_src = "V" in i[1:3]
                fun_3_st = fun3["line1"]["V"] if v_src else fun3["line1"]["X"]
                placeholder = i[-1]
                for k, v in extend_encode.items():
                    # print("    k", k)
                    # print("    v", v)
                    if v.get(placeholder):
                        for rsx, inst_name in v.get(placeholder).items():
                            inst_st_p = 'BitPat("b%s??????%s%s")' if k == "vs1" else 'BitPat("b%s?%s?????%s")'
                            funct7 = "1010111"
                            funct6 = i[0]
                            # bbb = rsx
                            funct3 = fun_3_st
                            vs2_str = f"5'b{rsx}" if k == "vs2" else "vs2[4:0]"
                            vs1_str = f"5'b{rsx}" if k == "vs1" else "vs1/imm/rs1[4:0]"
                            vd_str = "vd/rd[4:0]"
                            # print(f"{inst_name}:")
                            # print("funct6", aaa)
                            # print(k, bbb)
                            # print("funct3", ccc)
                            print(inst_name, "{")
                            print(
                                f"  encoding: 6'b{funct6} :: vm[0:0] :: {vs2_str} :: {vs1_str} :: 3'b{funct3} :: {vd_str} :: 7'b{funct7}"
                            )
                            print(f'  assembly: {{"{inst_name}.??", "?"}};')
                            print("  behavior: {};")
                            print("}")
                            # input(">1")
                            inst_st = inst_st_p % (i[0], rsx, fun_3_st)
                            fd.write(inst_name + ": " + inst_st + "\n")

            else:
                # print("  else")
                # inst_str = copy.deepcopy(i[-1])
                op_st = ""
                # 确认opcode
                if len(j_list) == 1:
                    op_st = j_list[0]
                else:
                    #  不是乘加/减
                    if "ma" in j_list:
                        if "add" in j_list:
                            j_list.remove("add")
                        else:
                            j_list.remove("ma")
                    if "ms" in j_list:
                        if "sub" in j_list:
                            j_list.remove("sub")
                        else:
                            j_list.remove("ms")
                    # 找最长的
                    max_len = 0
                    max_op = ""
                    for op_ in j_list:
                        if len(op_) > max_len:
                            max_len = len(op_)
                            max_op = op_
                    if all(max_op.__contains__(ss) for ss in j_list):
                        op_st += max_op
                        j_list = [max_op]

                    if "merge" in j_list:
                        j_list.remove("mv")

                    if len(j_list) != 1:
                        # print(j_list, "???")
                        pass
                    else:
                        op_st += j_list[0]
                end_index = 4 if fun_3 == "line0" else 3
                for inst_type in i[1:end_index]:
                    # print("    inst_type", inst_type)
                    if inst_type == "":
                        continue
                    inst_st = 'BitPat("b%s%s%s")' % (i[0], "?" * 11, fun3[fun_3][inst_type])
                    funct6 = i[0]
                    funct3 = fun3[fun_3][inst_type]
                    vs2_str = "vs2[4:0]"
                    vs1_str = "vs1/imm/rs1[4:0]"
                    vd_str = "vd/rd[4:0]"
                    funct7 = "1010111"
                    # print(f"{i[-1]}:")
                    # print("funct6", funct6)
                    # print("funct3", funct3)
                    print(i[-1].upper(), "{")
                    print(
                        f"  encoding: 6'b{funct6} :: vm[0:0] :: {vs2_str} :: {vs1_str} :: 3'b{funct3} :: {vd_str} :: 7'b{funct7};"
                    )
                    print(f'  assembly: {{"{i[-1]}.??", "?"}};')
                    print("}")
                    # input(">2")
                    abc = "?"
                    fd.write(i[-1] + "." + abc + inst_type.lower() + ": " + inst_st + "\n")

                end_count += 1
    print(count, end_count)


dump_inst()
inst_parse()
