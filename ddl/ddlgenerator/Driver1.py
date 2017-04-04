''' simple ER diagram, two strong entities with one relationship'''
from ddl.ddlgenerator.DDLGenerator import DDLGenerator

class Driver1():

    def __init__(self):
        dict={}
        entity_list =[]

        entity_one_dict = {}
        entity_one_attr_list = []
        entity_one_attr_list.append({'id':'1', 'name':'Salary'})
        entity_one_attr_list.append({'id':'2', 'name':'Address'})
        entity_one_attr_list.append({'id':'3', 'name':'FirstName'})
        entity_one_attr_list.append({'id':'4', 'name':'LastName'})
        entity_one_dict['attribute'] = entity_one_attr_list
        entity_one_dict['id']='1'
        entity_one_dict['name']='Employee'
        entity_one_key_list = []
        entity_one_key_list.append(['3','4'])
        entity_one_dict['key']=entity_one_key_list

        entity_two_dict = {}
        entity_two_attr_list = []
        entity_two_attr_list.append({'id':'1', 'name':'int'})
        entity_two_attr_list.append({'id':'2', 'name':'Name'})
        entity_two_dict['attribute']=entity_two_attr_list
        entity_two_dict['id']='2'
        entity_two_dict['name']='Department'
        entity_two_key_list=[]
        entity_two_key_list.append(['2'])
        entity_two_dict['key']=entity_two_key_list

        entity_list.append(entity_one_dict)
        entity_list.append(entity_two_dict)
        dict['entity']=entity_list

        relation_attr_list = []
        relation_attr_list.append({'max_participation':'N', 'entity_id':'1', 'min_participation':'1'})
        relation_attr_list.append({'max_participation':'N', 'entity_id':'2', 'min_participation':'1'})
        relation_attr_list.append({'name':'Date'})

        relation_list=[]
        relation_one_dict = {}

        relation_one_dict['attribute']=relation_attr_list
        relation_one_dict['id']='1'
        relation_one_dict['name'] = 'WorkFor'

        relation_list.append(relation_one_dict)

        dict['relation'] = relation_list

        ddlObject = DDLGenerator()
        new_dict = ddlObject.fill_missing_type(dict, True, 'psql')
        ddlObject.generate_ddl(new_dict, "psql")

if __name__ == "__main__":
        Driver1()
