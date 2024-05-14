from PyQt5 import QtWidgets, QtCore
import sys
import re
import requests
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bparser import BibTexParser

class BibTexUpdater(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('BibTeX Updater')
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        self.layout = QtWidgets.QVBoxLayout()

        self.text_box = QtWidgets.QTextEdit(self)
        self.layout.addWidget(self.text_box)

        self.status_label = QtWidgets.QLabel("")
        self.layout.addWidget(self.status_label)

        self.button = QtWidgets.QPushButton('Update BibTeX', self)
        self.button.clicked.connect(self.on_update_clicked)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def on_update_clicked(self):
        self.button.setEnabled(False)
        self.status_label.setText("Updating...")
        QtCore.QTimer.singleShot(100, self.update_bibtex)  # QTimer to keep the UI responsive
    
    def search_dblp(self, title, authors):
        query = '+'.join(title.split() + authors.split())
        response = requests.get(f'https://dblp.org/search/publ/api?q={query}&format=json')
        if response.status_code == 200:
            try:
                entries = response.json()['result']['hits']['hit']
                best_entry = None
                best_rank = float('inf')
                rank_priority = {
                    'Journal Articles': 1,
                    'Conference and Workshop Papers': 2,
                    'Parts in Books or Collections': 3,
                    'Books and Theses': 4,
                    'Editorship': 5,
                    'Reference Works': 6,
                    'Data and Artifacts': 7,
                    'Informal and Other Publications': 8
                }

                for entry in entries:
                    dblp_type = entry['info']['type']
                    dblp_title = entry['info']['title']

                    # Normalize type and title for comparison
                    normalized_type = dblp_type.strip()
                    normalized_dblp_title = re.sub('[^A-Za-z0-9]+', '', dblp_title.strip().lower())
                    normalized_title = re.sub('[^A-Za-z0-9]+', '', title.strip().lower())

                    # Determine the rank based on the type of publication
                    rank = rank_priority.get(normalized_type, 9)  # Default to a low priority if not matched

                    # Check if this entry is a better match based on rank and title similarity
                    if normalized_title == normalized_dblp_title and rank < best_rank:
                        best_rank = rank
                        best_entry = entry
                        print(f"New best match found: {normalized_type} with rank {rank}")
                        print(best_entry)
                        break  # Break out of the loop once the best match is found

                if best_entry:
                    url = best_entry['info']['url'] + '.bib'
                    bib_response = requests.get(url)
                    print(bib_response.text)
                    if bib_response.status_code == 200:
                        return bib_response.text

            except Exception as e:
                print("Error processing DBLP response:", e)
        return None

    def update_bibtex(self):
        input_bibtex = self.text_box.toPlainText()
        parser = BibTexParser(common_strings=True)
        bib_database = bibtexparser.loads(input_bibtex, parser=parser)

        writer = BibTexWriter()
        updated_database = []
        for entry in bib_database.entries:
            if 'title' in entry:
                bib = self.search_dblp(entry['title'], entry.get('author', ''))
                if bib:
                    bib_loaded = bibtexparser.loads(bib, parser=BibTexParser(common_strings=True))
                    if bib_loaded.entries:
                        updated_entry = bib_loaded.entries[0]
                        updated_entry['ID'] = entry['ID'] # Preserve the original ID
                        updated_database.append(updated_entry)
                else:
                    updated_database.append(entry)
            else:
                updated_database.append(entry)

        bib_database.entries = updated_database
        updated_bibtex = writer.write(bib_database)
        self.text_box.setPlainText(updated_bibtex)
        self.status_label.setText("Update complete!")
        self.button.setEnabled(True)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = BibTexUpdater()
    ex.show()
    sys.exit(app.exec_())
