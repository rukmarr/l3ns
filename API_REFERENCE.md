<a name="l3ns.base.network"></a>
# l3ns.base.network

<a name="l3ns.base.network.Network"></a>
## Network Objects

```python
class Network()
```

Base class for forming local and wide area networks

<a name="l3ns.base.network.Network.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(ip_range: Union[str, IPv4Network], local=False)
```

Creates network with given ip range.

Creates local or wide area nerwork with a given ip range that will be
distributed to subnetworks that will be created in this network.

**Arguments**:

- `ip_range` - IP address range for the networks
- `local` - Optional; Set to True to create local network

<a name="l3ns.base.network.Network.start"></a>
#### start

```python
 | start(interactive=False)
```

Launches all the subnetworks and nodes in this network

This function calls appropriate functions for subnets first
and for nodes later. Even nodes that are not connected to
any subnets will be started.

Interactive mode allows user to start and stop the network
with a simpler script, locking at the shell prompt
after the network is started and shutting it down on user
input. Non-interactive mode doesn't lock code execution, so
you can create more complex testing scripts.


**Arguments**:

- `interactive` - Optional; Sets whether interactive mode will be used

<a name="l3ns.base.network.Network.load"></a>
#### load

```python
 | load(*args)
```

Loads network resources

Loads network resources (i.e. containers and
docker networks in l3ns.ldc) that were previously
launched in a different script back in the memory.


Note that this will not load network stricture, it
needs to be already defined. This allows you to work
with network resources from several scripts.

<a name="l3ns.base.network.Network.stop"></a>
#### stop

```python
 | stop(*args)
```

Stops the network

<a name="l3ns.base.network.Network.add_node"></a>
#### add\_node

```python
 | add_node(node)
```

Add node to the network

<a name="l3ns.base.network.Network.add_subnet"></a>
#### add\_subnet

```python
 | add_subnet(subnet)
```

Add subnet to the network

<a name="l3ns.base.network.Network.create_subnet"></a>
#### create\_subnet

```python
 | create_subnet(subnet_name, *args, *, subnet_type: type = None, **kwargs)
```

Create subnet in this network

<a name="l3ns.base.network.Network.get_subnet_range"></a>
#### get\_subnet\_range

```python
 | get_subnet_range(size: int)
```

Retrieve an IP range of given size for subnet and remove it from available addresses

<a name="l3ns.base.network.NetworkConcurrent"></a>
## NetworkConcurrent Objects

```python
class NetworkConcurrent(Network)
```

WIP-interface to launch large networks (500+ nodes) concurrently.

<a name="l3ns.base.network.NetworkConcurrent.start"></a>
#### start

```python
 | start(interactive=False)
```

Starts the network concurrently using ThreadPoolExecutor

<a name="l3ns.base.network.NetworkConcurrent.stop"></a>
#### stop

```python
 | stop()
```

Stops the network concurrently using ThreadPoolExecutor

<a name="l3ns.base.node"></a>
# l3ns.base.node

<a name="l3ns.base.node.BaseNode"></a>
## BaseNode Objects

```python
class BaseNode()
```

Base class for Nodes representing computers in virtual networks

<a name="l3ns.base.node.BaseNode.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(name, internet_connection=False)
```

Create node

Create basic node with black configuration.

**Arguments**:

- `name` - unique identifier for new node
- `internet_connection` - Optional; whether node should be able th connect to internet

<a name="l3ns.base.node.BaseNode.connect_to"></a>
#### connect\_to

```python
 | connect_to(other_node: 'BaseNode', subnet_name: str = None, subnet_class: type = None, **subnet_kwargs)
```

Create subnet that connects this node to another

Create a subnet with that will consist of two nodes. You can specify
specific subnet class and name. If not, name will be generated automatically
and subnet class will be retrieved from [defaults](l3ns.defaults).

**Arguments**:

- `other_node` - Node to connect
- `subnet_name` - Name to use for net subnet
- `subnet_class` - Class to use for new subnet

<a name="l3ns.base.node.BaseNode.add_interface"></a>
#### add\_interface

```python
 | add_interface(ip_address, subnet: 'base_subnet.BaseSubnet')
```

Add network interface to container

Network interfaces are used to store node's IP address and names of the virtual
network interfaces that will be created on node start (like br-xxxxxx for docker networks)
This functions called mostly from Subnet.add_node.

<a name="l3ns.base.node.BaseNode.start"></a>
#### start

```python
 | start(*args, **kwargs)
```

Start function called from Network.start

