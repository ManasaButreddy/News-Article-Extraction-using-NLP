#pip install streamlit
#pip install Pillow
import streamlit as st
import subprocess
from PIL import Image
import os
import time

#creating Placeholder for logo
img = Image.open("Logo.png")
st.image(img, width =175)

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #ff6347;
    }
</style>
""", unsafe_allow_html=True)
menu = ["Home", "Scrape Articles", "Summarize Articles"]
choice = st.sidebar.selectbox("***MENU***", menu)

html_temp = """
<div style="background-color:tomato;">
<h2 style="color:white;text-align:center;">News Article Summarization </h2>
</div>
"""
st.markdown(html_temp, unsafe_allow_html = True)
#st.text("")
if choice == "Home":
    st.subheader("Welcome to the News Article Scraping and Summarization app!")
    st.write("Please select an option from the sidebar.")

elif choice == "Scrape Articles":
    website = st.radio("Choose the website", ["***Borneo Post***", "***Malay Mail***","***The Star***" ],
                               index=None, )
    if website is None:
        st.warning("Choose a website")
    else:
        st.write("You have selected:", website)
        st.session_state['website'] = website
    #define function to attach actions to radio button selection
    def scrape():
        
        if website == "***Malay Mail***":
            with st.spinner('Please wait while we are scrapping articles from Malay Mail'):
                subprocess.run(["python", "Scrapy2.py"])
            st.success("Scraping completed and file has been saved in the directory")

        elif website == "***The Star***":
            with st.spinner('Please wait while we are scrapping articles from The Star'):
                subprocess.run(["python", "Star.py"])
            st.success("Scraping completed and file has been saved in the directory")
        
        elif website == "***Borneo Post***":
            with st.spinner('Please wait while we are scrapping articles from Borneo Post'):
                subprocess.run(["python", "Borneo.py"])
            st.success("Scraping completed and file has been saved in the directory")

    st.write("Click the button below to start scraping articles.")
    if st.button("Start Scraping", on_click= scrape):
        #st.success("Scraping completed and file has been saved in the directory!!")
        pass
        
elif choice == "Summarize Articles":
    st.write("")
    st.write(f"You have selected {st.session_state['website']} website to summarize articles!")
    st.warning("If you would like to continue with same please click on ***Summarize Articles*** button, else from sidebar select ***Scrape Articles*** Menu and choose the website to scrape!!")
    
    todays_file1 = 'MMArticles{}.csv'.format(time.strftime("%d%m%Y"))
    todays_file2 = 'StarArticles{}.csv'.format(time.strftime("%d%m%Y"))
    todays_file3 = 'BorneoArticles{}.csv'.format(time.strftime("%d%m%Y"))
    
    #function for model building
    def model():
        if st.session_state['website'] == "***Malay Mail***":
            if os.path.exists(todays_file1):
                progress_text = "It takes some time.Please relax while summarization is in progress..."
                progress_bar = st.progress(0, text = progress_text)
                subprocess.run(["python", "ModelBuilding2.py"])
                for percent_complete in range(1, 101):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete, text = progress_text )
                    progress_bar.empty()
                st.success("Summarization completed and file has been uploaded to s3 bucket!")
            else:
                st.warning("File not found! Please scrape the website before summarizing.", icon="⚠️")

        elif st.session_state['website'] == "***The Star***":
            if os.path.exists(todays_file2):
                progress_text = "It takes some time.Please relax while summarization is in progress..."
                progress_bar = st.progress(0, text = progress_text)
                subprocess.run(["python", "Star_ModelBuilding.py"])
                for percent_complete in range(1, 101):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete, text = progress_text )
                    progress_bar.empty()
                st.success("Summarization completed and file has been uploaded to s3 bucket!")
            else:
                st.warning("File not found! Please scrape the website before summarizing.", icon="⚠️")
        
        elif st.session_state['website'] == "***Borneo Post***":
            if os.path.exists(todays_file3):
                progress_text = "It takes some time.Please relax while summarization is in progress..."
                progress_bar = st.progress(0, text = progress_text)
                subprocess.run(["python", "Borneo_ModelBuilding.py"])
                for percent_complete in range(1, 101):
                    time.sleep(0.01)
                    progress_bar.progress(percent_complete, text = progress_text )
                    progress_bar.empty()
                st.success("Summarization completed and file has been uploaded to s3 bucket!")
            else:
                st.warning("File not found! Please scrape the website before summarizing.", icon="⚠️")
        
    #st.write("Click the button below to summarize articles.")
    if st.button("Summarize Articles", on_click= model): 
        pass
