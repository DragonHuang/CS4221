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
        fdsets = {}
        attributes = set()
        related = []
        for tableName in self.tables:
            for name in self.tables[tableName].related:
                if name not in related:
                    related.append(name)
        for tableName in self.tables:
            if tableName in related:
                fdsets[tableName] = self.tables[tableName].drived_fdset()
        for tableName in fdsets:
            for attr in fdsets[tableName].attributes:
                attributes.add(attr)
        fdset = FunctionalDependencySet(attributes)
        for tableName in fdsets:
            for dep in fdsets[tableName].dependencies:
                try:
                    fdset.add_dependency(dep[0], dep[1])
                except Exception as e:
                    print(e)
        return fdset

class Table:
    def __init__(self, table_name):
        self.table_name = table_name
        self.attributes = set()
        self.primary_keys = set()
        self.refrences = []
        self.related = []

    def add_attribute(self, name, type):
        self.attributes.add(self.table_name + "." + name)

    def add_primary_key(self, name):
        self.primary_keys.add(self.table_name + "." + name)

    def add_foreign_key(self, this_attrs, that_table_name, that_attrs):
        this_attrs = set([self.table_name + "." + name for name in this_attrs])
        that_attrs = set([that_table_name + "." + name for name in that_attrs])
        self.related.append(self.table_name)
        if that_table_name != self.table_name:
            for name in this_attrs:
                self.attributes.add(name)
            for name in that_attrs:
                self.attributes.add(name)
            self.related.append(that_table_name)
        else:
            for name in this_attrs:
                self.attributes.add(name)
            self.refrences.append((this_attrs, that_attrs))
            print (this_attrs, that_attrs)
        

    def drived_fdset(self):
        fdset = FunctionalDependencySet(self.attributes)
        for attr in self.attributes:
            fdset.add_dependency(self.primary_keys, [attr])
        for ref in self.refrences:
            fdset.add_dependency(ref[0], ref[1])
        return fdset