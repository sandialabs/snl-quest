import streamlit as st
import pandas as pd
import pygwalker as pyg
import streamlit.components.v1 as components

def main():
    # Title of the app
    st.set_page_config(layout="wide")
    st.title('Data Visualizer')

    # File upload
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])


    if uploaded_file is not None:
        # Read data from CSV file into DataFrame
        df = pd.read_csv(uploaded_file)

    
        # for col in df.columns:
            
        #     df[col] = df[col].astype(str)

        df = df.map(cast_to_string)
        # Generate the HTML using Pygwalker
        pyg_html = pyg.to_html(df)

        styled_html= f'<div style="width: 100%; height:1500px; overflow-y: auto">{pyg_html}</div>'
        # Embed the HTML into the Streamlit app
        components.html(styled_html, height=1000, scrolling=True)
        
def cast_to_string(val):
    if isinstance(val, int):
        return val
    else:
        return str(val)
        

if __name__ == "__main__":
    main()

