import os
import subprocess
from collections import defaultdict
from typing import List, TYPE_CHECKING
from tempfile import TemporaryDirectory

from ..base.network import Network


if TYPE_CHECKING:
    from ..swarm.node import SwarmNode
    from ..swarm.utils import SwarmHost


class AutoClusterNetwork(Network):
    """Can be used only with AutoSwarmNode and AutoSwarmSubnet

    Local networks are not supported yet.
    Fixed nodes also are not supported yet, sorry.
    """
    _nodes: List['SwarmNode']

    # TODO: store preset in this module and find out abs path dynamically
    def __init__(
            self, ip_range, hosts: List['SwarmHost'], *args,
            kahypar_preset='/home/panda/kahypar/config/cut_kKaHyPar_sea20.ini',
            max_imbalance=0.03,
            **kwargs
    ):
        self.hosts = hosts
        self.kahypar_preset = kahypar_preset
        self.max_imbalance = max_imbalance
        super().__init__(ip_range, *args, **kwargs)

    def split_network(self):
        """This function will assign a cluster host for each Node in network"""
        subnet_to_node_idx = defaultdict(list)
        fixed_nodes_file_lines = []

        for node_idx, node in enumerate(self._nodes):
            for subnet in node.subnets:
                subnet_to_node_idx[subnet].append(str(node_idx+1))
                # fixed_nodes_file_lines.append('0' if node.is_router else '-1')
                fixed_nodes_file_lines.append('-1')

        hMetis_file_lines = [
            '{} {}'.format(len(self._subnets), len(self._nodes)),
            *[' '.join(subnet_to_node_idx[subnet]) for subnet in self._subnets]
        ]

        with TemporaryDirectory() as tmp_dir:
            hMetis_file = os.path.join(tmp_dir, 'in.graph')
            fixed_nodes_file = os.path.join(tmp_dir, 'fix_file')

            with open(hMetis_file, 'w') as tmp_file:
                tmp_file.write('\n'.join(hMetis_file_lines) + '\n')

            with open(fixed_nodes_file, 'w') as tmp_file:
                tmp_file.write('\n'.join(fixed_nodes_file_lines) + '\n')

            ret = subprocess.run(
                'kahypar -h {0} -k {1} -e {2} -o cut -m direct -f {4} -p {3} -w True'.format(
                    hMetis_file,
                    len(self.hosts),
                    self.max_imbalance,
                    self.kahypar_preset,
                    fixed_nodes_file
                ),
                shell=True,
                capture_output=True)

            if ret.returncode != 0:
                raise Exception("Error while using KaHyPar: \n" + ret.stdout.decode() + '\n' + ret.stderr.decode())

            try:
                ret_filename = os.path.join(
                    tmp_dir,
                    next(filter(
                            lambda f: f not in [
                                os.path.basename(hMetis_file),
                                os.path.basename(fixed_nodes_file)
                            ],
                            os.listdir(tmp_dir)
                    )))
            except StopIteration:
                raise Exception("Error: KaHYPar did not create any files")

            with open(ret_filename) as ret_file:
                raw_partition = [int(line) for line in ret_file.readlines()]

        for node_idx, part_idx in enumerate(raw_partition):
            self._nodes[node_idx].cluster_host = self.hosts[part_idx]

    def start(self, interactive=False):
        self.split_network()
        return super().start(interactive=interactive)

    def load(self):
        self.split_network()
        return super().load()
