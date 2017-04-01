from bcnf import FunctionalDependencySet

class Database:
    def __init__(self):
        self.tables = {}

    def set_table(self, name, table=None):
        table = table if table else Table(name)
        self.tables[name] = table
        return table

    def get_table(self, name):
        return self.tables[name]

    def drived_fdset(self):
        attributes = []
        for tableName in self.tables:
            for attribute in self.tables[tableName].attributes:
                if attribute[0] in self.tables[tableName].refrenced_attributes:
                    continue
                attributes.append(tableName + "." + attribute[0])
        fdset = FunctionalDependencySet(attributes)
        for tableName in self.tables:
            tableKey = [tableName + "." + key for key in self.tables[tableName].primary_keys]
            for attribute in self.tables[tableName].attributes:
                if attribute[0] in self.tables[tableName].refrenced_attributes:
                    for foreign_key in self.tables[tableName].foreign_keys:
                        if attribute[0] in foreign_key[0]:
                            fdset.add_dependency(tableKey, [foreign_key[1] + "." + key for key in foreign_key[2]])
                            break
                else:
                    fdset.add_dependency(tableKey, [tableName + "." + attribute[0]])
        return fdset

class Table:
    def __init__(self, table_name):
        self.table_name = table_name
        self.attributes = []
        self.primary_keys = []
        self.refrenced_attributes = []
        self.foreign_keys = []

    def add_attribute(self, name, type):
        self.attributes.append((name, type))

    def add_primary_key(self, attr):
        self.primary_keys.append(attr)

    def add_foreign_key(self, this_attrs, that_table_name, that_attrs):
        for attr in this_attrs:
            self.refrenced_attributes.append(attr)
        self.foreign_keys.append((tuple(this_attrs), that_table_name, tuple(that_attrs)))