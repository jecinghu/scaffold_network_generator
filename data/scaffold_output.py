from data import graph
from rdkit import Chem
from os import path
from .proto import *
import linecache
from .utils import *

# input_file = 'input_10.txt'
input_file = 'input.txt'
input_dir = path.join(path.dirname(__file__),
                      'datasets',
                      input_file
                      )


def get_sng_from_smiles(smiles):
    mol_graph = graph.get_mol_graph(smiles)
    ls_atom, ls_bond = mol_graph.graph_list_to_list()
    ls_scaffold = mol_graph.ls_mol_from_sng_u()
    ls_mol_atom_idx = []
    for i in range(len(ls_scaffold)):
        ls_atom_idx = []
        for j in ls_atom[i]:
            ls_atom_idx.append(j[1])
        ls_mol_atom_idx.append((Chem.MolToSmiles(ls_scaffold[i]),
                                ls_atom_idx))
    return ls_mol_atom_idx


def smiles_from_line(idx=0, file=input_dir):
    return linecache.getline(file, idx+1).strip()


def sng_from_line(idx=0, file=input_dir):
    return get_sng_from_smiles(smiles_from_line(idx, file))


def sng_from_line_2_queue(idx, q):
    q.put((idx, sng_from_line(idx)))


def protobuf_from_queue(q):
    scaffold_dict = DicIdxScaffolds()
    dataset = DicScaffoldLs()
    for i in range(get_num_lines(input_dir)):
        mol_index, sng_test = q.get()
        for mol_sng_index in range(len(sng_test)):
            sng_now, sng_atoms = sng_test[mol_sng_index]  # 获取当前的scaffold骨架 smiles 及 骨架原子的list
            sng_dict_index = -1
            sng_dict_len = len(scaffold_dict.dic_scaffold)  # scaffold dict 长度
            for sng_dict_index_tmp in range(sng_dict_len):  # 在scaffold dict里查重
                if sng_now == scaffold_dict.dic_scaffold[sng_dict_index_tmp]:
                    sng_dict_index = sng_dict_index_tmp
                    break
            if sng_dict_index == -1:  # 表明该scaffold未出现过
                scaffold_dict.dic_scaffold[sng_dict_len] = sng_now
                sng_dict_index = sng_dict_len
            # 初始化Dicmollsatom
            sng_pb = DicMolLsatom()
            sng_pb.idx_mol = mol_index
            sng_pb.ls_atom.idx_atom.extend(sng_atoms)
            # 将该scaffold对应的 当前正在处理的mol_id和atom_list添加到dataset当中
            dataset.idx_scaffold[sng_dict_index].dic_mol_atoms.extend([sng_pb])

    return scaffold_dict, dataset

def get_sng_protobuf(file=input_dir):
    # 初始化scaffold字典和 protobuf数据集
    scaffold_dict = DicIdxScaffolds()
    dataset = DicScaffoldLs()
    # 为方便后面再套循环，先随便初始化一个分子index
    for mol_index in range(get_num_lines(file)):
        smiles = linecache.getline(file, mol_index + 1).strip()
        sng_test = get_sng_from_smiles(smiles)
        # 遍历正在处理的分子的scaffold
        for mol_sng_index in range(len(sng_test)):
            sng_now, sng_atoms = sng_test[mol_sng_index]  # 获取当前的scaffold骨架 smiles 及 骨架原子的list
            sng_dict_index = -1
            sng_dict_len = len(scaffold_dict.dic_scaffold)  # scaffold dict 长度
            for sng_dict_index_tmp in range(sng_dict_len):  # 在scaffold dict里查重
                if sng_now == scaffold_dict.dic_scaffold[sng_dict_index_tmp]:
                    sng_dict_index = sng_dict_index_tmp
                    break
            if sng_dict_index == -1:  # 表明该scaffold未出现过
                scaffold_dict.dic_scaffold[sng_dict_len] = sng_now
                sng_dict_index = sng_dict_len
            # 初始化Dicmollsatom
            sng_pb = DicMolLsatom()
            sng_pb.idx_mol = mol_index
            sng_pb.ls_atom.idx_atom.extend(sng_atoms)
            # 将该scaffold对应的 当前正在处理的mol_id和atom_list添加到dataset当中
            dataset.idx_scaffold[sng_dict_index].dic_mol_atoms.extend([sng_pb])

    return scaffold_dict, dataset












