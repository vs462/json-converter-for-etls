import json
import streamlit as st
import pandas as pd
import base64
import converter as cnv

st.set_page_config(layout="wide")
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True) # make buttons display horizontally 
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
}
</style>
""", unsafe_allow_html=True)

st.title('JSON to Huginn names converter')

def expensive_computation():
    """ For performance testing """
    import time
    from datetime import datetime
    time.sleep(1)  # This makes the function take 2s to run
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    st.write(f"BACK TO LIVE {current_time}")
    st.markdown(f"BACK TO LIVE {current_time}")
     
def initialise():    
    js_upload, jsl_upload, js_raw, csv_upload = 'JSON Upload','JSONL Upload', 'Raw JSON', 'CSV Upload'
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
                st.markdown(f"Wrong JSON format. Error: {e}", unsafe_allow_html=True)        
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
            

def load_data(responses):
    data_load_state = st.text('Loading data...')
    loop = st.checkbox('Loop through all responses (might take a while, otherwise only the first response will be added)')    
    csv = st.checkbox('Add "data" prefix to values')
    resp_id = st.checkbox('Convert "id" to "response_id" (if applicable)')

    hugin_names_result = cnv.converter(responses, loop = loop, resp_id = resp_id)
    
    data_load_state.text('Loading data... Done!')  
    
    st.markdown("## Basic conversion", unsafe_allow_html=True) 

    display_huginn_names(hugin_names_result, csv = csv)
    display_table(responses, hugin_names_result)
    select_keys(responses, hugin_names_result)
    meta_segm(responses, hugin_names_result)
            
def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    b64 = base64.b64encode(object_to_download.encode()).decode() # some strings <-> bytes conversions necessary here    
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def display_huginn_names(hugin_names_result, file_name = 'huginn_names.json', csv = False):  
    if csv:
        for res in hugin_names_result:
            hugin_names_result[res]['value'] = hugin_names_result[res]['value'].replace('{{', '{{data.')
  
    with st.beta_expander("See full result"):
        st.write(hugin_names_result)
   
    with st.beta_expander("Download as JSON file"):
            huginn_names_json = json.dumps(hugin_names_result)
            tmp_download_link = download_link(huginn_names_json, file_name, 'Click here to download your file')
            st.markdown(tmp_download_link, unsafe_allow_html=True)
            
@st.cache(suppress_st_warning=True) 
def turn_to_table(responses):
    df = cnv.convert_to_table(responses)
    expensive_computation()
    return df
      
                                                        
def display_table(responses, hugin_names_result):  
    st.markdown(' ## Convert to a table', unsafe_allow_html=True)
    cov_to_table = st.checkbox('Convert')
    if cov_to_table:
        df = turn_to_table(responses)            
        to_table_container = st.beta_expander('View Table')
        check_names = st.beta_expander('Check names between the table and generated json')          
        df = turn_to_table(responses)        
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

def select_keys(responses, hugin_names_result):    
    st.markdown('## Modify keys', unsafe_allow_html=True) 
    mofify_keys = st.radio('', ('No modifications', 'Select keys to exclude', 'Select keys to include'))            
    if mofify_keys =='Select keys to exclude':
        choose_keys(responses, hugin_names_result, include = False)
            
    elif mofify_keys =='Select keys to include':
        choose_keys(responses, hugin_names_result, include = True)
              


initialise()

# table_data = {'Column 1': [1, 2], 'Column 2': [3, 4]}

# if st.button('delet dis'):
#     del table_data
#     st.write('mr button has delet for u')
    
# try:
#     st.write(pd.DataFrame(data=table_data))
# except:
#     pass

# # classifier_name = st.sidebar.selectbox(
# #     'Select classifier',
# #     ('KNN', 'SVM', 'Random Forest'))


# #st.markdown('<p class="small-font"> some string </p>', unsafe_allow_html=True)
# if st.button('put to sleep'):
#     expensive_computation()


