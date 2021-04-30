import re
#import streamlit as st
from pandas.io.json import json_normalize
import json
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


def huginn_names(unpacked_dic, resp_id = False):
    ''' final name, type, value formatting '''
    final_dic = {}        
    for key in unpacked_dic: 
        try:
            rest = key.split('"]')[1] + '"]'
        except:
            rest = ''
        h_value = key.split('"]')[0] + rest         
        h_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key.replace('"]["', '_') ).lower() # replace camel case by underscore
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


def converter(responses, loop = False, resp_id = False):   
    if type(responses) is list:  
        if loop:
            unpacked_dic = {}
            for single_resp in responses:
                unpacked_dic_i = merge_keys(single_resp, sep ='"]["')
                unpacked_dic.update(unpacked_dic_i)
        else:  
            unpacked_dic = merge_keys(responses[0], sep ='"]["')
    else:
        unpacked_dic = merge_keys(responses, sep ='"]["')
    final_names =  huginn_names(unpacked_dic, resp_id = resp_id)
    return final_names


def convert_to_table(responses):    
    normalized_df = json_normalize(responses)
    col_names = []
    for col in normalized_df.columns:
        new_col = re.sub(r'(?<!^)(?=[A-Z])', '_', col).lower()
        new_col = new_col.replace('.', '_')
        col_names.append(new_col)
    
    normalized_df.columns = col_names
    return normalized_df


def get_by_path(responses, h_path):
    key = h_path.strip('{{ | }}')
    key = key.split(' | split')[0] 
    key = key.replace('data.', '')
    all_vals = []
    if '["' in key:
        keys = [key.strip(']"') for key in key.split('["')]
        for resp in responses:
            try:
                val = reduce(operator.getitem, resp, keys) #get_by_path(resp, keys)
            except:
                val = ''
            all_vals.append(val)
    else:
        all_vals = [resp[key] for resp in responses]

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
    
    print(all_vals)
    #d = {n: all_vals.count(n) for n in unique_vals}
    dic1 = {}
    for i in unique_vals:
        name = i
        if i =='':
            name ='None'
            
        dic1[name] = all_vals.count(i)
        
    df_count_vals = pd.DataFrame.from_dict(dic1, columns = ['count'], orient='index')
    return (num_unique_vals, len(all_vals)), df_count_vals



# tests 
# with open('/Users/vasilisa/Chattermill/cm-datascience-ops/vasilisa/kontist/responses.json', 'r') as convo_id_file:
#          responses_test = json.load(convo_id_file)
         
         
         
# values_investigation(responses_test, '{{ hash }}')         
         
         
         
         
         
         
         
         