import re

class DDLGenerator():

    def generate_ddl(self, dict, smart, database):

        if database == 'psql':
            self.database = database
            self.data_types = self.psql_types
            self.data_types_one = self.psql_types_one
            self.data_types_two = self.psql_types_two
            self.reserved_keywords = self.psql_keywords
        elif database == 'oracle':
            self.database = database
            self.data_types = self.oracle_types
            self.data_types_one = self.oracle_types_one
            self.data_types_two = self.oracle_types_two
            self.reserved_keywords = self.oracle_keywords
        elif database == 'mysql':
            self.database = database
            self.data_types = self.mysql_types
            self.data_types_one = self.mysql_types_one
            self.data_types_two = self.mysql_types_two
            self.reserved_keywords = self.mysql_keywords
        elif database == 'sqlserver':
            self.database = database
            self.data_types = self.sqlserver_types
            self.data_types_one = self.sqlserver_types_one
            self.data_types_two = self.sqlserver_types_two
            self.reserved_keywords = self.sqlserver_keywords
        else:
            raise Exception('invalid database management system!')

        self.smart = smart
        self.generate_ddl_default(dict)
        return self.ddl_list

    def generate_ddl_default(self, dict):

        self.entities_list = dict['entity']
        relations_list = dict['relation']
        attr_name_counter_dict = {}

        for relation_dict in relations_list:
            self.check_for_same_attribute_names(relation_dict, attr_name_counter_dict)

        for entity_dict in self.entities_list:
            ''' maybe this step should find all the relationship that could be combined with the entity'''
            self.check_for_same_attribute_names(entity_dict, attr_name_counter_dict)
            self.ddl_list.append(self.create_table_for_entity(entity_dict, relations_list))

        for relation_dict in relations_list:
            if 'processed' in relation_dict and relation_dict['processed']=='True':
                '''print 'relation alr processed ' + str(count)'''
                pass
            else:
                self.ddl_list.append(self.create_table_for_relationship(relation_dict))

    def check_for_same_attribute_names(self, dict, counter_dict):

        relation_or_entity_name = dict['name'].strip()
        attr_dict_list = dict['attribute']

        for attr_dict in attr_dict_list:
            if 'name' in attr_dict:
                attr_name = attr_dict['name'].strip()
                if attr_name in counter_dict:
                    attr_dict['name'] = relation_or_entity_name + "_" + attr_name
                    counter_dict[attr_name] = counter_dict[attr_name] + 1
                else:
                    counter_dict[attr_name] = 1

    def create_table_for_entity(self, entity_dict, relations_list):

        table_name = entity_dict['name']
        self.check_for_keyword(table_name)

        entity_id = entity_dict['id']
        self.entity_id_name_dict[entity_id] = table_name

        ddl = "CREATE TABLE " + table_name.strip().replace(" ","_") + " (\n"
        unique_str = ""
        attribute_list = entity_dict['attribute']
        attr_id_to_name_dict = {}

        for attribute_dict in attribute_list:
            id = attribute_dict['id']

            if 'name' in attribute_dict:
                ddl = self.get_entity_attr_name_type(attr_id_to_name_dict, attribute_dict, ddl, id)

            else:
                ddl = self.handle_weak_entity_relationship(attr_id_to_name_dict, attribute_dict, ddl, entity_id, id,
                                                           relations_list)

        ddl, foreign_key_str, foreign_key_str_list, primary_key_str, unique_str = self.find_primary_foreign_keys(
            attr_id_to_name_dict, ddl, entity_dict, table_name, unique_str)

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

    def find_primary_foreign_keys(self, attr_id_to_name_dict, ddl, entity_dict, table_name, unique_str):
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
                        attr_name_list, attr_type_list = self.get_strong_entity_keys(attr_id_to_name_dict[attr][0])
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
                            attr_name_list, attr_type_list = self.get_strong_entity_keys(attr_id_to_name_dict[attr][0])
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

                            if 'type' in relation_attr_dict:
                                relation_attr_type = self.get_valid_data_type(relation_attr_dict['type'])
                            else:
                                relation_attr_type = self.get_default_type(relation_attr_name)
                            ddl += "    " + relation_attr_name.strip().replace(" ",
                                                                               "_") + " " + relation_attr_type + ",\n"
                        j = j + 1

                    relation_dict['processed'] = 'True'
                else:
                    j = j + 1
        return ddl

    def get_entity_attr_name_type(self, attr_id_to_name_dict, attribute_dict, ddl, id):
        attr_name = attribute_dict['name']
        self.check_for_keyword(attr_name)
        attr_name_type_pair = []
        attr_name_type_pair.append(attr_name)

        if 'type' in attribute_dict:
            type = self.get_valid_data_type(attribute_dict['type'])
        else:
            type = self.get_default_type(attr_name)

        ddl += "    " + attr_name.strip().replace(" ", "_") + " " + type + ",\n"
        attr_name_type_pair.append(type)
        attr_id_to_name_dict[id] = attr_name_type_pair
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

    def get_strong_entity_keys(self, relation_id):
        strong_entity_id = self.weak_entity_relationship_dict[relation_id]
        if strong_entity_id != '-1':
            strong_entity_dict = self.entities_list[int(strong_entity_id)-1]

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
                            if 'type' in strong_entity_attr_dict_list[int(key)-1]:
                                key_type_list.append(self.get_valid_data_type(strong_entity_attr_dict_list[int(key)-1]['type']))
                            else:
                                key_type_list.append(self.get_default_type(strong_entity_attr_dict_list[int(key)-1]['name']))
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

                    if 'type' in attr_dict:
                        pair.append(self.get_valid_data_type(attr_dict['type']))
                    else:
                        pair.append(self.get_default_type(attr_dict['name']))
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

    def get_valid_data_type(self, type):
        temp = type + " "
        temp = temp.strip().lower()

        open_bracket = re.search(r'\(', temp)
        if open_bracket:
            index_open_bracket = open_bracket.start()

            close_bracket = re.search(r'\)', temp)
            if close_bracket:
                index_close_bracket = close_bracket.start()

                comma = re.search(r'\,', temp)
                if comma:
                    index_comma = comma.start()
                    if index_comma >index_open_bracket+1 and index_comma < index_close_bracket - 1:

                        temp = temp[0:index_open_bracket]
                        if temp in self.data_types_two:
                            return type
                        else:
                            return self.get_default_type("")
                    else:
                        return self.get_default_type("")
                else:
                    temp = temp[0:index_open_bracket]
                    if temp in self.data_types_one:
                        return type
                    else:
                        return self.get_default_type("")
            else:
                return self.get_default_type("")
        else:
            if type in self.data_types:
                return type
            else:
                return self.get_default_type("")

    def get_default_type(self, attr_name):

        if self.smart == False:
            return 'varchar(32)'
        else:
            temp = attr_name + ""
            temp = temp.lower()
            if 'id' in temp or 'int' in temp or 'integer' in temp or 'num' in temp or 'number' in temp or 'postcode' in temp or 'tel' in temp or 'hp' in temp:
                if self.database == 'psql' or self.database == 'oracle':
                    return 'integer'
                elif self.database == 'mysql':
                    return 'int(10)'
                else:
                    return 'int'

            if 'rating' in temp or 'rate' in temp or 'price' in temp or 'money' in temp or 'salary' in temp or 'cost' in temp:
                if self.database == 'psql':
                    return 'decimal'
                else:
                    return 'decimal(1,1)'

            if 'date' in temp:
                return 'date'

            return 'varchar(32)'

    def check_for_keyword(self, str):
        temp = str + " "
        if temp.strip().upper() in self.reserved_keywords:
            raise Exception('name cannot be reserved keyword: ' + str)

    def __init__(self):

        self.ddl_list = []
        self. weak_entity_relationship_dict = {}
        self.strong_entity_id = '-1'
        self.strong_entity_name = ''
        self.entities_list = []
        self.entity_id_name_dict = {}
        self.table_primary_key_dict={}

        self.smart = False
        self.database = ''
        self.data_types = []
        self.data_types_one = []
        self.data_types_two = []

        self.psql_types = ['bigint','bigserial', 'boolean', 'bool', 'box', 'bytea', 'cidr', 'circle', 'date', 'decimal',
                           'double precision', 'inet', 'integer', 'interval', 'line', 'lseg', 'macaddr', 'money',
                           'numeric', 'path', 'point', 'polygon', 'real', 'smallint', 'serial', 'text', 'time',
                           'timetz', 'timestamp', 'timestamptz', 'tsquery', 'tsvector', 'txid_snapshot', 'uuid', 'xml']
        self.psql_types_one = ['bit', 'bit varying', 'character varying', 'character', 'varchar',  'char',
                               'decimal', 'numeric']
        self.psql_types_two = ['decimal', 'numeric']


        self.oracle_types = ['long', 'raw', 'long raw',  'float', 'integer', 'int', 'smallint', 'real', 'double precision',
                             'date', 'timestamp', 'rowid', 'nclob', 'clob', 'blob', 'bfile']
        self.oracle_types_one = ['char','nchar','nvarchar2', 'varchar2', 'timestamp', 'timestamp with time zone',
                                 'timestamp with local time zone', 'interval year', 'urowid']
        self.oracle_types_two = ['number', 'dec', 'decimal']


        self.mysql_types = [ 'tinytext', 'text', 'blob', 'mediumtext', 'mediumblob', 'longtext', 'longblob', 'set',
                             'date', 'datetime', 'timestamp', 'time', 'year']
        self.mysql_types_one = ['char', 'varchar', 'tinyint', 'smallint', 'mediumint', 'int', 'bigint']
        self.mysql_types_two = ['float', 'double', 'decimal']


        self.sqlserver_types = [ 'text', 'nchar', 'nvarchar', 'ntext', 'bit', 'varbinary', 'image', 'tinyint', 'cursor',
                                 'smallint', 'int', 'bigint', 'smallmoney', 'money',  'real', 'datetime', 'datetime2', 'xml',
                                 'smalldatetime', 'date', 'time', 'datetimeoffset', 'timestamp', 'sql_variant', 'uniqueidentifier', 'table']
        self.sqlserver_types_one = ['char', 'varchar', 'binary', 'varbinary', 'float']
        self.sqlserver_types_two = ['numeric', 'decimal']

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

        self.oracle_keywords = ['ACCESS','ADD','ALL','ALTER','AND','ANY','AS','ASC','AT','AUDIT','BETWEEN','BY','CHAR',
                                'CHECK','CLUSTER','COLUMN','COMMENT','COMPRESS','CONNECT','CREATE','CURRENT','DATE','DECIMAL','DEFAULT','DELETE',
                                'DESC','DISTINCT','DROP','ELSE','EXCLUSIVE','EXISTS','FILE','FLOAT','FOR','FROM','GRANT','GROUP',
                                'HAVING','IDENTIFIED','IMMEDIATE','IN','INCREMENT','INDEX','INITIAL','INSERT','INTEGER','INTERSECT',
                                'INTO','IS','LEVEL','LIKE','LOCK','LONG','MAXEXTENTS','MINUS','MISLABEL','MODE','MODIFY','NOAUDIT',
                                'NOCOMPRESS','NOT','NOWAIT','NULL','NUMBER','OF','OFFLINE','ON','ONLINE','OPTION','OR','ORDER','PCTFREE',
                                'PRIOR','PRIVILEGES','PUBLIC','RAW','RENAME','RESOURCE','REVOKE','ROW','ROWID','ROWNUM','ROWS','SELECT',
                                'SESSION','SET','SHARE','SIZE','SMALLINT','START','SUCCESSFUL','SYNONYM','SYSDATE','TABLE','THEN',
                                'TO','TRIGGER','UID','UNION','UNIQUE','UPDATE','USER','VALIDATE','VALUES','VARCHAR','VARCHAR2','VIEW',
                                'WHENEVER','WHERE','WITH']

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

        self.sqlserver_keywords = ['ADD','EXTERNAL','PROCEDURE','ALL','FETCH','PUBLIC','ALTER','FILE','RAISERROR','AND','FILLFACTOR','READ','ANY','FOR','READTEXT',
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


