''' many-one relationship, merge relationship with the MANY entity'''

from ddl.ddlgenerator.DDLGenerator import DDLGenerator

class Driver9():

    def __init__(self):
        dict={}
        entity_list =[]

        entity_one_dict = {}
        entity_one_attr_list = []
        entity_one_attr_list.append({'id':'1', 'name':'name'})
        entity_one_attr_list.append({'id':'2', 'name':'type'})
        entity_one_dict['attribute'] = entity_one_attr_list
        entity_one_dict['id']='1'
        entity_one_dict['name']='A'
        entity_one_key_list = []
        entity_one_key_list.append(['1'])
        entity_one_dict['key']=entity_one_key_list

        entity_list.append(entity_one_dict)
        dict['entity']=entity_list

        relation_list = []

        relation_one_attr_list = []
        relation_one_attr_list.append({'max_participation':'1', 'entity_id':'1', 'min_participation':'1'})
        relation_one_dict = {}
        relation_one_dict['attribute']=relation_one_attr_list
        relation_one_dict['id']='1'
        relation_one_dict['name'] = 'AA'

        relation_two_dict = {}
        relation_two_attr_list = []
        relation_two_attr_list.append({'max_participation': '1', 'entity_id': '1', 'min_participation': '1'})
        relation_two_dict['attribute'] = relation_two_attr_list
        relation_two_dict['id'] = '2'
        relation_two_dict['name'] = 'BB'

        relation_list.append(relation_one_dict)
        relation_list.append(relation_two_dict)
        dict['relation'] = relation_list

        ddlObject = DDLGenerator()
        new_dict = ddlObject.fill_missing_type(dict, True, 'psql')
        list = ddlObject.generate_ddl(new_dict, "psql")

        for element in list:
            print element

if __name__ == "__main__":
        Driver9()
