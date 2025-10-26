"""
Add Search to Your Streamlit App with Algolia

This example shows Streamlit developers how to integrate Algolia search into their apps.

Already using Streamlit? Add powerful search in minutes:
- Algolia: Lightning-fast, typo-tolerant search with on-demand index updates
- Supabase: Database operations (this example, but works with any backend)
- Streamlit: Your familiar UI framework with caching and session state

This example demonstrates production-ready patterns for adding search functionality,
including on-demand synchronization instead of costly scheduled reindexing.
Perfect for Streamlit apps that need search capabilities.
"""

import base64
from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st
from algoliasearch.search.client import SearchClientSync
from st_supabase_connection import SupabaseConnection

assets_path = Path(__file__).parent.joinpath("assets")
# =============================================================================
# STREAMLIT PAGE CONFIGURATION
# =============================================================================
st.set_page_config(page_title="Streamlit + Algolia", page_icon=":material/search:")
st.title("Streamlit + Algolia")
st.logo(
    image=assets_path.joinpath("Algolia-logo-white.png"),
    icon_image=assets_path.joinpath("Algolia-mark-white.png"),
)

# =============================================================================
# ADD SEARCH TO YOUR STREAMLIT APP: INITIALIZE ALGOLIA CLIENT
# =============================================================================
# Step 1: Configure your Algolia index name
INDEX_NAME = "books_dataset"

# Step 2: Initialize Supabase (this is just for the demo's data layer)
# Replace this with your own database connection if you use a different backend
supabase_client = st.connection(
    name="supabase_connection",
    type=SupabaseConnection,
)

# Step 3: Initialize Algolia - this is what adds search to your Streamlit app!
# Store your credentials in .streamlit/secrets.toml
algolia_client = SearchClientSync(
    app_id=st.secrets.ALGOLIA_APP_ID,
    api_key=st.secrets.ALGOLIA_API_KEY,
)

# Initialize variables to store API responses for debugging
supabase_api_response = algolia_api_response = None

# =============================================================================
# SIDEBAR: DATA MANAGEMENT FUNCTIONS
# =============================================================================
with st.sidebar:
    # Collapsible section for adding/updating/deleting books
    with st.expander("Admin panel", icon=":material/settings:"):
        st.write("Add, update, or delete books from the database.")
        # Input fields for book data
        isbn = st.text_input("Book ISBN (required)")
        title = st.text_input("Book Title")
        year = st.number_input("Year of Publication", min_value=1000, max_value=2025, value=2025)

        # Two-column layout for action buttons
        col1, col2 = st.columns(2)

        # Button 1: Add or Update book
        if col1.button("Add/Update Book", width="stretch", icon=":material/add:"):
            if isbn:
                # Sync 1: Update Supabase database
                # By updating only what changes, and when it changes, we avoid costly full reindexing
                attributes_to_update = {"ISBN": isbn}
                if title:
                    attributes_to_update["Book-Title"] = title
                if year:
                    attributes_to_update["Year-Of-Publication"] = year

                # Upsert operation ensures we add new records or update existing ones
                supabase_api_response = (
                    supabase_client.table("books")
                    .upsert(
                        json=attributes_to_update,
                        on_conflict="ISBN",
                    )
                    .execute()
                )

                # Sync 2: Update Algolia search index on-demand

                algolia_api_response = algolia_client.partial_update_object(
                    index_name=INDEX_NAME,
                    object_id=isbn,
                    attributes_to_update=attributes_to_update,
                    create_if_not_exists=True,
                )
                # Wait for Algolia to finish indexing before proceeding
                algolia_client.wait_for_task(
                    index_name=INDEX_NAME, task_id=algolia_api_response.task_id
                )
                # Clear cache to force refresh of displayed data
                st.cache_data.clear()
                st.success("Book added/updated successfully", icon=":material/check_circle:")
            else:
                st.error("ISBN is required", icon=":material/error:")

        # Button 2: Delete book
        if col2.button("Delete Book", width="stretch", icon=":material/delete:"):
            if isbn:
                # Delete from Supabase
                supabase_api_response = (
                    supabase_client.table("books").delete().eq("ISBN", isbn).execute()
                )

                # On-demand deletion from Algolia index
                # We only update what changed, preventing costly full reindex operations
                algolia_api_response = algolia_client.delete_object(
                    index_name=INDEX_NAME, object_id=isbn
                )
                # Wait for deletion to complete
                algolia_client.wait_for_task(
                    index_name=INDEX_NAME, task_id=algolia_api_response.task_id
                )
                # Clear cache to refresh data
                st.cache_data.clear()
                st.success("Book deleted successfully", icon=":material/check_circle:")
            else:
                st.error("ISBN is required", icon=":material/error:")

    # Display API responses for debugging (only if operations were performed)
    if supabase_api_response and algolia_api_response:
        with st.expander("Supabase API response"):
            st.json(supabase_api_response)
        with st.expander("Algolia API response"):
            st.json(algolia_api_response)

    # Manual refresh button
    if st.button("Rerun app", width="stretch", icon=":material/refresh:"):
        st.rerun()

    # Display current books in the database
    response = supabase_client.table("books").select("*").execute()
    if response.data:
        st.dataframe(pd.DataFrame(response.data).sort_values(by="ISBN"), hide_index=True)

