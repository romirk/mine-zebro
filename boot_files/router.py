import comms

# Executed once imported
print("router online")


class Router:

    def __init__(self, cooms):
        print("Router setup started")
        modules = Submodules()


        return


class Submodules:
    __predefined_max = 2 # should be equal to the max number of modules
    __id_list = ["Comms", "locomotion"] #every module needs to implement a getter for their id

    def __init__(self):
        self.__list = [] * self.__predefined_max

    def map_list_index_from_id(self, id):
        return self.__list.index(id)

    def add_module_by_index(self, index, module):
        self.__list.insert(index, module)

    def add_module_by_id(self, id, module):
        return self.add_module_by_index(self.map_list_index_from_id(id))

    def get_module_from_id(self, id):
        return self.__list.index(id)

    def get_module_from_index(self, index):
        return self.__list[index]
