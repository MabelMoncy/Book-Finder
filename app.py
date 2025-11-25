import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Page Config
st.set_page_config(page_title="Book Search", layout="wide")

# Load Environment Variables
load_dotenv()
BOOK_API_KEY = os.getenv("BOOK_API_KEY")

# --- YOUR ORIGINAL LOGIC FUNCTIONS ---

def extract_essential_details(data):
    if 'items' not in data:
        return []

    extracted_data = []

    for info in data['items']:
        vol_info = info.get('volumeInfo',{})
        access_info = info.get('accessInfo',{})
        industry_identifiers = vol_info.get('industryIdentifiers',[])
        
        isbn_value = "Unknown identifier"
        isbn_type = "Unknown type"
        
        if industry_identifiers:
            isbn_value = industry_identifiers[0].get("identifier")
            isbn_type = industry_identifiers[0].get("type")
            
        book_details = {
            "title" : vol_info.get("title","Unknown title"),
            "authors" : vol_info.get("authors",["Unknown authors"]),
            "publisher" : vol_info.get("publisher","Unknown publisher"),
            "publishedDate" : vol_info.get("publishedDate","Unknown published date"),
            "description" : vol_info.get("description","No description available"),
            "isbnType" : isbn_type,
            "isbnNumber" : isbn_value,
            "pageCount" : vol_info.get("pageCount",0),
            "language" : vol_info.get("language","Unknown language"),
            "saleability" : vol_info.get("saleability","Unknown saleability"),
            "pdf" : access_info.get("pdf",{}).get("isAvailable",False),
            "Information Link" : vol_info.get("infoLink","Unknown information link"),
            "webReaderLink" : access_info.get("webReaderLink","Unknown web reader link"),
            # Added only this so we can show a picture in the UI
            "thumbnail": vol_info.get("imageLinks", {}).get("thumbnail", "") 
        }
        # FIX: Appended inside the loop so we get all books, not just the last one
        extracted_data.append(book_details)
        
    return extracted_data

def getAuthorData(author, BOOK_API_KEY):
    # Added maxResults=40 so it lists ALL available books, not just 10
    r = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=inauthor:{author}&maxResults=40&key={BOOK_API_KEY}")
    data = r.json()
    final_data = extract_essential_details(data)
    return final_data

def getTitileData(title, BOOK_API_KEY):
    r = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=intitle:{title}&maxResults=40&key={BOOK_API_KEY}")
    data = r.json()
    final_data = extract_essential_details(data)
    return final_data

def getCategoryData(category, BOOK_API_KEY):
    r = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=subject:{category}&maxResults=40&key={BOOK_API_KEY}")
    data = r.json()
    final_data = extract_essential_details(data)
    return final_data

def getIsbnData(isbn, BOOK_API_KEY):
    r = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&maxResults=40&key={BOOK_API_KEY}")
    data = r.json()
    final_data = extract_essential_details(data)
    return final_data

# --- STREAMLIT GUI IMPLEMENTATION ---

# Initialize Session State to hold data
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# The Pop-up Screen (Dialog)
@st.dialog("Search Options")
def search_dialog():
    st.write("Search by \n 1.Author \n 2.Title \n 3.Category \n 4.ISBN")
    
    # User input replacement
    choice = st.selectbox("Enter your choice:", [1, 2, 3, 4], format_func=lambda x: {1: "1. Author", 2: "2. Title", 3: "3. Category", 4: "4. ISBN"}[x])
    
    user_input_value = ""
    
    # Logic to show the correct input box based on choice
    if choice == 1:
        user_input_value = st.text_input("Enter the name of the author:")
    elif choice == 2:
        user_input_value = st.text_input("Enter the name of the book:")
    elif choice == 3:
        user_input_value = st.text_input("Enter the category of the book:")
    elif choice == 4:
        user_input_value = st.text_input("Enter the isbn of the book:")

    if st.button("Search"):
        if not BOOK_API_KEY:
            st.error("API Key missing.")
            return

        # Calling YOUR functions exactly as defined
        data = []
        if choice == 1:
            data = getAuthorData(user_input_value, BOOK_API_KEY)
        elif choice == 2:
            data = getTitileData(user_input_value, BOOK_API_KEY)
        elif choice == 3:
            data = getCategoryData(user_input_value, BOOK_API_KEY)
        elif choice == 4:
            data = getIsbnData(user_input_value, BOOK_API_KEY)
        
        # Store result in session state and reload
        st.session_state.search_results = data
        st.rerun()

# --- MAIN APP LAYOUT ---

st.title("Book Information System")

# If no results, show the pop-up immediately
if not st.session_state.search_results:
    # We add a small button to open it manually if needed
    if st.button("Open Search"):
        search_dialog()
    # Auto-open on first load
    search_dialog()

# Display Data (Replacing your print_data function)
else:
    # Button to search again
    if st.button("Search Again"):
        st.session_state.search_results = []
        st.rerun()

    st.write(f"Found {len(st.session_state.search_results)} items.")
    
    # Iterate through your list of dictionaries
    for book in st.session_state.search_results:
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if book.get("thumbnail"):
                    st.image(book["thumbnail"], width=100)
                else:
                    st.write("No Image")

            with col2:
                # Displaying the exact keys you defined in extract_essential_details
                st.subheader(book["title"])
                st.write(f"**Author:** {book['authors']}")
                st.write(f"**Publisher:** {book['publisher']}")
                st.write(f"**Description:** {book['description']}")
                
                # Showing extra details in an expander to keep it clean
                with st.expander("More Details"):
                    st.write(f"**ISBN Type:** {book['isbnType']}")
                    st.write(f"**ISBN Number:** {book['isbnNumber']}")
                    st.write(f"**Published Date:** {book['publishedDate']}")
                    st.write(f"**Page Count:** {book['pageCount']}")
                    st.write(f"**Saleability:** {book['saleability']}")
                    st.write(f"**PDF Available:** {book['pdf']}")
                    st.write(f"**Link:** {book['Information Link']}")