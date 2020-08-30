import os
import hashids

from .. import ldc
from .utils import my_hash, generate_wg_keys, ClusterHost, vpn_server_address
from .subnet import WgSubnet


node_config_template = '''[Interface]
PrivateKey = {private_key}

[Peer]
# vpn_server
Endpoint={vpn_server_address}:{vpn_server_port}
PublicKey = {vpn_server_public_key}
AllowedIPs = {network_ip_range}
PersistentKeepalive = 25
'''

node_startup_script = '''
pid=$(docker inspect -f '{{{{.State.Pid}}}}' {c_id}) && \\
mkdir -p /var/run/netns/ && \\
ln -sfT /proc/$pid/ns/net /var/run/netns/{c_id} && \\
ip link add dev {ifc} type wireguard && \\
wg setconf {ifc} {config_path} && \\
ip link set {ifc} netns {c_id} && \\
ip -n {c_id} addr add {ip_address}/{net_mask} dev {ifc} && \\
ip -n {c_id} link set {ifc} up
'''


class RemoteNode(ldc.DockerNode):

    def __init__(self, name, cluster_host: 'ClusterHost', **kwargs):
        self.cluster_host = cluster_host
        self.config_path = os.path.join('/tmp/l3ns', name) + '.conf'

        self.private_key, self.public_key = generate_wg_keys()

        super().__init__(name, **kwargs)

        self._client = cluster_host.get_docker_client()

    def _connect_subnet(self, network, ip):

        if isinstance(network, ldc.DockerSubnet):
            super()._connect_subnet(network, ip)
        elif isinstance(network, WgSubnet):
            # connect to wg_subnet

            self.cluster_host.upload_config(self.config_path, node_config_template.format(
                private_key=self.private_key,
                vpn_server_address=vpn_server_address,
                vpn_server_port=network.listen_port,
                vpn_server_public_key=network.public_key,
                network_ip_range=network.get_network().ip_range
            ))

            cmd = node_startup_script.format(
                ifc='wg-' + my_hash(self.name, network),
                ip_address=self.get_ip(network),
                net_mask=network.prefixlen(),
                config_path=self.config_path,
                c_id=self.container.short_id
            )

            # print('_________________\n', cmd, '_________________')

            status_code, stdout, stderr = self.cluster_host.exec_command(cmd)

            if status_code:
                print('Error while connecting node {} to the subnet {}:'.format(self.name, network.name))
                print('status_code: ' + str(status_code))
                if stdout:
                    print('stdout: ' + stdout)
                if stderr:
                    print('stderr: ' + stderr)
            else:
                print('{} connected to the subnet {}'.format(self.name, network.name))

        else:

            raise Exception("Unexpected network type: " + network.name)

    def __repr__(self):
        return '<{class_name}({name}@{hostname}, {ip})'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            ip=self.get_ip(),
            hostname=self.cluster_host.address)
