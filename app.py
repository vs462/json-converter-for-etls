import json
import streamlit as st
import pandas as pd
import base64
import converter as cnv

st.set_page_config(layout="wide")
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True) # make buttons display horizontally 

st.markdown('<style>' + open('styles.css').read() + '</style>', unsafe_allow_html=True)
st.title('JSON to Huginn names converter')
  
def initialise():    
    js_upload, jsl_upload, js_raw, csv_upload = 'JSON Upload','JSONL Upload', 'Raw JSON', 'CSV/Excel Upload'
    way_to_add = st.radio("Choose format", (js_upload, jsl_upload, js_raw, csv_upload))
    if way_to_add == js_upload:
        user_file = st.file_uploader("Upload JSON file", type="json")
        if user_file:
            user_filename = user_file.name
            responses = json.load(user_file) 
            load_data(responses)  
            
    elif way_to_add == jsl_upload:
        responses = []
        user_file = st.file_uploader("Upload JSONL file", type="jsonl") 
        if user_file:           
            user_filename = user_file.name
            for json_str in list(user_file) :                
                result = json.loads(json_str)
                responses.append(result)
            load_data(responses) 

    elif way_to_add == js_raw:  
        user_input = st.text_area("Or just paste a response")        
        if user_input:
            user_filename = 'generated_huginn_names'
            try:
                responses = json.loads(user_input)
                load_data(responses)
            except Exception as e:
                st.markdown(f'<p class="error">Wrong JSON format. Error: {e} </p>', unsafe_allow_html=True)        
    else:
        user_file = st.file_uploader("Upload a CSV/Excel file") 
        if user_file:
            user_filename = user_file.name.lower()
            
            if user_filename.split('.')[-1] == 'csv':                
                df_uploaded = pd.read_csv(user_file)
                responses = [resp for resp in df_uploaded.to_dict(orient="records")]
                load_data(responses)
            
            elif (user_filename.split('.')[-1] == 'xls') or (user_filename.split('.')[-1] == 'xlsx'):
                df_uploaded = pd.read_excel(user_file)
                responses = [resp for resp in df_uploaded.to_dict(orient="records")]
                load_data(responses)
            
            else:
                st.warning("you need to upload a csv or excel file.")
            
def add_data_str(responses):   
    """ Add 'data' in front of each response """

    if isinstance(responses, dict):
        print('here')
        new_responses = {'data': responses} 
    else:  
        new_responses = [{'data':resp} for resp in responses]
    

    return new_responses
    
    
def load_data(responses):
    data_load_state = st.text('Loading data...')
    loop = st.checkbox('Loop through all responses (might take a while, otherwise only the first response will be added)')            
    csv = st.checkbox('Add "data" prefix to values')
    resp_id = st.checkbox('Convert "id" to "response_id" (if applicable)')    
    responses = add_data_str(responses) if csv else responses
    hugin_names_result = cnv.converter(responses, loop = loop, resp_id = resp_id)    
    data_load_state.text('Loading data... Done!')      
    st.markdown('<p class="header"> Convert all </p>', unsafe_allow_html=True) 
    
    display_huginn_names(hugin_names_result)
    display_table(responses, hugin_names_result)
    select_keys(responses, hugin_names_result)
    meta_segm(responses, hugin_names_result)
            
def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    b64 = base64.b64encode(object_to_download.encode()).decode() # some strings <-> bytes conversions necessary here    
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def display_huginn_names(object_to_download, file_name = 'huginn_names.json',  download_link_text = 'Click here to download your file'):  
    with st.beta_expander("See full result"):
        st.write(object_to_download)
   
    with st.beta_expander("Download as JSON file"):
            object_to_download = json.dumps(object_to_download)
            tmp_download_link = download_link(object_to_download, file_name, 'Click here to download your file')
            st.markdown(tmp_download_link, unsafe_allow_html=True)
            
@st.cache(suppress_st_warning=True) 
def turn_to_table(responses):
    df = cnv.convert_to_table(responses)
    return df 
                                                        
