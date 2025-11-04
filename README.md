# Add Search to Streamlit Apps with Algolia

Demonstrates pagination of Algolia results in Streamlit and on-demand Algolia index updates right from the Streamlit app.

<div align="center">
    <a href="https://algolia.streamlit.app/">
        <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Open in Streamlit" style="height: 60px !important;width: 217px !important;">
    </a>
</div>

**Tech Stack:**

- Streamlit for Python-based UI
- Algolia for search functionality
- Supabase for database operations (can be replaced with any database)

## What This Application Does

Implements a book search interface using Streamlit for the UI, Algolia for search, and Supabase for data persistence. Search includes:

- Typo tolerance and instant results
- Pagination of search results
- Caching to reduce API calls
- Real-time index synchronization on data changes
- Error handling and edge cases

**Dataset:** 27,000+ book records from Kaggle's [Books dataset](https://www.kaggle.com/datasets/saurabhbagchi/books-dataset)

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.10+** installed
2. An **Algolia account** ([Sign up for free](https://www.algolia.com/users/sign_up?utm_source=streamlit_algolia&utm_medium=github&utm_campaign=tutorial))
3. A **Supabase project** ([Create one here](https://supabase.com/dashboard))

## 🚀 Step-by-Step Setup Instructions

### Step 1: Clone or Download This Project

```bash
# If you have git installed
git clone https://github.com/SiddhantSadangi/streamlit_algolia.git
cd algolia

# Or download and extract the project folder
```

### Step 2: Install Python Dependencies

Create a virtual environment (recommended):

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install required packages:

```bash
pip install -r requirements.txt
```

### Step 3: Create a Supabase Project and Database

1. **Sign up for Supabase** at <https://supabase.com/dashboard>
2. **Create a new project**
3. **Navigate to the Table Editor** in Supabase dashboard
4. **Create the books table** by uploading the `books.csv` file. Use ISBN as the primary key.

5. **Get your Supabase credentials:**
   - Navigate to **Project Settings** → **API**
   - Copy your **Project URL**
   - Copy your **anon/public key**

### Step 4: Create Algolia Account and Index

1. **Sign up for Algolia** at <https://www.algolia.com/users/sign_up>
2. **Create a new application** in your Algolia dashboard
3. **Note your credentials:**

   - Application ID
   - Write API Key (needed for updating the index)

### Step 5: Connect Supabase to Algolia

1. **In your Algolia dashboard**, go to **Data Sources**
2. Click **Add a data source** → Select **Supabase**
3. **Configure the connection:**
   - **Trigger**: On demand (or set up automatic triggers)
   - **Indexing strategy**: Full record updates
   - **Source table**: `books`
   - **Destination index**: `books_dataset`
   - **Map fields** from your books table to Algolia index. Use `ISBN` as the ObjectID.
4. **Run the initial sync** to populate your Algolia index

### Step 6: Set Up Streamlit Secrets

Create a `.streamlit` folder in your project root if it doesn't exist:

```bash
mkdir .streamlit
```

Create a `secrets.toml` file in the `.streamlit` folder:

```toml
# .streamlit/secrets.toml

# Supabase Configuration
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key-here"

# Algolia Configuration
ALGOLIA_APP_ID = "your-app-id-here"
ALGOLIA_API_KEY = "your-write-api-key-here"
```

Replace the placeholders with your actual credentials from Steps 3 and 4.

> [!WARNING]
> Never commit `secrets.toml` to version control. It is already in `.gitignore`.

### Step 7: Launch the Application

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 📖 How to Use the Application

### Searching for Books

1. Enter a search query in the main search box (e.g., "Harry Potter", "Mystery", "Crichton")
2. View results with pagination controls
3. Use the pagination buttons to navigate through multiple pages
4. Click "Raw results" to see the full API response

### Managing Books (On-Demand Index Updates)

1. **Add a Book:**

   - Enter ISBN and title in the sidebar
   - Click "Add/Update Book"
   - The book will be added to both Supabase and Algolia **in real-time**

2. **Update a Book:**

   - Enter the ISBN of an existing book
   - Enter a new title or year of publication
   - Click "Add/Update Book" (uses upsert logic)
   - Only this one record is updated in Algolia, not the entire index

3. **Delete a Book:**

   - Enter the ISBN
   - Click "Delete Book"
   - The book will be removed from both systems immediately

4. **View Current Books:**
   - Check the dataframe at the bottom of the sidebar
   - Shows all books currently in the database

## 🔗 Resources and Links

- [Algolia Documentation](https://www.algolia.com/doc/)
- [Supabase Documentation](https://supabase.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Books Dataset on Kaggle](https://www.kaggle.com/datasets/saurabhbagchi/books-dataset)
