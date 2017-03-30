import re

class DDLGenerator():

    ''' step one: fill in missing types,return to user for confirmation'''
    def fill_missing_type(self, dict, smart, database):

        entity_dict_list = dict['entity']
        for entity_dict in entity_dict_list:
            self.check_entity_attribute_types(entity_dict, smart, database)

        relation_dict_list = dict['relation']
        for relation_dict in relation_dict_list:
            self.check_relation_attribute_types(relation_dict, smart, database)

        return dict

    def check_entity_attribute_types(self, entity_dict, smart, database):
        attr_dict_list = entity_dict['attribute']
        for attr_dict in attr_dict_list:
            if 'name' in attr_dict:
                if 'type' not in attr_dict:
                    type = self.get_default_type(attr_dict['name'], smart, database)
                    attr_dict['type'] = type
                else:
                    sql_type = attr_dict['type']
                    database_type = self.change_to_correct_type(sql_type, database)
                    attr_dict['type'] = database_type

    def check_relation_attribute_types(self, relation_dict, smart, database):
        attr_dict_list = relation_dict['attribute']
        for attr_dict in attr_dict_list:
            if 'name' in attr_dict:
                if 'type' not in attr_dict:
                    type = self.get_default_type(attr_dict['name'], smart, database)
                    attr_dict['type'] = type
                else:
                    sql_type = attr_dict['type']
                    database_type = self.change_to_correct_type(sql_type, database)
                    attr_dict['type'] = database_type

    def get_default_type(self, attr_name, smart, database):

        if smart == False:
            if database == 'psql' or database == 'mssql':
                return 'varchar(32)'
            elif database == 'mysql':
                return 'text'
            elif database == 'oracle':
                return 'VARCHAR2'

        else:
            temp = attr_name + ""
            temp = temp.lower()

            if 'id' in temp or 'int' in temp or 'integer' in temp or 'num' in temp or 'number' in temp or 'postcode' in temp or 'tel' in temp or 'hp' in temp:
                if database == 'psql':
                    return 'integer'
                elif database == 'mysql':
                    return 'INT'
                elif database == 'oracle':
                    return 'NUMBER'
                elif database == 'mssql':
                    return 'int'

            elif 'rating' in temp or 'rate' in temp or 'price' in temp or 'money' in temp or 'salary' in temp or 'cost' in temp or 'ratio' in temp or 'percentage' in temp:
                if database == 'psql' or database == 'mssql' :
                    return 'real'
                elif database == 'mysql':
                    return 'FLOAT'
                elif database == 'oracle':
                    return 'NUMBER'

            elif 'date' in temp:
                if database == 'psql':
                    return 'date'
                elif database == 'mysql' or database == 'oracle':
                    return 'DATE'
                elif database == 'mssql':
                    return 'varchar(64)'

            elif 'datetime' in temp or 'time' in temp:
                if database == 'psql':
                    return 'time'
                elif database == 'mysql':
                    return 'DATETIME'
                elif database == 'oracle':
                    return 'DATE'
                elif database == 'mssql':
                    return 'varchar(64)'

            else:
                if database == 'psql' or database == 'mssql':
                    return 'varchar(32)'
                elif database == 'mysql':
                    return 'text'
                elif database == 'oracle':
                    return 'VARCHAR2'

    def change_to_correct_type(self, sql_type, database):

        psql_types_dict = {'string':'varchar(32)', 'int':'integer', 'float':'real', 'double':'double precision',
                          'date':'date','datetime':'time','timestamp':'timestamp'}

        mysql_types_dict = {'string':'text', 'int':'INT', 'float':'FLOAT','double':'DOUBLE','date':'DATE',
                            'datetime':'DATETIME', 'timestamp':'TIMESTAMP'}

        oracle_types_dict = {'string':'VARCHAR2', 'int':'NUMBER', 'float':'NUMBER','double':'NUMBER','date':'DATE',
                             'datetime':'DATE', 'timestamp':'TIMESTAMP'}

        mssql_types_dict = {'string':'varchar(32)', 'int':'int','float':'real','double':'float','date':'varchar(64)',
                            'datetime':'varchar(64)','timestamp':'rowversion'}

        if database == 'psql':
            return psql_types_dict[sql_type]
        elif database == 'mysql':
            return mysql_types_dict[sql_type]
        elif database == 'oracle':
            return oracle_types_dict[sql_type]
        else:
            return mssql_types_dict[sql_type]


    ''' step two: user confirmed type, and all types are correct'''
    def generate_ddl(self, dict, database):

        self.database = database

        if database == 'psql':
            self.reserved_keywords = self.psql_keywords
        elif database == 'mysql':
            self.reserved_keywords = self.mysql_keywords
        elif database == 'oracle':
            self.reserved_keywords = self.oracle_keywords
        elif database == 'mssql':
            self.database = database
            self.reserved_keywords = self.mssql_keywords
        else:
            raise Exception('unsupported database management system: ' + database)

        self.generate_create_table_queries(dict)
        return self.ddl_list


    def generate_create_table_queries(self, dict):

        entities_list = dict['entity']
        relations_list = dict['relation']

        attr_name_counter_dict = {}
        not_combinable_relations = []
        recursive_relations = []
        combinable_recursive_relation_dict = {}
        entity_combinable_relation_dict = {}

        for relation_dict in relations_list:
            not_combinable_relations, recursive_relations = self.check_for_same_attribute_names_relationships(relation_dict, attr_name_counter_dict, not_combinable_relations, recursive_relations)
            entity_combinable_relation_dict, combinable_recursive_relation_dict = self.search_for_combinable_relations(relation_dict, combinable_recursive_relation_dict, entity_combinable_relation_dict, not_combinable_relations, recursive_relations)

        for entity_dict in entities_list:
            self.check_for_same_attribute_names_entity(entity_dict, attr_name_counter_dict)

        for entity_dict in entities_list:
            self.merge_entity_and_relationships(entity_dict, combinable_recursive_relation_dict, entity_combinable_relation_dict)
            self.ddl_list.append(self.create_table_for_entity(entity_dict, entities_list, relations_list))

        for relation_dict in relations_list:
            if 'processed' in relation_dict and relation_dict['processed']=='True':
                '''print 'relation alr processed ' + str(count)'''
                pass
            else:
                self.ddl_list.append(self.create_table_for_relationship(relation_dict))


    def check_for_same_attribute_names_relationships(self, dict, counter_dict, not_combinable_relation, recursive_relation):

        participating_entities_count = 0
        is_weak_relationship = False

        relationship_name = dict['name'].strip()
        relationship_id = dict['id']
        attr_dict_list = dict['attribute']

        for attr_dict in attr_dict_list:
            if 'entity_id' in attr_dict:
                participating_entities_count = participating_entities_count + 1

            elif 'relation_id' in attr_dict:
                is_weak_relationship = True

            elif 'name' in attr_dict:
                attr_name = attr_dict['name'].strip()
                if attr_name in counter_dict:
                    attr_dict['name'] = relationship_name + "_" + attr_name
                    counter_dict[attr_name] = counter_dict[attr_name] + 1
                else:
                    counter_dict[attr_name] = 1

            else:
                pass

        if is_weak_relationship == True:
            not_combinable_relation.append(relationship_id)
            self.weak_entity_relationship_id_list.append(relationship_id)

        elif participating_entities_count > 2:
            not_combinable_relation.append(relationship_id)

        elif participating_entities_count == 1 and is_weak_relationship == False:
            recursive_relation.append(relationship_id)

        else:
            pass

        return not_combinable_relation, recursive_relation


    def search_for_combinable_relations(self, relation_dict, combinable_recursive_relation_dict, entity_combinable_relation_dict, not_combinable_relations, recursive_relations):

        found = False
        lst = []
        relationship_id = relation_dict['id']

        if relationship_id not in not_combinable_relations:
            attr_dict_list = relation_dict['attribute']

            if relationship_id not in recursive_relations:
                ''' 1-1 total participation or one-many'''
                entity_one_dict = attr_dict_list[0]
                entity_two_dict = attr_dict_list[1]
                if 'min_participation' in entity_one_dict and 'max_participation' in entity_one_dict and 'min_participation' in entity_two_dict and 'max_participation' in entity_two_dict:
                    one_min = entity_one_dict['min_participation']
                    one_max = entity_one_dict['max_participation']
                    two_min = entity_two_dict['min_participation']
                    two_max = entity_two_dict['max_participation']

                    if one_min=='0' and one_max=='1' and two_min=='1' and two_max=='1':
                        entity_id = entity_two_dict['entity_id']
                        foreign_entity_id = entity_one_dict['entity_id']
                        found = True

                    elif one_min=='1' and one_max=='1':
                        if two_min=='0' and two_max =='1' or two_min=='1' and two_max=='1':
                            entity_id = entity_one_dict['entity_id']
                            foreign_entity_id = entity_two_dict['entity_id']
                            found = True

                    elif one_min.isdigit() and int(one_min)<=1 and one_max=='1':
                        if two_min.isdigit() and int(two_min)<=1 and two_max=='N':
                            entity_id = entity_two_dict['entity_id']
                            foreign_entity_id = entity_one_dict['entity_id']
                            found = True

                    elif one_min.isdigit() and int(one_min)<=1 and one_max=='N':
                        if two_min.isdigit() and int(two_min)<=1 and two_max=='1':
                            entity_id = entity_one_dict['entity_id']
                            foreign_entity_id = entity_one_dict['entity_id']
                            found = True

                    else:
                        found = False

                    if found == True:
                        relationship_name = relation_dict['name']
                        relation_dict['processed'] = 'True'

                        for i in range(2, len(attr_dict_list)):
                            if 'name' in attr_dict_list[i] and 'type' in attr_dict_list[i]:
                                lst.append({'name': attr_dict_list[i]['name'], 'type': attr_dict_list[i]['type']})

                        entity_combinable_relation_dict[entity_id] =  {'name':relationship_name, 'attribute':lst, 'foreign_entity_id': foreign_entity_id, 'relationship_id':relationship_id}

            else:
                entity_one_dict = attr_dict_list[0]
                relationship_name = relation_dict['name']
                relation_dict['processed'] = 'True'

                for i in range(1, len(attr_dict_list)):
                    if 'name' in attr_dict_list[i] and 'type' in attr_dict_list[i]:
                        lst.append({'name': attr_dict_list[i]['name'], 'type': attr_dict_list[i]['type']})
                combinable_recursive_relation_dict[entity_one_dict['entity_id']] = {'name':relationship_name, 'attribute':lst}

        return entity_combinable_relation_dict, combinable_recursive_relation_dict


    def check_for_same_attribute_names_entity(self,entity_dict, attr_name_counter_dict):

        entity_name = entity_dict['name'].strip()
        attr_dict_list = entity_dict['attribute']

        for attr_dict in attr_dict_list:

            if 'name' in attr_dict:
                attr_name = attr_dict['name'].strip()
                if attr_name in attr_name_counter_dict:
                    attr_dict['name'] = entity_name + "_" + attr_name
                    attr_name_counter_dict[attr_name] = attr_name_counter_dict[attr_name] + 1
                else:
                    attr_name_counter_dict[attr_name] = 1

    def merge_entity_and_relationships(self, entity_dict, combinable_recursive_relation_dict, entity_combinable_relation_dict):
        entity_id = entity_dict['id']
        entity_name = entity_dict['name']

        if entity_id in combinable_recursive_relation_dict:

            relationship_name = combinable_recursive_relation_dict[entity_id]['name']
            relationship_attr_dict_list = combinable_recursive_relation_dict[entity_id]['attribute']

            primary_key_attr_id = entity_dict['key'][0][0]
            attr_dict_list = entity_dict['attribute']
            primary_key_attr_dict = attr_dict_list[int(primary_key_attr_id)-1]
            primary_key_name = primary_key_attr_dict['name']
            primary_key_type = primary_key_attr_dict['type']

            next_id = len(attr_dict_list)
            attr_dict_list.append({'id':str(next_id), 'name': relationship_name + "_" + primary_key_name, 'type':primary_key_type,
                                   'reference': 'REFERENCES '+ entity_name + "_" +relationship_name + ' (' + primary_key_name + ')'})
            next_id = next_id + 1

            for relationship_attr_dict in relationship_attr_dict_list:
                attr_dict_list.append({'id':str(next_id), 'name':relationship_attr_dict['name'], 'type':relationship_attr_dict['type']})

            entity_dict['attribute'] = attr_dict_list
            entity_dict['name'] = entity_name + '_' + relationship_name

        elif entity_id in entity_combinable_relation_dict:

            relationship_name = entity_combinable_relation_dict[entity_id]['name']
            entity_dict['name'] = entity_dict['name'] + "_" + relationship_name

            relationship_attr_dict_list = entity_combinable_relation_dict[entity_id]['attribute']
            entity_attr_dict_list = entity_dict['attribute']
            next_id = len(entity_attr_dict_list)

            for relationship_attr_dict in relationship_attr_dict_list:
                entity_attr_dict_list.append({'id':str(next_id), 'name':relationship_attr_dict['name'], 'type': relationship_attr_dict['type']})
                next_id = next_id + 1

            foreign_entity_id = entity_combinable_relation_dict[entity_id]['foreign_entity_id']
            entity_attr_dict_list.append({'id': next_id, 'foreign_entity_id': foreign_entity_id})

        else:
            pass

    def create_table_for_entity(self, entity_dict, entities_list, relations_list):

        table_name = entity_dict['name']
        self.check_for_keyword(table_name)
        ddl = "CREATE TABLE " + table_name.strip().replace(" ", "_") + " (\n"

        entity_id = entity_dict['id']
        self.entity_id_name_dict[entity_id] = table_name.strip()

        attribute_list = entity_dict['attribute']
        attr_id_to_name_dict = {}
        unique_str = ""

        for attribute_dict in attribute_list:
            id = attribute_dict['id']

            if 'name' in attribute_dict:
                ddl = self.get_entity_attr_name_type(attr_id_to_name_dict, attribute_dict, ddl, id)

            elif 'foreign_entity_id' in attribute_dict:
                ddl = self.handle_merged_relationship(attribute_dict, entities_list, relations_list, ddl)

            elif 'relation_id' in attribute_dict:
                ddl = self.handle_weak_entity_relationship(attr_id_to_name_dict, attribute_dict, ddl, entity_id, id,
                                                           relations_list)
            else:
                pass

        ddl, foreign_key_str, foreign_key_str_list, primary_key_str, unique_str = self.find_primary_foreign_keys(
            attr_id_to_name_dict, ddl, entity_dict, table_name, unique_str, entities_list)

        if primary_key_str != "":
            ddl += primary_key_str

        if unique_str != "":
            ddl += unique_str

        if foreign_key_str != "":
            for str in foreign_key_str_list:
                ddl += str

        ddl = ddl[:-2]
        ddl += "\n);"

        print '\n'
        print ddl
        print '\n'

    def get_entity_attr_name_type(self, attr_id_to_name_dict, attribute_dict, ddl, id):

        attr_name = attribute_dict['name']
        self.check_for_keyword(attr_name)
        attr_type = attribute_dict['type']
        self.check_type_validity(attr_type)

        attr_name_type_pair = []
        attr_name_type_pair.append(attr_name)
        attr_name_type_pair.append(attr_type)

        if 'reference' in attribute_dict:
            ddl += "    " + attr_name.strip().replace(" ", "_") + " " + attr_type + " " + attribute_dict['reference'] + ",\n"
        else:
            ddl += "    " + attr_name.strip().replace(" ", "_") + " " + attr_type + ",\n"

        attr_id_to_name_dict[id] = attr_name_type_pair
        return ddl

    def handle_merged_relationship(self, attribute_dict, entities_list, relations_list, ddl):

        foreign_identity_id = attribute_dict['foreign_entity_id']

        for entity_dict in entities_list:

            if entity_dict['id'] == foreign_identity_id:
                foreign_entity_name = entity_dict['name']
                primary_key_attr_name_list, primary_key_attr_type_list = self.find_primary_keys_name_type(entity_dict, entities_list, relations_list)

                for i in range(0, len(primary_key_attr_name_list)):
                    name = primary_key_attr_name_list[i]
                    type = primary_key_attr_type_list[i]

                    ddl += "    " + name + " " + type + " REFERENCES " + foreign_entity_name + " (" + name + "),\n"

                break

        return ddl

    def find_primary_keys_name_type(self, entity_dict, entities_list, relations_list):
        name_list = []
        type_list = []
        entity_id = entity_dict['id']

        primary_keys_list = entity_dict['key'][0]
        attr_dict_list = entity_dict['attribute']
        for attr_id in primary_keys_list:
            for attr_dict in attr_dict_list:
                if attr_dict['id'] == attr_id:

                    if 'name' in attr_dict:
                        name_list.append(attr_dict['name'])
                        type_list.append(attr_dict['type'])

                    elif 'relation_id' in attr_dict:
                        for relation_dict in relations_list:
                            if relation_dict['id'] in self.weak_entity_relationship_id_list:
                                relation_attr_dict_list = relation_dict['attribute']
                                if relation_attr_dict_list[2]['relation_id'] == attr_dict['relation_id']:
                                    if relation_attr_dict_list[0]['entity_id'] == entity_id:
                                        strong_entity_id = relation_attr_dict_list[1]['entity_id']
                                    else:
                                        strong_entity_id =relation_attr_dict_list[0]['entity_id']

                                    strong_name_list, strong_type_list = self.find_primary_keys_name_type(entities_list[strong_entity_id-1], entities_list, relations_list)
                                    for i in range(0, len(strong_name_list)):
                                        name_list.append(strong_name_list[i])
                                        type_list.append(strong_type_list[i])

                                    break

        return name_list, type_list


    def find_primary_foreign_keys(self, attr_id_to_name_dict, ddl, entity_dict, table_name, unique_str, entities_list):
        primary_key_str = ""
        foreign_key_str = ""
        foreign_key_str_list = []
        key_list = entity_dict['key']

        if len(key_list) > 0:
            primary_key_str = "    PRIMARY KEY ("
            primary_key_attr_list = key_list[0]
            primary_key_name_list = []
            key_type_pair = []
            foreign_key_str_list = []

            for attr in primary_key_attr_list:
                if attr in attr_id_to_name_dict:
                    if attr_id_to_name_dict[attr][0].isdigit() == False:
                        primary_key_str += attr_id_to_name_dict[attr][0].strip().replace(" ", "_") + ", "
                        primary_key_name_list.append(attr_id_to_name_dict[attr])
                    else:
                        attr_name_list, attr_type_list = self.get_strong_entity_keys(attr_id_to_name_dict[attr][0], entities_list)
                        foreign_key_str = "    FOREIGN KEY ("
                        for i in range(0, len(attr_name_list)):
                            ddl += "    " + attr_name_list[i].strip().replace(" ", "_") + " " + attr_type_list[
                                i] + ",\n"
                            foreign_key_str += attr_name_list[i].strip().replace(" ", "_") + ", "
                            key_type_pair.append(attr_name_list[i])
                            key_type_pair.append(attr_type_list[i])
                            primary_key_name_list.append(key_type_pair)
                        foreign_key_str = foreign_key_str[:-2]
                        foreign_key_str += ") REFERENCES " + self.strong_entity_name.strip().replace(" ", "_") + " ("
                        for attr_name in attr_name_list:
                            foreign_key_str += attr_name.strip().replace(" ", "_") + ", "
                            primary_key_str += attr_name.strip().replace(" ", "_") + ", "
                        foreign_key_str = foreign_key_str[:-2]
                        foreign_key_str += "),\n"
                        foreign_key_str_list.append(foreign_key_str)

            primary_key_str = primary_key_str[:-2]
            primary_key_str += "),\n"
            self.table_primary_key_dict[table_name] = primary_key_name_list

            for i in range(1, len(key_list)):
                unique_str = "    UNIQUE ("
                unique_attr_list = key_list[i]

                foreign_key_str = "    FOREIGN KEY ("
                foreign_key_list = []

                for attr in unique_attr_list:
                    count = 0

                    if attr in attr_id_to_name_dict:
                        if attr_id_to_name_dict[attr][0].isdigit() == False:
                            count = count + 1

                            if count == len(unique_attr_list):
                                raise Exception('another key: all attributes have name')

                            unique_str += attr_id_to_name_dict[attr][0].strip().replace(" ", "_") + ", "

                        else:
                            attr_name_list, attr_type_list = self.get_strong_entity_keys(attr_id_to_name_dict[attr][0], entities_list)
                            for j in range(0, len(attr_name_list)):
                                attr_name = attr_name_list[j]
                                attr_type = attr_type_list[j]
                                ddl += "    " + attr_name.strip().replace(" ", "_") + " " + attr_type + ",\n"
                                unique_str += attr_name.strip().replace(" ", "_") + ", "

                                foreign_key_list.append(attr_name)

                            unique_str = unique_str[:-2]
                            unique_str += "),\n"

                for foreign_key in foreign_key_list:
                    foreign_key_str += foreign_key.strip().replace(" ", "_") + ", "
                foreign_key_str = foreign_key_str[:-2]
                foreign_key_str += ") REFERENCES " + self.strong_entity_name.strip().replace(" ", "_") + " ("

                for foreign_key in foreign_key_list:
                    foreign_key_str += foreign_key.strip().replace(" ", "_") + ", "
                foreign_key_str = foreign_key_str[:-2]
                foreign_key_str += "),\n"
                foreign_key_str_list.append(foreign_key_str)
        return ddl, foreign_key_str, foreign_key_str_list, primary_key_str, unique_str

    def handle_weak_entity_relationship(self, attr_id_to_name_dict, attribute_dict, ddl, entity_id, id, relations_list):
        relation_id = attribute_dict['relation_id']
        temp_lst = []
        temp_lst.append(relation_id)
        attr_id_to_name_dict[id] = temp_lst
        for relation_dict in relations_list:
            relation_attr_dict_list = relation_dict['attribute']

            j = 0
            while j < len(relation_attr_dict_list):
                relation_attr_dict = relation_attr_dict_list[j]

                if 'relation_id' in relation_attr_dict and relation_attr_dict['relation_id'] == relation_id:
                    self.strong_entity_id = self.get_strong_entity_id(relation_attr_dict_list, j, entity_id)
                    self.weak_entity_relationship_dict[relation_id] = self.strong_entity_id

                    j = j + 1
                    while j < len(relation_attr_dict_list):
                        relation_attr_dict = relation_attr_dict_list[j]

                        if 'name' in relation_attr_dict:
                            relation_attr_name = relation_attr_dict['name']
                            self.check_for_keyword(relation_attr_name)
                            relation_attr_type = relation_attr_dict['type']
                            ddl += "    " + relation_attr_name.strip().replace(" ", "_") + " " + relation_attr_type + ",\n"
                        j = j + 1

                    relation_dict['processed'] = 'True'
                else:
                    j = j + 1
        return ddl

    def get_strong_entity_id(self, relation_attr_dict_list, cur_index, weak_entity_id):

        index = cur_index - 1
        while index >=0:
            dict = relation_attr_dict_list[index]
            if 'entity_id' in dict:
                if dict['entity_id'] != weak_entity_id:
                    strong_entity_id = dict['entity_id']
                    break
            index = index - 1

        return strong_entity_id

    def get_strong_entity_keys(self, relation_id, entities_list):
        strong_entity_id = self.weak_entity_relationship_dict[relation_id]
        if strong_entity_id != '-1':
            strong_entity_dict = entities_list[int(strong_entity_id)-1]

            if 'id' in strong_entity_dict and strong_entity_dict['id'] == strong_entity_id:

                if 'name' in strong_entity_dict:
                    self.strong_entity_name = strong_entity_dict['name']
                    self.check_for_keyword(self.strong_entity_name)

                if self.strong_entity_name in self.table_primary_key_dict:
                    primary_key_type_list = self.table_primary_key_dict[self.strong_entity_name]
                    key_name_list = []
                    key_type_list = []
                    for pair in primary_key_type_list:
                        key_name_list.append(pair[0])
                        key_type_list.append(pair[1])

                else:
                    strong_entity_key_list = strong_entity_dict['key']
                    if len(strong_entity_key_list) != 0:
                        key_name_list = []
                        key_type_list = []

                        strong_entity_primary_key_list = strong_entity_key_list[0]
                        strong_entity_attr_dict_list = strong_entity_dict['attribute']
                        for key in strong_entity_primary_key_list:
                            key_name_list.append(strong_entity_attr_dict_list[int(key)-1]['name'])
                            key_type_list.append(strong_entity_attr_dict_list[int(key)-1]['type'])

        return key_name_list, key_type_list

    def create_table_for_relationship(self,relation_dict):

        entities_id_list=[]
        relationship_attr_type_pair_list = []
        foreign_key_list = []

        relation_attr_list = relation_dict['attribute']

        for attr_dict in relation_attr_list:
            if 'entity_id' in attr_dict:
                entities_id_list.append(attr_dict['entity_id'])
            else:
                if 'name' in attr_dict:
                    pair = []
                    self.check_for_keyword(attr_dict['name'])
                    pair.append(attr_dict['name'])
                    self.check_type_validity(attr_dict['type'])
                    pair.append(attr_dict['type'])
                    relationship_attr_type_pair_list.append(pair)

        relationship_name = relation_dict['name']
        self.check_for_keyword(relationship_name)

        ddl = 'CREATE TABLE ' + relationship_name.strip().replace(" ", "_") + ' (\n'
        for pair in relationship_attr_type_pair_list:
            ddl += "    " + pair[0].strip().replace(" ", "_") + " " + pair[1] + ",\n"

        primary_key_str = "    PRIMARY KEY ("
        for id in entities_id_list:
            if id in self.entity_id_name_dict:
                entity_name = self.entity_id_name_dict[id]
                if entity_name in self.table_primary_key_dict:
                    foreign_key_str = "    FOREIGN KEY ("
                    primary_key_list = self.table_primary_key_dict[entity_name]
                    for pair in primary_key_list:
                        ddl += "    " + pair[0].strip().replace(" ", "_") + " " + pair[1] + ",\n"
                        primary_key_str += pair[0].strip().replace(" ", "_") + ", "
                        foreign_key_str += pair[0].strip().replace(" ", "_") + ", "

                    foreign_key_str = foreign_key_str[:-2]
                    foreign_key_str += ") REFERENCES " + entity_name + " ("
                    for pair in primary_key_list:
                        foreign_key_str += pair[0].strip().replace(" ", "_") + ", "
                    foreign_key_str = foreign_key_str[:-2]
                    foreign_key_str += "),\n"
                    foreign_key_list.append(foreign_key_str)

        primary_key_str = primary_key_str[:-2]
        primary_key_str += "),\n"

        ddl += primary_key_str
        for str in foreign_key_list:
            ddl += str

        ddl = ddl[:-2]
        ddl += "\n);"
        print ddl
        return ddl

    def check_for_keyword(self, str):
        temp = str + " "
        if temp.strip().upper() in self.reserved_keywords:
            raise Exception('name cannot be reserved keyword: ' + str)

    def check_type_validity(self, type):

        psql_valid_types = {'varchar()', 'integer', 'real', 'double precision', 'date', 'time', 'timestamp'}
        mysql_valid_types = {'text', 'int', 'integer','float','double','date','datetime','timestamp'}
        oracle_valid_types = {'varchar2','number','date','timestamp'}
        mssql_valid_types = {'varchar()', 'rowversion','int','float','real'}

        temp = type + " "
        temp = temp.strip().lower()

        if self.database == 'mysql':
            if temp not in mysql_valid_types:
                raise Exception('invalid data type for mysql: ' + type)
        elif self.database == 'oracle':
            if temp not in oracle_valid_types:
                raise Exception('invalid data type for oracle: ' + type)
        else:
            open_bracket = re.search(r'\(', temp)
            if open_bracket:
                index_open = open_bracket.start()

                close_bracket = re.search(r'\)', temp)
                if close_bracket:
                    index_close = close_bracket.start()
                else:
                    raise Exception('invalid data type for ' + self.database + ': ' + type)

                temp = temp[0:index_open+1] + temp[index_close:]

            if self.database == 'psql':
                if temp not in psql_valid_types:
                    raise Exception('invalid data type for psql: ' + type)
            elif self.database == 'mssql':
                if temp not in mssql_valid_types:
                    raise Exception('invalid data type for mssql: ' + type)


    def __init__(self):

        self.ddl_list = []
        self.weak_entity_relationship_id_list = []
        self. weak_entity_relationship_dict = {}
        self.strong_entity_id = '-1'
        self.strong_entity_name = ''
        self.entity_id_name_dict = {}
        self.table_primary_key_dict={}
        self.database = ''

        self.reserved_keywords = []
        self.psql_keywords = ['ALL','ANALYSE','ANALYZE','AND','ANY','AS','ASC','AUDIT','BETWEEN',
                              'BINARY','BOTH','CASE','CAST','CHECK','COLLATE','COLUMN','CONSTRAINT','CREATE','CROSS',
                              'CURRENT_DATE', 'CURRENT_ROLE','CURRENT_TIME','CURRENT_TIMESTAMP','CURRENT_USER','DEFAULT',
                              'DEFERRABLE','DESC','DISTINCT','DO','ELSE','END','EXCEPT','FALSE','FOR','FOREIGN','FREEZE',
                              'FROM','FULL','GRANT','GROUP','HAVING','ILIKE','IN','INITIALLY','INNER','INTERSECT','INTO',
                              'IS','ISNULL','JOIN','LEADING','LEFT','LIKE','LIMIT','LOCALTIME','LOCALTIMESTAMP','NATURAL',
                              'NEW','NOT','NOTNULL','RESERVED','OFF','OFFSET','OLD','ON','ONLY','OR','ORDER','OUTER','OVERLAPS',
                              'PLACING','PRIMARY','REFERENCES','RIGHT','SELECT','SESSION_USER','SIMILAR','SOME','SYMMETRIC',
                              'TABLE','THEN','TO','TRAILING','TRUE','UNION','UNIQUE','USER','USING','WHEN','WHERE']

        self.mysql_keywords = ['ADD','ALL','ALTER','ANALYZE','AND','AS','ASC','AUTO_INCREMENT','BDB','BERKELEYDB','BETWEEN','BIGINT','BINARY',
                              'BLOB','BOTH','BTREE','BY','CASCADE','CASE','CHANGE','CHAR','CHARACTER','CHECK','COLLATE','COLUMN','COLUMNS','CONSTRAINT',
                              'CREATE','CROSS','CURRENT_DATE','CURRENT_TIME','CURRENT_TIMESTAMP','DATABASE','DATABASES','DAY_HOUR','DAY_MINUTE','DAY_SECOND',
                              'DEC','DECIMAL','DEFAULT','DELAYED','DELETE','DESC','DESCRIBE','DISTINCT','DISTINCTROW','DIV','DOUBLE','DROP','ELSE','ENCLOSED',
                              'ERRORS','ESCAPED','EXISTS','EXPLAIN','FALSE','FIELDS','FLOAT','FOR','FORCE','FOREIGN','FROM','FULLTEXT','FUNCTION','GEOMETRY',
                              'GRANT','GROUP','HASH','HAVING','HELP','HIGH_PRIORITY','HOUR_MINUTE','HOUR_SECOND','IF','IGNORE','IN','INDEX','INFILE','INNER',
                              'INNODB','INSERT','INT','INTEGER','INTERVAL','INTO','IS','JOIN','KEY','KEYS','KILL','LEADING','LEFT','LIKE','LIMIT','LINES','LOAD',
                              'LOCALTIME','LOCALTIMESTAMP','LOCK','LONG','LONGBLOB','LONGTEXT','LOW_PRIORITY','MASTER_SERVER_ID','MATCH','MEDIUMBLOB','MEDIUMINT',
                              'MEDIUMTEXT','MIDDLEINT','MINUTE_SECOND','MOD','MRG_MYISAM','NATURAL','NOT','NULL','NUMERIC','ON','OPTIMIZE','OPTION','OPTIONALLY',
                              'OR','ORDER','OUTER','OUTFILE','PRECISION','PRIMARY','PRIVILEGES','PROCEDURE','PURGE','READ','REAL','REFERENCES','REGEXP','RENAME',
                              'REPLACE','REQUIRE','RESTRICT','RETURNS','REVOKE','RIGHT','RLIKE','RTREE','SELECT','SET','SHOW','SMALLINT','SOME','SONAME','SPATIAL',
                              'SQL_BIG_RESULT','SQL_CALC_FOUND_ROWS','SQL_SMALL_RESULT','SSL','STARTING','STRAIGHT_JOIN','STRIPED','TABLE','TABLES','TERMINATED',
                              'THEN','TINYBLOB','TINYINT','TINYTEXT','TO','TRAILING','TRUE','TYPES','UNION','UNIQUE','UNLOCK','UNSIGNED','UPDATE','USAGE','USE',
                              'USER_RESOURCES','USING','VALUES','VARBINARY','VARCHAR','VARCHARACTER','VARYING','WARNINGS','WHEN','WHERE','WITH','WRITE','XOR',
                              'YEAR_MONTH','ZEROFILL']

        self.oracle_keywords = ['ACCESS','ADD','ALL','ALTER','AND','ANY','AS','ASC','AT','AUDIT','BETWEEN','BY','CHAR',
                                'CHECK','CLUSTER','COLUMN','COMMENT','COMPRESS','CONNECT','CREATE','CURRENT','DATE','DECIMAL',
                                'DEFAULT','DELETE','DESC','DISTINCT','DROP','ELSE','EXCLUSIVE','EXISTS','FILE','FLOAT','FOR',
                                'FROM','GRANT','GROUP','HAVING','IDENTIFIED','IMMEDIATE','IN','INCREMENT','INDEX','INITIAL','INSERT',
                                'INTEGER','INTERSECT','INTO','IS','LEVEL','LIKE','LOCK','LONG','MAXEXTENTS','MINUS','MISLABEL',
                                'MODE','MODIFY','NOAUDIT','NOCOMPRESS','NOT','NOWAIT','NULL','NUMBER','OF','OFFLINE','ON','ONLINE',
                                'OPTION','OR','ORDER','PCTFREE','PRIOR','PRIVILEGES','PUBLIC','RAW','RENAME','RESOURCE','REVOKE','ROW','ROWID',
                                'ROWNUM','ROWS','SELECT','SESSION','SET','SHARE','SIZE','SMALLINT','START','SUCCESSFUL','SYNONYM',
                                'SYSDATE','TABLE','THEN','TO','TRIGGER','UID','UNION','UNIQUE','UPDATE','USER','VALIDATE','VALUES',
                                'VARCHAR','VARCHAR2','VIEW','WHENEVER','WHERE','WITH']

        self.mssql_keywords = ['ADD','EXTERNAL','PROCEDURE','ALL','FETCH','PUBLIC','ALTER','FILE','RAISERROR','AND','FILLFACTOR','READ','ANY','FOR','READTEXT',
                                'AS','FOREIGN','RECONFIGURE','ASC','FREETEXT','REFERENCES','AUTHORIZATION','FREETEXTTABLE','REPLICATION','BACKUP','FROM','RESTORE',
                                'BEGIN','FULL','RESTRICT','BETWEEN','FUNCTION','RETURN','BREAK','GOTO','REVERT','BROWSE','GRANT','REVOKE','BULK','GROUP','RIGHT','BY',
                                'HAVING','ROLLBACK','CASCADE','HOLDLOCK','ROWCOUNT','CASE','IDENTITY','ROWGUIDCOL','CHECK','IDENTITY_INSERT','RULE','CHECKPOINT','IDENTITYCOL',
                                'SAVE','CLOSE','IF','SCHEMA','CLUSTERED','IN','SECURITYAUDIT','COALESCE','INDEX','SELECT','COLLATE','INNER','SEMANTICKEYPHRASETABLE','COLUMN',
                                'INSERT','SEMANTICSIMILARITYDETAILSTABLE','COMMIT','INTERSECT','SEMANTICSIMILARITYTABLE','COMPUTE','INTO','SESSION_USER','CONSTRAINT','IS','SET',
                                'CONTAINS','JOIN','SETUSER','CONTAINSTABLE','KEY','SHUTDOWN','CONTINUE','KILL','SOME','CONVERT','LEFT','STATISTICS','CREATE','LIKE','SYSTEM_USER',
                                'CROSS','LINENO','TABLE','CURRENT','LOAD','TABLESAMPLE','CURRENT_DATE','MERGE','TEXTSIZE','CURRENT_TIME','NATIONAL','THEN','CURRENT_TIMESTAMP','NOCHECK',
                                'TO','CURRENT_USER','NONCLUSTERED','TOP','CURSOR','NOT','TRAN','DATABASE','NULL','TRANSACTION','DBCC','NULLIF','TRIGGER','DEALLOCATE','OF','TRUNCATE','DECLARE',
                                'OFF','TRY_CONVERT','DEFAULT','OFFSETS','TSEQUAL','DELETE','ON','UNION','DENY','OPEN','UNIQUE','DESC','OPENDATASOURCE','UNPIVOT','DISK','OPENQUERY','UPDATE','DISTINCT',
                                'OPENROWSET','UPDATETEXT','DISTRIBUTED','OPENXML','USE','DOUBLE','OPTION','USER','DROP','OR','VALUES','DUMP','ORDER','VARYING','ELSE','OUTER','VIEW','END','OVER','WAITFOR',
                                'ERRLVL','PERCENT','WHEN','ESCAPE','PIVOT','WHERE','EXCEPT','PLAN','WHILE','EXEC','PRECISION','WITH','EXECUTE','PRIMARY','WITHIN GROUP','EXISTS','PRINT','WRITETEXT','EXIT','PROC']