Start procedure starts with gathering routing information from
node's subnets and LANs. Then Node._start is called to create the node itself,
after that Node._connect_subnets connects node to it's subnets and
Node._deploy_routes sets up node's routes.

<a name="l3ns.base.node.BaseNode.make_router"></a>
#### make\_router

```python
 | @classmethod
 | make_router(cls, *args, **kwargs)
```

Function defining router node to be implemented in resource-specific classed, like DockerNode

<a name="l3ns.base.node.BaseNode.activate_protocol"></a>
#### activate\_protocol

```python
 | activate_protocol(protocol, config)
```

Function activating routing protocol for node
to be implemented in resource-specific classed, like DockerNode

<a name="l3ns.base.node.BaseNode.unlock"></a>
#### unlock

```python
 | unlock()
```

Unlock node from waiting mode

Node: WIP

Starting large networks can take a long time, so if one node workload
depends on the other node it cant be launched before the other node started.
If you want all nodes to start simultaneously, a waiting mode before workload
is required. For DockerNode, for example, we modify entrypoint to make
original entrypoint and cmd to be launched only if certain file exists and
than create that file on unlocking.

<a name="l3ns.base.node.BaseNode.put_string"></a>
#### put\_string

```python
 | put_string(path, string)
```

Put sting in file on node

<a name="l3ns.base.subnet"></a>
# l3ns.base.subnet

<a name="l3ns.base.subnet.BaseSubnet"></a>
## BaseSubnet Objects

```python
class BaseSubnet()
```

Base class for subnets representing IP subnets of the virtual networks

<a name="l3ns.base.subnet.BaseSubnet.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(name: str, *args, *, size: int = 1024, network: 'base_network.Network' = None)
```

Create subnet with given name and size in given Network

Names of networks need to be unique, as with Nodes.
Size can't be anything as long as Network has free IP addresses in pool.
However there is to caveats:
1. Some implementation must have several IP addresses reserved, for example
DockerNetwork reserves one IP address for virtual bridge interface.
This will increase network size.
2. Actual subnet IP address size must be a power of two. So actual size of network will be
increase to a nearest power of two.

**Arguments**:

- `name` - name for new subnet
- `*args` - nodes to add to the new network
- `size` - Optional; size of a new network
- `network` - Optional; as the name implies every subnet lies in some network.
  If network is not provided, l3ns.defaults.network will be used.

<a name="l3ns.base.subnet.BaseSubnet.add_node"></a>
#### add\_node

```python
 | add_node(node: 'base_node.BaseNode')
```

Add node to the network

This is a main method to define network structure.
This will add node to network, in create interface in node with an
IP address from this subnet.

<a name="l3ns.base.subnet.BaseSubnet.start"></a>
#### start

```python
 | start()
```

Subnet starting procedure to be implemented in resource-specific classed, like DockerSubnet

<a name="l3ns.base.subnet.BaseSubnet.load"></a>
#### load

```python
 | load()
```

Subnet loading procedure to be implemented in resource-specific classed, like DockerSubnet

<a name="l3ns.base.subnet.BaseSubnet.stop"></a>
#### stop

```python
 | stop()
```

Subnet stopping procedure to be implemented in resource-specific classed, like DockerSubnet

<a name="l3ns.base.subnet.BaseSubnet.get_network"></a>
#### get\_network

```python
 | get_network()
```

Get Network this subnet resides in.

<a name="l3ns.base.subnet.BaseSubnet.get_gateway"></a>
#### get\_gateway

```python
 | get_gateway(node)
```

Get default gateway for this network

If this subnet resides in a local network and has LAN gateway
(i.e. Node that belongs both to local and wide area networks and
has NAT protocol configured), than lan gateway will be used
as default gateway.
If there is no LAN gateway in the subnet, random router
will be used as default gateway.
If there is no LAN gateway and no router in the subnet, function
will return None

<a name="l3ns.base.subnet.BaseSubnet.get_nodes_dict"></a>
#### get\_nodes\_dict

```python
 | get_nodes_dict()
```

Get nodes in a dict with IP addresses as keys

<a name="l3ns.base.subnet.BaseSubnet.prefixlen"></a>
#### prefixlen

```python
 | prefixlen()
```

Get subnet IP address prefix length

<a name="l3ns.base.subnet.BaseSubnet.get_ip_range"></a>
#### get\_ip\_range

```python
 | get_ip_range()
```

Get subnet IP address,

<a name="l3ns.base.subnet.BaseSubnet.nodes"></a>
#### nodes

```python
 | @property
 | nodes()
```

Get a list of subnet's nodes

