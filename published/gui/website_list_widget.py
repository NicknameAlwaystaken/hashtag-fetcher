from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

class WebsiteListWidget(QWidget):

    # Define a signal named 'fetchHashtagsSignal'
    fetchHashtagsSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Main Layout for the widget
        mainLayout = QVBoxLayout(self)

        self.new_text = "New..."

        # List Widget
        self.website_list_label = QLabel("Website links. use format 'https://www.websitelink.any/'")
        self.website_list_widget = QListWidget()
        self.website_list_widget.addItem(self.new_text)
        self.website_list_widget.setCurrentRow(0)
        mainLayout.addWidget(self.website_list_label)
        mainLayout.addWidget(self.website_list_widget)

        # Bottom Layout containing the QLineEdit and QPushButton
        bottomLayout = QHBoxLayout()

        # QLineEdit for input
        self.inputField = QLineEdit()
        bottomLayout.addWidget(self.inputField)

        # QPushButton to add/change items
        self.actionButton = QPushButton("Add link")
        bottomLayout.addWidget(self.actionButton)
        
        self.removeButton = QPushButton("Remove link")
        bottomLayout.addWidget(self.removeButton)

        self.fetchButton = QPushButton("Fetch Hashtags")
        bottomLayout.addWidget(self.fetchButton)


        mainLayout.addLayout(bottomLayout)

        self.actionButton.clicked.connect(self.modify_selected_link)

        self.removeButton.clicked.connect(self.remove_selected_link)
        
        self.website_list_widget.itemSelectionChanged.connect(self.itemSelected)

        self.fetchButton.clicked.connect(self.fetchHashtagsSignal.emit)

    def add_links(self, urls):
        for url in urls:
            self.website_list_widget.insertItem(self.website_list_widget.count() - 1, QListWidgetItem(url))

    def add_link(self, url: str):
        if self.valid_url(url):
            self.website_list_widget.insertItem(self.website_list_widget.count() - 1, QListWidgetItem(url))

    def valid_url(self, url: str):
        valid_length = len(url) > 2
        has_dot = url.find(".") != -1
        return valid_length and has_dot

    def remove_selected_link(self):
        selectedItems = self.website_list_widget.selectedItems()
        if selectedItems:
            for item in selectedItems:
                if item.text() != self.new_text:
                    self.website_list_widget.takeItem(self.website_list_widget.row(item))

    def modify_selected_link(self):
        # Slot to handle the button click for add/change
        selectedItems = self.website_list_widget.selectedItems()
        selectedItemText = selectedItems[0].text()
        if selectedItems and selectedItemText != self.new_text:
            # Change selected item
            currentText = self.inputField.text()
            if currentText and currentText != self.new_text:
                selectedItems[0].setText(currentText)
        else:
            # Add new item
            self.add_link(self.inputField.text())

    def itemSelected(self):
        # Slot to handle item selection in the list
        selectedItems = self.website_list_widget.selectedItems()
        if selectedItems:
            selectedItemText = selectedItems[0].text()
            if selectedItemText != self.new_text:
                self.inputField.setText(selectedItemText)
                self.actionButton.setText("Change link")
            else:
                self.inputField.clear()
                self.actionButton.setText("Add link")

    def get_links(self):
        urls = [self.website_list_widget.item(x).text() for x in range(self.website_list_widget.count()) if self.website_list_widget.item(x).text() != self.new_text]
        return urls



if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    window = WebsiteListWidget()
    window.show()

    app.exec()
