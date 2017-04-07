'''test 1 er diagram'''

from ddl.ddlgenerator.DDLGenerator import DDLGenerator

class Driver3():

    def __init__(self):

        dict={}
        entity_list =[]

        entity_one_dict = {}
        entity_one_attr_list = []
        entity_one_attr_list.append({'id':'1', 'name':'email'})
        entity_one_attr_list.append({'id':'2', 'name':'name', 'not_null':'true'})
        entity_one_attr_list.append({'id':'3', 'name':'password','not_null':'true'})
        entity_one_dict['attribute'] = entity_one_attr_list
        entity_one_dict['id']='1'
        entity_one_dict['name']='student'
        entity_one_key_list = []
        entity_one_key_list.append(['1'])
        entity_one_dict['key']=entity_one_key_list
        entity_list.append(entity_one_dict)

        entity_two_dict = {}
        entity_two_attr_list = []
        entity_two_attr_list.append({'id':'1', 'name':'description'})
        entity_two_attr_list.append({'id':'2', 'name':'title'})
        entity_two_attr_list.append({'id':'3', 'name':'code','unique':'true'})
        entity_two_attr_list.append({'id':'4', 'relation_id':'1'})
        entity_two_dict['attribute']=entity_two_attr_list
        entity_two_dict['id']='2'
        entity_two_dict['name']='course'
        entity_two_key_list=[]
        entity_two_key_list.append(['3','4'])
        entity_two_dict['key']=entity_two_key_list
        entity_list.append(entity_two_dict)

        entity_three_dict = {}
        entity_three_attr_list = []
        entity_three_attr_list.append({'id': '1', 'name': 'acronym'})
        entity_three_attr_list.append({'id': '2', 'name': 'address','not_null':'true'})
        entity_three_dict['attribute'] = entity_three_attr_list
        entity_three_dict['id'] = '3'
        entity_three_dict['name'] = 'university'
        entity_three_key_list = []
        entity_three_key_list.append(['1'])
        entity_three_dict['key'] = entity_three_key_list
        entity_list.append(entity_three_dict)

        entity_four_dict = {}
        entity_four_attr_list = []
        entity_four_attr_list.append({'id': '1', 'name': 'id', 'type':'string'})
        entity_four_attr_list.append({'id': '2', 'name': 'content'})
        entity_four_attr_list.append({'id': '3', 'name': 'number', 'type': 'int'})
        entity_four_attr_list.append({'id': '4', 'relation_id': '2'})
        entity_four_dict['attribute'] = entity_four_attr_list
        entity_four_dict['id'] = '4'
        entity_four_dict['name'] = 'unit'
        entity_four_key_list = []
        entity_four_key_list.append(['1'])
        entity_four_key_list.append(['3','4'])
        entity_four_dict['key'] = entity_four_key_list
        entity_list.append(entity_four_dict)

        dict['entity']=entity_list

        relation_list=[]

        relation_one_dict = {}
        relation_one_attr_list = []
        relation_one_attr_list.append({'max_participation': 'N', 'entity_id': '1', 'min_participation': '0'})
        relation_one_attr_list.append({'max_participation': 'N', 'entity_id': '2', 'min_participation': '0'})
        relation_one_attr_list.append({'name': 'date', 'type': 'date', 'not_null':'true'})
        relation_one_dict['attribute']=relation_one_attr_list
        relation_one_dict['id']='1'
        relation_one_dict['name'] = 'register'
        relation_list.append(relation_one_dict)

        relation_two_dict = {}
        relation_two_attr_list = []
        relation_two_attr_list.append({'max_participation': '1', 'entity_id': '2', 'min_participation': '1'})
        relation_two_attr_list.append({'max_participation': 'N', 'entity_id': '3', 'min_participation': '0'})
        relation_two_attr_list.append({'relation_id': '1'})
        relation_two_dict['attribute'] = relation_two_attr_list
        relation_two_dict['id'] = '2'
        relation_two_dict['name'] = 'created'
        relation_list.append(relation_two_dict)

        relation_three_dict = {}
        relation_three_attr_list = []
        relation_three_attr_list.append({'max_participation': 'N', 'entity_id': '2', 'min_participation': '0'})
        relation_three_attr_list.append({'max_participation': '1', 'entity_id': '4', 'min_participation': '1'})
        relation_three_attr_list.append({'relation_id': '2'})
        relation_three_dict['attribute'] = relation_three_attr_list
        relation_three_dict['id'] = '3'
        relation_three_dict['name'] = 'composed'
        relation_list.append(relation_three_dict)

        dict['relation'] = relation_list

        ddlObject = DDLGenerator()
        new_dict = ddlObject.fill_missing_type(dict, True, 'psql')
        list = ddlObject.generate_ddl(new_dict, "psql")
        for element in list:
            print element

if __name__ == "__main__":
        Driver3()
