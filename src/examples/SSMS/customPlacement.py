from yafs.placement import Placement

class FogPlacement(Placement):
    def initial_allocation(self, sim, app_name):
        # id_cluster are the fog devices
        id_cluster = sim.topology.find_IDs({"model": "fog-server"})
        id_cluster.extend(sim.topology.find_IDs({"model": "cloud-server"}))
        print id_cluster
        app = sim.apps[app_name]
        services = app.services

        for module in self.scaleServices:
            for rep in range(0, self.scaleServices[module]):
                sim.deploy_module(app_name, module, services[module], id_cluster)

class CloudPlacement(Placement):
    def initial_allocation(self, sim, app_name):
        # id_cluster are the fog devices
        id_cluster = sim.topology.find_IDs({"model": "cloud-server"})
        print id_cluster
        app = sim.apps[app_name]
        services = app.services

        for module in self.scaleServices:
            for rep in range(0, self.scaleServices[module]):
                sim.deploy_module(app_name, module, services[module], id_cluster)