def display_table(responses, hugin_names_result):  
    st.markdown(' <p class="header">  Convert to a table </p>', unsafe_allow_html=True)
    cov_to_table = st.checkbox('Convert')
    if cov_to_table:
        df = turn_to_table(responses)            
        to_table_container = st.beta_expander('View Table')
        check_names = st.beta_expander('Check names between the table and generated json')          
        df = turn_to_table(responses)        
        if to_table_container:
            tmp_download_link = download_link(df, 'HUGINN_DF.csv', 'Download as csv')
            to_table_container.markdown(tmp_download_link, unsafe_allow_html=True)
            to_table_container.dataframe(df.style)   
            
        if check_names:
            keys = [key for key in hugin_names_result]        
            cols = [col for col in df.columns]        
            missing_json = [key for key in (set(keys) - set(cols))]
            missing_table = [key for key in (set(cols) - set(keys))]
            check_names.markdown(f'Present in json but not in the table: {missing_json}', unsafe_allow_html=True)
            check_names.markdown(f'Present in table not genereted json: {missing_table}', unsafe_allow_html=True)   

def select_keys(responses, hugin_names_result):    
    st.markdown('<p class="header">  Modify keys </p>', unsafe_allow_html=True) 
    mofify_keys = st.radio('', ('No modifications', 'Select keys to exclude', 'Select keys to include'))            
    if mofify_keys =='Select keys to exclude':
        choose_keys(responses, hugin_names_result, include = False)      
    elif mofify_keys =='Select keys to include':
        choose_keys(responses, hugin_names_result, include = True)
              
def choose_keys(responses, hugin_names_result, include):
    prefix = 'include' if include  else 'exclude'         
    selected_keys = []
    all_keys = [key for key in hugin_names_result]
    all_path = [hugin_names_result[key]['value'] for key in hugin_names_result]    
    for key, path in zip(all_keys, all_path):
        select_key = st.checkbox(f'{prefix} "{key}"')
        if select_key:
            selected_keys.append(key)
            expand = st.button(f'view {key}') 
            if expand:
                expand = st.button(f'close {key} view')
                uniques_val, table_counts = cnv.values_investigation(responses, path)                
                st.markdown(f'{uniques_val[0]} unique values out of {uniques_val[1]}', unsafe_allow_html=True) 
                st.dataframe(table_counts)           
    if not include:
        all_keys = [key for key in hugin_names_result]
        selected_keys = list(set(all_keys) - set(selected_keys))
        
    new_dic = { new_key: hugin_names_result[new_key] for new_key in selected_keys }  
    display_huginn_names(new_dic, file_name = 'huginn_names.json')
    #meta_segm(responses, new_dic)

def meta_segm(responses, hugin_names_result): 
    st.markdown('<p class="header">  Split into segments/meta </p', unsafe_allow_html=True) 
    choose_meta = st.radio('', ('No modification', 'Select all', 'Unselect all'))

    if choose_meta == 'Select all' or choose_meta == 'Unselect all': 
        
        all_keys = [key for key in hugin_names_result]
        all_path = [hugin_names_result[key]['value'] for key in hugin_names_result]        
        meta_fields = {}
        segments ={}
        for key, path in zip(all_keys, all_path):    
            st.markdown('<p class="sep-line"> </p>', unsafe_allow_html=True)
            st.markdown(f'<p class="keys-font"> {key}</p>', unsafe_allow_html=True)
            
            display_key = f'{key[:50]}...' if len(key) > 50 else key
            
            radio_name = (f'Meta ({display_key})', f'Segment ({display_key})', f'Exclude ({display_key})') if choose_meta=='Select all' else (f'Exclude ({key})', f'Meta ({key})', f'Segment ({key})')
            met_or_seg = st.radio('', radio_name)
            
            expand2 = st.button(f'expand {display_key}') 
            if expand2:
                expand2 = st.button(f'close  {display_key}')
                uniques_val, table_counts = cnv.values_investigation(responses, path)                
                st.markdown(f'{uniques_val[0]} unique values out of {uniques_val[1]}', unsafe_allow_html=True) 
                st.dataframe(table_counts) 
                
            if met_or_seg == f'Segment ({display_key})':
                segments[key] = hugin_names_result[key]
            else:
                meta_fields[key] = hugin_names_result[key]         
                
        st.markdown('<p class="header"> User Meta </p>', unsafe_allow_html=True)
        # with st.beta_expander("Manually change meta"):                 
        #         meta_fields2 = st.text_area("", meta_fields)  
        
        display_huginn_names(meta_fields, 'huginn_meta.json', 'Download Meta')

        
        st.markdown('<p class="header"> Segments </p>', unsafe_allow_html=True)
        # with st.beta_expander("Manually change segments"):
        #         segments2 = st.text_area("", segments)  
        display_huginn_names(segments, 'huginn_segments.json', 'Download Segments')


initialise()






