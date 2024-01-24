from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QLineEdit
from PyQt6.QtCore import pyqtSignal
from pipeline.hashtag_fetcher import HashtagFetcher

class HashtagListWidget(QListWidget):

    requestRefresh = pyqtSignal()

    def __init__(self, hashtagFetcher: HashtagFetcher, parent=None):
        super().__init__(parent)
        self.hashtagFetcher = hashtagFetcher
        self.initUI()

    def initUI(self):
        # Main Vertical Layout
        mainLayout = QVBoxLayout(self)

        # Horizontal layout for hashtag list, buttons, and blacklist
        topRowLayout = QHBoxLayout()

        self.fetched_hashtags = set()
        self.hashtag_list = set()
        self.blacklist = set()

        # Hashtag List
        self.hashtag_list_widget = QListWidget()
        self.hashtag_list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.hashtag_list_widget.itemSelectionChanged.connect(self.onHashtagListSelectionChanged)

        # Blacklist
        self.blacklist_widget = QListWidget()
        self.blacklist_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        # Buttons Layout
        buttonLayout = QVBoxLayout()

        # Button to move to blacklist
        self.toBlacklistButton = QPushButton("Add to Blacklist")
        self.toBlacklistButton.clicked.connect(self.moveToBlacklist)
        buttonLayout.addWidget(self.toBlacklistButton)

        # Button to move back to hashtag list
        self.toHashtagListButton = QPushButton("Remove from Blacklist")
        self.toHashtagListButton.clicked.connect(self.moveToHashtagList)
        buttonLayout.addWidget(self.toHashtagListButton)
        # Filter list and controls
        self.filtered_list_widget = QListWidget()
        
        # Minimum length input
        self.min_len_input = QSpinBox()
        self.min_len_input.setMinimum(0)  # 0 for no minimum limit
        self.min_len_input.setMaximum(1000)  # Arbitrary large number

        # Maximum length input
        self.max_len_input = QSpinBox()
        self.max_len_input.setMinimum(0)  # 0 for no maximum limit
        self.max_len_input.setMaximum(1000)  # Arbitrary large number

        # Filter button
        self.filterButton = QPushButton("Filter")
        self.filterButton.clicked.connect(self.applyFilter)

        self.filtered_list_widget.itemSelectionChanged.connect(self.onFilterListSelectionChanged)

        # Arrange the filter controls in a layout
        filterLayout = QVBoxLayout()
        filterLayout.addWidget(QLabel("Min Length:"))
        filterLayout.addWidget(self.min_len_input)
        filterLayout.addWidget(QLabel("Max Length:"))
        filterLayout.addWidget(self.max_len_input)
        filterLayout.addWidget(self.filterButton)

        # Add filter controls and list to the main layout
        filterList_layout = QVBoxLayout()
        self.filterList_label = QLabel("Filtered list")
        filterList_layout.addWidget(self.filterList_label)
        filterList_layout.addWidget(self.filtered_list_widget)
        topRowLayout.addLayout(filterList_layout)
        topRowLayout.addLayout(filterLayout)

        # Add widgets to main layout
        fetched_list_layout = QVBoxLayout()
        self.hashtag_list_label = QLabel("Hashtag list")
        fetched_list_layout.addWidget(self.hashtag_list_label)
        fetched_list_layout.addWidget(self.hashtag_list_widget)
        topRowLayout.addLayout(fetched_list_layout)
        topRowLayout.addLayout(buttonLayout)

        blacklist_layout = QVBoxLayout()
        self.blacklist_label = QLabel("Blacklist")
        blacklist_layout.addWidget(self.blacklist_label)
        blacklist_layout.addWidget(self.blacklist_widget)
        topRowLayout.addLayout(blacklist_layout)

        # Add top row layout to main layout
        mainLayout.addLayout(topRowLayout)

        # Split List Section
        self.transform_list_label = QLabel("Word transform list. Word --> Result | Spaces separate new words: 'artificialtea -> artificial tea'", self)
        self.transform_list_widget = QListWidget()
        self.transform_list_widget.setMaximumHeight(200)
        self.transform_list_widget.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.transform_input = QLineEdit()
        self.confirm_transform_button = QPushButton("Confirm Transform")
        self.confirm_transform_button.clicked.connect(self.confirm_transformation)

        self.delete_transform_button = QPushButton("Delete Transform")
        self.delete_transform_button.clicked.connect(self.delete_transform)

        # Arrange split controls in a horizontal layout
        splitControlLayout = QHBoxLayout()
        self.transform_original_text = QLabel("Transform Word", self)
        splitControlLayout.addWidget(self.transform_original_text)
        splitControlLayout.addWidget(self.transform_input)
        splitControlLayout.addWidget(self.delete_transform_button)
        splitControlLayout.addWidget(self.confirm_transform_button)

        # Add this connection in initUI
        self.transform_list_widget.itemSelectionChanged.connect(self.onTransformListSelectionChanged)

        # Add split list and controls to the main layout
        mainLayout.addWidget(self.transform_list_label)
        mainLayout.addWidget(self.transform_list_widget)
        mainLayout.addLayout(splitControlLayout)

        # Set the main layout for the widget
        self.setLayout(mainLayout)

    def addItemToList(self, listWidget: QListWidget, itemText):
        """Add an item to a list and sort the list."""
        listWidget.addItem(QListWidgetItem(itemText))
        self.sortList(listWidget)

    def removeItemFromList(self, listWidget: QListWidget):
        """Remove the selected item from a list."""
        selectedItems = listWidget.selectedItems()
        if selectedItems:
            item = selectedItems[0]
            listWidget.takeItem(listWidget.row(item))

    def sortList(self, listWidget: QListWidget):
        """Sort the items in a list."""
        itemsText = [listWidget.item(i).text() for i in range(listWidget.count())]
        listWidget.clear()
        for text in sorted(itemsText):
            listWidget.addItem(QListWidgetItem(text))

    def add_to_blacklist(self, word: str):
        """Add a word to the blacklist."""
        self.blacklist.add(word.lower())
        self.refresh_blacklist()

    def remove_from_blacklist(self, word: str):
        """Remove word from blacklist."""
        self.blacklist.remove(word.lower())
        self.refresh_blacklist()

    def refresh_blacklist(self):
        self.blacklist_widget.clear()
        for word in self.blacklist:
            self.addItemToList(self.blacklist_widget, word)

    def is_blacklisted(self, word: str):
        """Check if a word is in the blacklist."""
        return word.lower() in self.blacklist

    def moveToBlacklist(self):
        selectedItems = self.hashtag_list_widget.selectedItems()
        if selectedItems:
            item = selectedItems[0]
            hashtag = item.text()
            self.add_to_blacklist(hashtag)
        
            self.applyFilter()
            return
        
        selectedItems = self.filtered_list_widget.selectedItems()
        if selectedItems:
            item = selectedItems[0]
            hashtag = item.text()
            self.add_to_blacklist(hashtag)
        
            self.applyFilter()

    def moveToHashtagList(self):
        selectedItems = self.blacklist_widget.selectedItems()
        if selectedItems:
            item = selectedItems[0]
            hashtag = item.text()
            self.remove_from_blacklist(hashtag)

            self.applyFilter()

    def confirm_transformation(self):
        originalText = self.transform_original_text.text()
        transformedText = self.transformText(self.transform_input.text())
        
        transform_selection = self.transform_list_widget.selectedItems()
        if transform_selection:
            transform_selection[0].setText(f"{originalText} -> {transformedText}")
        else:
            # Add transformed text to splitList
            self.addItemToList(self.transform_list_widget, f"{originalText} -> {transformedText}")

        self.applyFilter()

    def delete_transform(self):
        self.removeItemFromList(self.transform_list_widget)
        self.applyFilter()

    def transformText(self, text):
        transformedText = text
        return transformedText

    def onTransformListSelectionChanged(self):
        selectedItems = self.transform_list_widget.selectedItems()
        if selectedItems:
            transform_text = selectedItems[0].text().split(' -> ')
            text = transform_text[0]  # Get the original part of the text
            self.transform_original_text.setText(text)
            self.transform_input.setText(transform_text[1])

        selected_item = self.hashtag_list_widget.selectedItems()
        if selected_item:
            selected_item[0].setSelected(False)
        selected_item = self.filtered_list_widget.selectedItems()
        if selected_item:
            selected_item[0].setSelected(False)

    def onFilterListSelectionChanged(self):
        # Get selected text from filterList and display in splitInput
        selectedItems = self.filtered_list_widget.selectedItems()
        if selectedItems:
            self.transform_original_text.setText(selectedItems[0].text())
            self.transform_input.setText(selectedItems[0].text())

        selected_item = self.hashtag_list_widget.selectedItems()
        if selected_item:
            selected_item[0].setSelected(False)
        selected_item = self.transform_list_widget.selectedItems()
        if selected_item:
            selected_item[0].setSelected(False)

    def onHashtagListSelectionChanged(self):
        # Get selected text from hashtagList and display in splitInput
        selectedItems = self.hashtag_list_widget.selectedItems()
        if selectedItems:
            self.transform_original_text.setText(selectedItems[0].text())
            self.transform_input.setText(selectedItems[0].text())
            
        selected_item = self.filtered_list_widget.selectedItems()
        if selected_item:
            selected_item[0].setSelected(False)
        selected_item = self.transform_list_widget.selectedItems()
        if selected_item:
            selected_item[0].setSelected(False)

    def applyFilter(self):
        self.refreshHashtagListWidget()

        self.applyBlacklistFilter()

        self.processListWithTransformations()

        self.filterList()

        self.applyBlacklistFilter()

        self.refresh_blacklist()

        self.requestRefresh.emit()

    def applyBlacklistFilter(self):
        for word in self.blacklist:
            self.removeItemIfFound(self.hashtag_list_widget, word)

    def removeItemIfFound(self, listWidget: QListWidget, word: str):
        """Remove an item from the list if it matches the given word."""
        for i in range(listWidget.count()-1, -1, -1):
            if listWidget.item(i).text().lower() == word.lower():
                listWidget.takeItem(i)

    def copyFetchedHashtags(self):
        self.hashtag_list = self.fetched_hashtags.copy()

    def refreshHashtagListWidget(self):
        self.copyFetchedHashtags()
        self.hashtag_list_widget.clear()
        for word in self.hashtag_list:
            self.addItemToList(self.hashtag_list_widget, word)

    def processListWithTransformations(self):
        # Process each transformation in the transform list
        for i in range(self.transform_list_widget.count()):
            transform_item = self.transform_list_widget.item(i)
            original, transformed = transform_item.text().split(' -> ')
            transformed_words = transformed.split()

            # Find and replace the original word in the hashtag list
            for j in range(self.hashtag_list_widget.count()-1, -1, -1):
                hashtag_item = self.hashtag_list_widget.item(j)
                if hashtag_item.text() == original:
                    # Remove the original word
                    self.hashtag_list_widget.takeItem(j)

                    # Add the transformed words if not already in the list
                    for word in transformed_words:
                        if not self.isWordInList(self.hashtag_list_widget, word):
                            self.addItemToList(self.hashtag_list_widget, word)

    def isWordInList(self, listWidget: QListWidget, word: str) -> bool:
        """Check if a word is already in the list."""
        return any(item.text() == word for item in self.iterateListItems(listWidget))

    def iterateListItems(self, listWidget: QListWidget):
        """Generator to iterate over items in a QListWidget."""
        for i in range(listWidget.count()):
            yield listWidget.item(i)

    def isWordInList(self, listWidget: QListWidget, word: str) -> bool:
        """Check if a word is already in the list."""
        return any(item.text() == word for item in self.iterateListItems(listWidget))
    
    def iterateListItems(self, listWidget: QListWidget):
        """Generator to iterate over items in a QListWidget."""
        for i in range(listWidget.count()):
            yield listWidget.item(i)

    def filterList(self):
        # Temporary list to store items before sorting
        tempItems = []

        minLen = self.min_len_input.value()
        maxLen = self.max_len_input.value() if self.max_len_input.value() > 0 else float('inf')

        # Reapply length filter to the hashtag list
        for i in range(self.hashtag_list_widget.count()-1, -1, -1):
            item = self.hashtag_list_widget.item(i)
            if not (minLen <= len(item.text()) <= maxLen):
                self.hashtag_list_widget.takeItem(i)
                tempItems.append(item.text())

        # Clear the filteredList and add sorted items
        self.filtered_list_widget.clear()
        for text in sorted(tempItems):
            self.filtered_list_widget.addItem(QListWidgetItem(text))

    def add_hashtags(self, hashtags):
        # Add hashtags to the list
        self.fetched_hashtags = set()
        for hashtag in hashtags:
            self.fetched_hashtags.add(hashtag)

        self.copyFetchedHashtags()
        self.applyFilter()
        
