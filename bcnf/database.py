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
                attributes.append(tableName + "." + attribute[0])
        fdset = FunctionalDependencySet(attributes)
        return fdset

class Table:
    def __init__(self, table_name):
        self.table_name = table_name
        self.attributes = []
        self.primary_keys = []
        self.foreign_keys = []

    def add_attribute(self, name, type):
        self.attributes.append((name, type))

    def add_primary_key(self, attr):
        self.primary_keys.append(attr)

    def add_foreign_key(self, this_attrs, that_table_name, that_attrs):
        self.foreign_keys.append((tuple(this_attrs), that_table_name, tuple(that_attrs)))