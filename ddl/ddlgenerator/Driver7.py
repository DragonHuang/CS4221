''' many-one relationship, merge relationship with the MANY entity'''

from ddlgenerator.DDLGenerator import DDLGenerator

class Driver7():

    def __init__(self):
        dict={}
        entity_list =[]

        entity_one_dict = {}
        entity_one_attr_list = []
        entity_one_attr_list.append({'id':'1', 'name':'ID', 'type': 'datetime'})
        entity_one_attr_list.append({'id':'2', 'name':'Name'})
        entity_one_attr_list.append({'id':'3', 'name':'DOB', 'type':'date'})
        entity_one_dict['attribute'] = entity_one_attr_list
        entity_one_dict['id']='1'
        entity_one_dict['name']='Person'
        entity_one_key_list = []
        entity_one_key_list.append(['1'])
        entity_one_dict['key']=entity_one_key_list

        entity_list.append(entity_one_dict)
        dict['entity']=entity_list

        relation_attr_list = []
        relation_attr_list.append({'max_participation':'N', 'entity_id':'1', 'min_participation':'N'})

        relation_list=[]
        relation_one_dict = {}

        relation_one_dict['attribute']=relation_attr_list
        relation_one_dict['id']='1'
        relation_one_dict['name'] = 'MarriedTo'

        relation_list.append(relation_one_dict)

        dict['relation'] = relation_list

        ddlObject = DDLGenerator()
        new_dict = ddlObject.fill_missing_type(dict, True, 'psql')
        ddlObject.generate_ddl(new_dict, "psql")

if __name__ == "__main__":
        Driver7()
