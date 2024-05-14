# BibTeXer
Updates BibTex code with newer references using DBLP API.
This is the hierarchy used for updating (from most important to least important):
1. Journal Articles
2. Conference and Workshop Papers
3. Parts in Books or Collections
4. Books and Theses
5. Editorship
6. Reference Works
7. Data and Artifacts
8. Informal and Other Publications

# Usage
Install the requirements:
`pip install -r requirements.txt`

Start the GUI using:
`python main.py`

Paste as many BibTex references as you like, the tool will update each of them iteratively while keeping the original reference ID.
