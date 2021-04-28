import re
import streamlit as st
from pandas.io.json import json_normalize

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


def huginn_names(unpacked_dic):
    ''' final name, type, value formatting '''
    final_dic = {}        
    for key in unpacked_dic:          
        h_value = key        
        h_key = key.replace('.', '_') 
        h_key = re.sub(r'(?<!^)(?=[A-Z])', '_', h_key).lower() # replace camel case by underscore
        final_dic[h_key] = {}        
        final_dic[h_key]['type'] = 'text'        
        final_dic[h_key]['name'] = h_key.replace("_", " ").title()  
        
        if type(unpacked_dic[key]) is list:
            h_value = h_value +  " | split: ',' | as_object "
            
        final_dic[h_key]['value']= '{{ ' + h_value + ' }}'
    try: # rename 'id' column (if exists) with 'response_id'
        final_dic['response_id'] = final_dic.pop('id')
        final_dic['response_id']['name']='Response Id'
    except:
        pass
    return final_dic


def converter(responses, loop = False):   
    if type(responses) is list:            
        unpacked_dic = merge_keys(responses[0], sep ='.')
    else:
        unpacked_dic = merge_keys(responses, sep ='.')
    final_names =  huginn_names(unpacked_dic)
    return final_names


def converter_full(responses):   
    if type(responses) is list:
        unpacked_dic = {}
        for single_resp in responses:
            unpacked_dic_i = merge_keys(single_resp, sep ='.')
            unpacked_dic.update(unpacked_dic_i)
    else:
        unpacked_dic = merge_keys(responses, sep ='.')     
    final_names =  huginn_names(unpacked_dic)
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




