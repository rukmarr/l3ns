import docker

dc = docker.from_env()


def show_taken_networks():

    for net in dc.networks.list():
        try:
            print('{}: {}'.format(net.name, net.attrs['IPAM']['Config'][0]['Subnet']))
        except (KeyError, IndexError):
            print('{}: Error: {}'.format(net.name, 'No config'))
        except Exception as e:
            print('{}: Error: {}'.format(net.name, e))


if __name__ == "__main__":
    show_taken_networks()
