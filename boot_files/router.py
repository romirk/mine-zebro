import comms

class Router:

    def __init__(self):
        self.__modules = Submodules()

    def boot_modules(self, comms):
        print("Router setup started")
        #Boot all modules and save the essential ones given by the MCP
        self.__modules.add_by_id(comms.get_id(), comms)#Need an for submodules to inherit from
        #locomotion = locomotion.locomotion_manager()





class Submodules:
    __predefined_max = 2 # should be equal to the max number of modules
    __id_list = ["Comms", "locomotion"] #every module needs to implement a getter for their id

    def __init__(self):
        self.__list = [] * self.__predefined_max

    def map_id_to_index(self, id):
        return self.__id_list.index(id)

    def add_by_index(self, index, module):
        self.__list.insert(index, module)

    def add_by_id(self, id, module):
        return self.add_by_index(self.map_id_to_index(id), module)

    def get_from_id(self, id):
        return self.__list.index(id)

    def get_module_from_index(self, index):
        return self.__list[index]
