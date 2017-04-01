class Database:
    def __init__(self):
        self.tables = {}

    def set_table(self, name, table=None):
        table = table if table else Table(name)
        self.tables[name] = table
        return table

    def get_table(name):
        return self.tables[name]

class Table:
    def __init__(self, table_name):
        self.table_name = table_name
        self.attributes = []
        self.primary_keys = []
        self.foreign_keys = []

    def add_attribute(self, name, type):
        self.attributes.append((name, type))

    def add_primary_key(self, attrs):
        self.primary_keys.append(tuple(attrs))

    def add_foreign_key(self, this_attrs, that_table_name, that_attrs):
        self.foreign_keys.append((tuple(this_attrs), that_table_name, tuple(that_attrs)))