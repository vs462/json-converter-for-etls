import re
from pandas import json_normalize
from functools import reduce
import operator
import pandas as pd

def merge_keys(dic, sep = '_'):  
    ''' recursive function to keep looping through nested dic values to unpack all '''
    to_return = {}
    for key, value in dic.items():
       if not isinstance(value, dict): 
         to_return[key] = value
       else:
         for merged_key, merged_value in merge_keys(value).items():
           to_return[sep.join((key, merged_key))] = merged_value
    return to_return

def converter(responses, resp_id, loop = False):   
    if type(responses) is list:  
        if loop:
            unpacked_dic = {}
            for single_resp in responses:
                unpacked_dic_i = merge_keys(single_resp, sep ="']['")
                unpacked_dic.update(unpacked_dic_i)
        else:  
            unpacked_dic = merge_keys(responses[0], sep ="']['")
    else:
        unpacked_dic = merge_keys(responses, sep ="']['")   
    final_names =  huginn_names(unpacked_dic, resp_id)    
    return final_names

def huginn_names(unpacked_dic, resp_id):

    ''' final name, type, value formatting '''
    
    final_dic = {}        
    
    for key in unpacked_dic: 
        try:  # check if nested 
            rest = key.split("']")[1] + "']"
        except:
            rest = '' 
            
        h_value = key.split("']")[0] + rest  # turn to key1['key2']['key3'] format
        
        h_key = re.sub(r"^data'\]\['", '', key).replace("['", "_") # remove word 'data' if it's added      
        h_key = re.sub(r'[^0-9a-zA-Z_ ]+', '', h_key).replace(" ", "_").lower() # remove any special charachters 
        
        final_dic[h_key] = {}        
        final_dic[h_key]['type'] = 'text'           
        final_dic[h_key]['name'] = h_key.replace("_", " ").title()  
        
        if type(unpacked_dic[key]) is list:
            h_value = h_value +  " | split: ',' | as_object "
        final_dic[h_key]['value']= '{{' + h_value + '}}'
    
    if resp_id:
        try: # rename 'id' column (if exists) with 'response_id'
            final_dic['response_id'] = final_dic.pop('id')
            final_dic['response_id']['name']='Response Id'
        except:
            pass
    return final_dic


def convert_to_table(responses):    
    normalized_df = json_normalize(responses)
    col_names = []
    for col in normalized_df.columns:
        new_col = col.replace('data.', '')
        #new_col = re.sub(r'(?<!^)(?=[A-Z])', '_', new_col).lower()
        new_col = re.sub(r'[^0-9a-zA-Z]+', '_', new_col ).lower() 
        new_col = new_col.replace('.', '_')
        
        col_names.append(new_col)
    
    normalized_df.columns = col_names
    return normalized_df


def get_by_path(responses, h_path):    
    key = h_path.strip('{{ | }}')
    key = key.split(' | split')[0]     
    all_vals = []
    if "']" in key: # if nested 
        keys = [key.strip("]").replace("'","") for key in key.split("[")]
     
    for resp in responses:
        try:
            val = reduce(operator.getitem, keys, resp)
        except:
            try:
                val = resp[key]
            except:
                val = None
        all_vals.append(val)
    return all_vals
    
    
def values_investigation(responses, h_path):
    all_vals = get_by_path(responses, h_path)    
    # not sure maybe replace by try later 
    # if any(isinstance(val, list) for val in all_vals):
    #     all_vals = [str(item) for item in all_vals]
    try:
        unique_vals = set(all_vals)
    except:
        all_vals = [str(item) for item in all_vals]
        unique_vals = set(all_vals)
        
    num_unique_vals = len(set(all_vals))
    
    #d = {n: all_vals.count(n) for n in unique_vals}
    dic1 = {}
    for i in unique_vals:
        name = i
        if i =='':
            name ='None'            
        dic1[name] = all_vals.count(i)        
    df_count_vals = pd.DataFrame.from_dict(dic1, columns = ['count'], orient='index')
    return (num_unique_vals, len(all_vals)), df_count_vals
        
        