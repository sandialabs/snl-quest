import streamlit as st
import streamlit.components.v1 as stc
import matplotlib
import pandas as pd
from openai import OpenAI
import configparser
import contextlib
import io
import os

# Config file path
config_file = 'config.ini'

def save_api_key_to_config(api_key):
    config = configparser.ConfigParser()
    config['openai'] = {'api_key': api_key}
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def get_api_key_from_config():
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        return config['openai'].get('api_key', '')
    return ''
def load_css(css_file):
    with open(css_file, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



def natural_question_to_pandas(df, question, openai_api_key):
    columns = ', '.join(df.columns)
    
    openai_client = OpenAI(api_key=openai_api_key)
    
    prompt = (
        f"Assuming 'df' is user's dataframe and is already loaded with columns {columns}, "
        f"translate the following question into python program using Pandas : '{question}'. "
        "The program should print the final results with explanation text. "
        "The program should also save any plot in ./Lib/site-packages/quest/snl_libraries/gpt/data/graphs/latest_graph.png file."
        "The whole program should be in a single code block."
    )
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        if response.choices:
            pandas_commands = response.choices[0].message.content.strip()
        else:
            pandas_commands = "No response from the model."
    except Exception as e:
        return f"An error occurred: {str(e)}"

    return pandas_commands

def extract_content(input_string):
    # Check if the string starts with 'begin' and ends with 'end'
    # if input_string.startswith("```python") and input_string.endswith("```"):
    # Find the index of the first occurrence of ```python and the last occurrence of ```
    start_index = input_string.find("```python") + len("```python")
    end_index = input_string.rfind("```")
    # Extract the content between 
    content = input_string[start_index:end_index].strip()
    return content
    # else:
        # return "There's no python code in this message"

# Function to safely evaluate the generated Python code - Placeholder for demonstration
def run_code_and_capture_output(code, local_vars=None):
    if local_vars is None:
        local_vars = {}
    # Capture the output of the code execution
    with contextlib.redirect_stdout(io.StringIO()) as output:
        exec(code, globals(), local_vars)
    return output.getvalue(), local_vars

def main():
    
    # Set the page to wide mode
    st.set_page_config(layout="wide")
    # css_file = 'style.css'
    # load_css(css_file)
    st.title("QuESt GPT - AI-powered tool for data analysis and visualization")
    
    # Attempt to load the API key from config if available
    saved_api_key = get_api_key_from_config()
    tab1, tab2 = st.tabs(["Load Data", "Analyze Data"])
    with tab1:
        col1, col2 = st.columns([1, 2])  # Second column is 2 times wider than the first
        with col1:
            # File uploader allows user to add their own CSV
            uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        
            if uploaded_file is not None:
                st.session_state.uploaded_csv = uploaded_file   
                # Read and display the CSV file
                df = pd.read_csv(st.session_state.uploaded_csv )
                # Generate a detailed summary of the CSV
                summary = "Summary of the uploaded CSV data:\n\n"
                summary += f"Total rows: {len(df)}\n"
                summary += f"Total columns: {len(df.columns)}\n"
                summary += "Column names: " + ", ".join(df.columns) + "\n"
                summary += "\nBasic statistics for numerical columns:\n"
                summary += df.describe().to_string()  # Basic statistics for numerical columns
                
                # The summary is displayed for informational purposes - to give context
                st.text(summary) 
        with col2:
            if uploaded_file is not None and "uploaded_csv" in st.session_state and st.session_state.uploaded_csv is not None:
                st.write("Data View")
                st.dataframe(df, height=500)
                # Visualize
                # pyg_html = pyg.walk(df,return_html=True)
                # # Render with components
                # stc.html(pyg_html,scrolling=True,height=800)

    with tab2:
        if 'results' not in st.session_state:
            st.session_state.results = []
        col1, col2 = st.columns([1, 1])
        with col1:
            api_key = st.text_input("Enter your OpenAI API key", value=saved_api_key, type="password")
            
            # Button to save the API key
            save_key = st.button("Save Key")
            if save_key:
                save_api_key_to_config(api_key)
                st.success("API key saved successfully!")
            if "uploaded_csv" in st.session_state and st.session_state.uploaded_csv is not None:
                query_prompt = "Ask any question about the data or request calculations based on it:"
                query = st.text_input(query_prompt)
                analyze_button = st.button("Analyze")
                # df=pd.read_csv(st.session_state.uploaded_csv )
                # Prompt for user query about the data
                if api_key:
                    if query and analyze_button:  # Ensure there's an API key and a query
                        # 
                        pandas_commands = natural_question_to_pandas(df, query, api_key)
                        st.session_state.code = pandas_commands
                        st.write(st.session_state.code)
                         
                    else:
                        st.error("Please enter your question.")
                else:
                    st.error("Please enter your OpenAI API key.")
        with col2:
            
            if "code" in st.session_state and st.session_state.code is not None:
                try:
                    pycode = extract_content(st.session_state.code)
                    show_button = st.button("Show results")
                    # df=pd.read_csv(st.session_state.uploaded_csv )
                    local_vars={"df":df}
                    if show_button:
                        output = run_code_and_capture_output(pycode,local_vars)
                        st.session_state.results.append(output[0])
                        st.write(output[0])
                        df1=pd.DataFrame(st.session_state.results,columns=["Query History"])
                        st.dataframe(df1,width=800)
                        image_path = './Lib/site-packages/quest/snl_libraries/gpt/data/graphs/latest_graph.png'
                        st.image(image_path)
                        
                    else:
                        st.error("Please run the code to see the results")
                except Exception as e:
                    st.error( f"An error occurred: {str(e)}, please analyze the question again")
        
if __name__ == "__main__":
    main()
