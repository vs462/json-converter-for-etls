import json
import streamlit as st
import pandas as pd
import base64
import converter as cnv

st.set_page_config(layout="wide")
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
st.markdown("""
<style>
.small-font {
    font-size:200px !important;
}
</style>
""", unsafe_allow_html=True)

st.title('JSON to Huginn names converter')
   
def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    b64 = base64.b64encode(object_to_download.encode()).decode() # some strings <-> bytes conversions necessary here    
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def display_huginn_names(hugin_names_result):    
    with st.beta_expander("See full result"):
         st.write(hugin_names_result)
   
    with st.beta_expander("Download as JSON file"):
        # huginn_names_json = json.dumps(hugin_names_result)
        # tmp_download_link = download_link(huginn_names_json, 'huginn_names.json', 'Click here to download your file')
        # st.markdown(tmp_download_link, unsafe_allow_html=True)      
     # download file if user clicks (faster)    
        if st.button('Download Huginn names as a json file'):
            huginn_names_json = json.dumps(hugin_names_result)
            tmp_download_link = download_link(huginn_names_json, 'huginn_names.json', 'Click here to download your file')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

def only_selected_keys(df, select_keys):
    for col in df.columns:
        select_keys.button(col)

def choose_keys(df, expander, include = True):
    expander = expander
    if include: 
        for col in df.columns: 
                    include = expander.checkbox(f'Include {col}')
                    if include:
                        expand = expander.button(f'view {col}')                                            
                        if expand:
                            expand = expander.button(f'close {col} view')
                            all_values = [val for val in df[col]]
                            expander.markdown(all_values, unsafe_allow_html=True)    
    else:
                for col in df.columns: 
                    include = expander.checkbox(f'Exclude {col}')
                    if include:
                        expand = expander.button(f'view {col}')                                            
                        if expand:
                            expand = expander.button(f'close {col} view')
                            all_values = [val for val in df[col]]
                            expander.markdown(all_values, unsafe_allow_html=True) 

def choose_keys2(df,  include = True):
    expander = st
    prefix = 'include' if include  else 'exclude'
    
    for col in df.columns: 
        select_col = expander.checkbox(f'{prefix} {col}')
        if select_col:
            expand = expander.button(f'view {col}') 
            if expand:
                expand = expander.button(f'close {col} view')
                all_values = [val for val in df[col]]
                expander.markdown(all_values, unsafe_allow_html=True)
            
                                                      
def display_table(responses, hugin_names_result):
    
    further = st.checkbox('Further investigation')
    
    if further:
        to_table_container = st.beta_expander('Convert to a table')
        check_names = st.beta_expander('Check names between the table and generated json')
        # select_keys = st.beta_expander('Select keys to include')
        # unselect_keys = st.beta_expander('Select keys to exclude')
           
        mofify_keys = st.selectbox('',('Modify keys','Select keys to exclude', 'Select keys to include'))

        df = cnv.convert_to_table(responses)
        
        if to_table_container:
            tmp_download_link = download_link(df, 'YOUR_DF.csv', 'Download as csv')
            to_table_container.markdown(tmp_download_link, unsafe_allow_html=True)
            to_table_container.dataframe(df.style)
    
        if check_names:
            keys = [key for key in hugin_names_result]        
            cols = [col for col in df.columns]        
            missing_json = [key for key in (set(keys) - set(cols))]
            #missing_json = ''.join(str(e) for e in missing_json)
            missing_table = [key for key in (set(cols) - set(keys))]
            check_names.markdown(f'Present in the table not genereted json: {missing_json}', unsafe_allow_html=True)
            check_names.markdown(f'Present in table not genereted json: {missing_table}', unsafe_allow_html=True)
        
        # if select_keys:
        #     choose_keys(df, select_keys, include = True)
          
        # if unselect_keys:
        #     choose_keys(df, unselect_keys, include = False)
        #     select_keys = None
            
        if mofify_keys =='Select keys to exclude':
            choose_keys2(df, include = False)
        elif mofify_keys =='Select keys to include':
            choose_keys2(df, include = True)
                
    
def load_data(responses):
    data_load_state = st.text('Loading data...')
    loop = st.checkbox('Loop through all responses (might take a while, otherwise only the first response will be added)')
    
    hugin_names_result = cnv.converter(responses, loop = loop)
      
    data_load_state.text('Loading data... Done!')    
    display_huginn_names(hugin_names_result)
    display_table(responses, hugin_names_result)
    

def initialise():
    js_upload, js_raw, csv_upload = 'JSON Upload', 'JSON Raw', 'CSV Upload'    
    way_to_add = st.radio("Add your data",
                 (js_upload, js_raw, csv_upload))

    if way_to_add == 'JSON Upload':
        user_file = st.file_uploader("Upload json file", type="json") 
        if user_file:
            user_input = None
            responses = json.load(user_file) 
            load_data(responses)        
    
    elif way_to_add == 'JSON Raw':    
        user_input = st.text_area("Or just paste a response")
        
        if user_input:
            user_file = None
            try:
                responses = json.loads(user_input)
                load_data(responses)
            except Exception as e:
                st.markdown(f"Wrong JSON format. Error: {e}", unsafe_allow_html=True)        
    else:
        st.markdown('CSV uploads are not yet allowed, sorry', unsafe_allow_html=True)
 
        
initialise()



# classifier_name = st.sidebar.selectbox(
#     'Select classifier',
#     ('KNN', 'SVM', 'Random Forest'))



#st.markdown('<p class="small-font"> some string </p>', unsafe_allow_html=True)





