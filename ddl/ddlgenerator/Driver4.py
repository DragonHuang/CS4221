''' one ternary relationship with three strong entities '''

from ddl.ddlgenerator.DDLGenerator import DDLGenerator

class Driver4():

    def __init__(self):
        dict={}
        entity_list =[]

        entity_one_dict = {}
        entity_one_attr_list = []
        entity_one_attr_list.append({'type':'string', 'id':'1', 'name':'ItemNumber'})
        entity_one_dict['attribute'] = entity_one_attr_list
        entity_one_dict['id']='1'
        entity_one_dict['name']='ITEM'
        entity_one_key_list = []
        entity_one_key_list.append(['1'])
        entity_one_dict['key']=entity_one_key_list

        entity_two_dict = {}
        entity_two_attr_list = []
        entity_two_attr_list.append({'id':'1', 'name':' WareHouseNumber '})
        entity_two_dict['attribute']=entity_two_attr_list
        entity_two_dict['id']='2'
        entity_two_dict['name']='WAREHOUSE'
        entity_two_key_list=[]
        entity_two_key_list.append(['1'])
        entity_two_dict['key']=entity_two_key_list

        entity_three_dict = {}
        entity_three_attr_list = []
        entity_three_attr_list.append({'id': '1', 'name': 'VendorNumber'})
        entity_three_dict['attribute'] = entity_three_attr_list
        entity_three_dict['id'] = '3'
        entity_three_dict['name'] = 'VENDOR'
        entity_three_key_list = []
        entity_three_key_list.append(['1'])
        entity_three_dict['key'] = entity_three_key_list

        entity_list.append(entity_one_dict)
        entity_list.append(entity_two_dict)
        entity_list.append(entity_three_dict)
        dict['entity']=entity_list

        relation_attr_list = []
        relation_attr_list.append({'max_participation':'N', 'entity_id':'1', 'min_participation':'1'})
        relation_attr_list.append({'max_participation':'N', 'entity_id':'2', 'min_participation':'1'})
        relation_attr_list.append({'max_participation':'N', 'entity_id':'3', 'min_participation':'1'})
        relation_attr_list.append({'name':'QtyShipped ', 'type':'int'})

        relation_list=[]
        relation_one_dict = {}

        relation_one_dict['attribute']=relation_attr_list
        relation_one_dict['id']='1'
        relation_one_dict['name'] = 'Shipment'

        relation_list.append(relation_one_dict)

        dict['relation'] = relation_list

        ddlObject = DDLGenerator()
        new_dict = ddlObject.fill_missing_type(dict, True, 'psql')
        ddlObject.generate_ddl(new_dict, "psql")

if __name__ == "__main__":
        Driver4()


