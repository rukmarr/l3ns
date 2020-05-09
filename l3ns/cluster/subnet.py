import os
import subprocess
import shutil

from .. import base
from .. import ldc
from .utils import my_hash, generate_wg_keys, find_free_port
from .. import utils

server_config_template = '''[Interface]
ListenPort = {listen_port}
PrivateKey = {private_key}

'''

peer_config_template = '''[Peer]
# {name}
PublicKey = {public_key}
AllowedIPs = {ip_address}/32
'''

server_startup_script = '''
ip link add dev {ifc} type wireguard && \
wg setconf {ifc} {config_file} && \
ip addr add {ip_address}/{net_mask} dev {ifc} && \
ip link set {ifc} up  && \
iptables -A INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT && \
iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT && \
iptables -A FORWARD -i {ifc} -o {ifc} -m conntrack --ctstate NEW -j ACCEPT
'''


class WgSubnet(base.BaseSubnet):

    def __init__(self, *args, size=1023, **kwargs):
        super().__init__(*args, size=size + 1, **kwargs)

        self.private_key, self.public_key = generate_wg_keys()
        self.listen_port = None

        # TODO: proper config for this
        self.interface_name = 'wg-' + my_hash(self.name)
        self.config_folder = '/tmp/l3ns/' + self.name
        self.config_filename = os.path.join(self.config_folder, 'wg.conf')

        self._vpn_server_ip = self._get_host_ip()

    def make_server_config(self):
        self.listen_port = find_free_port()
        config = server_config_template.format(
            listen_port=self.listen_port,
            private_key=self.private_key)

        config += '\n\n'.join([peer_config_template.format(
            name=node.name,
            public_key=node.public_key,
            ip_address=node.get_ip(net=self)
        ) for node in self._nodes_dict.values()])

        return config

    def start(self):
        if self.started:
            return

        try:
            os.mkdir(self.config_folder)
        except FileExistsError:
            pass  # TODO: for now

        with open(self.config_filename, 'w') as config_file:
            config_file.write(self.make_server_config())

        ret = subprocess.run(server_startup_script.format(
            ifc=self.interface_name,
            config_file=self.config_filename,
            ip_address=self._vpn_server_ip,
            net_mask=self.prefixlen()
        ),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            shell=True)

        if ret.returncode != 0:
            print('Error while starting subnet ' + self.name + ':', ret.stdout.strip(), sep='\n')

    def load(self):
        # TODO: load keys??
        pass

    def stop(self):
        ret = subprocess.run('ip link delete {}'.format(self.interface_name),
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             universal_newlines=True,
                             shell=True)

        if ret.returncode != 0:
            print('Error while removing subnet ' + self.name + ':', ret.stdout.strip(), sep='\n')

        try:
            shutil.rmtree(self.config_folder)
        except FileNotFoundError:
            print('Error while removing subnet ' + self.name + ':',
                  'WireGuard config directory does not exist', sep='\n')

        print('subnet', self.name, 'stopped')

    @classmethod
    def make_subnet(cls, *args, size=1023, network=None):
        node_list = utils.args.list_from_args(args)

        try:
            cluster_host_set = set([node.cluster_host for node in node_list])
        except AttributeError:
            raise Exception("Only RemoteNodes can be in the ClusterSubnet")

        if len(cluster_host_set) == 1:
            return ldc.DockerSubnet(*args, size=size, network=network)
        else:
            return cls(*args, size=size, network=network)
