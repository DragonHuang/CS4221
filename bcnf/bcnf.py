from itertools import permutations, chain


class FunctionalDependencySet:
    def __init__(self, attributes):
        self.dependencies = []
        self.attributes = set()
        self.is_decomposed = False
        self.tables = []

        for attr in attributes:
            self.add_attribute(attr)

    def add_attribute(self, attr):
        self.attributes.add(attr)

    def add_dependency(self, x, y):
        for i in chain(x, y):
            if i not in self.attributes:
                raise Exception("Attribute " + i + " does not exist")
        self.dependencies.append((set(x), set(y)))

    def get_attr_closure(self, attr):
        closure = set(attr)
        last = set()
        while closure != last:
            last = closure.copy()
            for dep in self.dependencies:
                if dep[0].issubset(closure):
                    closure.update(dep[1])
        return closure

    def find_candidate_keys(self):
        for i in range(1, len(self.attributes) + 1):
            ans = []
            for keys in permutations(self.attributes, i):
                keys = ''.join(keys)
                if self.get_attr_closure(keys) == self.attributes:
                    ans.append(''.join(sorted(keys)))
            if len(ans) > 0:
                return set(ans)

    def find_prime_attributes(self):
        candidate_keys = self.find_candidate_keys()
        prime_attributes = set()
        for key in candidate_keys:
            for attr in key:
                prime_attributes.add(attr)
        return sorted(prime_attributes)

    def is_full_depends(self, a, b):
        if b not in self.get_attr_closure(a):
            return False
        for i in range(1, len(a)):
            for keys in permutations(a, i):
                if b in self.get_attr_closure(keys):
                    return False
        return True

    def is_bcnf(self):
        result = True
        for dep in self.dependencies:
            result = result and (dep[1].issubset(dep[0]) or self.get_attr_closure(dep[0]) == self.attributes)
        return result

    def decompose(self):
        if self.is_decomposed:
            return
        self.is_decomposed = True
        self.tables = [self.attributes]
        for dep in self.dependencies:
            for attr_set in self.tables:
                new_set = dep[0].symmetric_difference(dep[1])
                if new_set.issubset(attr_set) and new_set != attr_set:
                    attr_set.difference_update(dep[1])
                    self.tables.append(new_set)
        return self.tables

    def decompose_all(self):
        tables_possibilities = []
        for ordering in permutations(self.dependencies):
            tbl = [self.attributes.copy()]
            for dep in ordering:
                for attr_set in tbl:
                    new_set = dep[0].symmetric_difference(dep[1])
                    if new_set.issubset(attr_set) and new_set != attr_set:
                        attr_set.difference_update(dep[1])
                        tbl.append(new_set)
            tbl = [tuple(x) for x in tbl]
            tables_possibilities.append(tuple(tbl))
        return set(tables_possibilities)

if __name__ == '__main__':
    r = FunctionalDependencySet(['A1', 'B1', 'C1'])
    r.add_dependency(set(['A1']), set(['B1']))
    r.add_dependency(set(['A1']), set(['C1']))

    print r.get_attr_closure(['A1'])