# =============================================================================
# ADD A SEARCH INPUT TO YOUR STREAMLIT APP
# =============================================================================
# This is how you add a search input - customize it for your app!
query = st.text_input(
    "Search for a book",
    icon=":material/search:",
    label_visibility="collapsed",
    placeholder="Search for a book",
)

# =============================================================================
# PAGINATION STATE MANAGEMENT
# =============================================================================
# Initialize session state to track current page and search queries
# This persists across reruns and allows us to implement pagination
if "page" not in st.session_state:
    st.session_state.page = 0
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# =============================================================================
# IMPLEMENT ALGOLIA SEARCH IN YOUR STREAMLIT APP
# =============================================================================
if query:
    # Reset to page 0 when search query changes
    # This ensures users start at the first page for new searches
    if query != st.session_state.get("current_query", ""):
        st.session_state.page = 0
        st.session_state.current_query = query

    # Use Streamlit's caching to prevent redundant API calls
    @st.cache_data
    def cached_search(query: str, page: int):
        return algolia_client.search(
            search_method_params={
                "requests": [
                    {
                        "indexName": INDEX_NAME,
                        "query": query,
                        "hitsPerPage": 5,  # Number of results per page
                        "page": page,  # Current page number (0-indexed)
                    },
                ],
            },
        )

    # Execute the search - this is where Algolia magic happens in your Streamlit app!
    response = cached_search(query=query, page=st.session_state.page)

    # Extract total number of hits from the response
    total_hits = response.results[0].actual_instance.nb_hits

    # Check if we have results to display
    if total_hits:
        # Calculate pagination metadata
        total_pages = response.results[0].actual_instance.nb_pages
        current_page = (
            response.results[0].actual_instance.page + 1
        )  # Convert to 1-based for display

        # =============================================================================
        # PAGINATION CONTROLS
        # =============================================================================
        def pagination_controls(position: Literal["top", "bottom"] = "top"):
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

            with col1:
                # First page button
                if st.button(
                    "⏮ First",
                    disabled=current_page == 1,
                    key=f"first_{position}",
                    width="stretch",
                ):
                    st.session_state.page = 0
                    st.rerun()

            with col2:
                # Previous page button
                if st.button(
                    "◀ Previous",
                    disabled=current_page == 1,
                    key=f"prev_{position}",
                    width="stretch",
                ):
                    st.session_state.page -= 1
                    st.rerun()

            with col3:
                # Display current page and total pages
                st.caption(f"Found {total_hits} results (Page {current_page} of {total_pages})")

            with col4:
                # Next page button
                if st.button(
                    "Next ▶",
                    disabled=current_page == total_pages,
                    key=f"next_{position}",
                    width="stretch",
                ):
                    st.session_state.page += 1
                    st.rerun()

            with col5:
                # Last page button
                if st.button(
                    "Last ⏭",
                    disabled=current_page == total_pages,
                    key=f"last_{position}",
                    width="stretch",
                ):
                    st.session_state.page = total_pages - 1
                    st.rerun()

        # Display pagination controls at the top
        pagination_controls("top")

        # =============================================================================
        # SEARCH RESULTS DISPLAY
        # =============================================================================
        # Iterate through search results and display them
        for result in response.results:
            for hit in result.actual_instance.hits:
                # Convert Hit object to dictionary for easier field access
                hit_dict = dict(hit)

                # Extract book information from search results
                # Note: Field names match the CSV column names from the books dataset
                title = hit_dict.get("Book-Title")
                author = hit_dict.get("Book-Author")
                isbn = hit_dict.get("ISBN")
                publisher = hit_dict.get("Publisher")
                year = hit_dict.get("Year-Of-Publication")
                image_url = hit_dict.get("Image-URL-L")

                # Create a two-column layout for each result
                col1, col2 = st.columns([1, 3])

                # Display book cover image if available
                if image_url:
                    col1.image(image_url)

                # Display book details in the second column
                with col2:
                    st.subheader(f"**{title}**")
                    st.caption(f"*By {author} **|** Year: {year}* ")
                    st.write(f"Publisher: {publisher} (*ISBN: {isbn}*)")
                    st.link_button(
                        label="Buy on Amazon",
                        url=f"https://www.amazon.com/s?k={title.replace(' ', '+')}",
                        icon=":material/shopping_cart:",
                    )

                # Add a divider between results
                st.divider()

        # Display pagination controls at the bottom
        pagination_controls("bottom")
    else:
        # No results found
        st.info("No results")

    # =============================================================================
    # DEBUG: RAW API RESPONSE
    # =============================================================================
    # Expandable section to view raw API response for debugging
    with st.expander("Raw results"):
        st.json(response.to_json())

    # Add Algolia branding at the bottom
    @st.cache_data
    def get_logo_base64():
        with open(assets_path.joinpath("Algolia-logo-white.png"), "rb") as f:
            return base64.b64encode(f.read()).decode()

    logo_base64 = get_logo_base64()
    st.markdown(
        f"<div style='text-align: right;'><span style='font-size: 12px;'>Search powered by &nbsp;&nbsp</span><a href='https://www.algolia.com/' target='_blank'><img src='data:image/png;base64,{logo_base64}' style='height: 24px; vertical-align: middle;'></a></div>",
        unsafe_allow_html=True,
    )
