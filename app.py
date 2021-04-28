import json
import streamlit as st
import pandas as pd
import base64
import converter as cnv
st.set_page_config(layout="wide")
#       json.dump(final_names, outfile)
st.markdown("""
<style>
.small-font {
    font-size:10px !important;
}
</style>
""", unsafe_allow_html=True)
#st.markdown('<p class="small-font"> some string </p>', unsafe_allow_html=True)

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
        #select_keys.markdown(df[col], unsafe_allow_html=True)
    
def display_table(responses, hugin_names_result):   
    to_table_container = st.beta_expander('Convert to a table')
    check_names = st.beta_expander('Check names between the table and generated json')
    select_keys = st.beta_expander('Select keys to include')
    unselect_keys = st.beta_expander('Select keys to exclude')
     
    if to_table_container or check_names:
        df = cnv.convert_to_table(responses)
    
    if to_table_container:
        tmp_download_link = download_link(df, 'YOUR_DF.csv', 'Download as csv')
        to_table_container.markdown(tmp_download_link, unsafe_allow_html=True)
        to_table_container.dataframe(df.style)

    if check_names:
        keys = [key for key in hugin_names_result]        
        cols = [col for col in df.columns]        
        missing = set(cols) - set(keys)
        st.markdown(f'missing keys: {missing}', unsafe_allow_html=True)
    
    if select_keys:
        #only_selected_keys(df, select_keys)
        for col in df.columns:
            expand = select_keys.button(col)
            if expand:
                select_keys.markdown(df[col], unsafe_allow_html=True)
        
    
def load_data(responses):
    data_load_state = st.text('Loading data...')
    loop = st.checkbox('Loop through all responses (might take a while, otherwise only the first response will be added)')
    
    if loop:
        hugin_names_result = cnv.converter_full(responses)
    else: 
        hugin_names_result = cnv.converter(responses)        
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


classifier_name = st.sidebar.selectbox(
    'Select classifier',
    ('KNN', 'SVM', 'Random Forest')
)







