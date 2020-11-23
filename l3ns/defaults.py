import l3ns.base.network


network = l3ns.base.network.Network('22.0.0.0/16')
"""Default network for all Subnets"""

import l3ns.ldc.subnet
subnet_class = l3ns.ldc.subnet.DockerSubnet
"""Default subnet class for Node.connect_to and Network.create_subnet"""

