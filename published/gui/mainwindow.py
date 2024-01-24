
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QListWidget, QHBoxLayout, QLabel
from gui.website_list_widget import WebsiteListWidget
from gui.hashtag_list_widget import HashtagListWidget
from pipeline.hashtag_fetcher import HashtagFetcher
import config.settings as settings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hashtag Processor")

        self.settings_file = 'filter_settings.json'
        self.export_filename = 'wordlist.txt'
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.websiteListWidget = WebsiteListWidget()
        self.websiteListWidget.setMaximumHeight(200)

        self.hashtagFetcher = HashtagFetcher()
        self.hashtagListWidget = HashtagListWidget(self.hashtagFetcher)

        self.saveChangesButton = QPushButton("Save settings")

        # Main layout is a vertical layout
        mainLayout = QVBoxLayout(central_widget)

        # Add the 'Save Changes' button at the top
        mainLayout.addWidget(self.saveChangesButton)

        # Create a horizontal layout for the lists and add it to the main layout
        listsLayout = QHBoxLayout()
        mainLayout.addLayout(listsLayout)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.websiteListWidget)
        vertical_layout.addWidget(self.hashtagListWidget)

        result_layout = QVBoxLayout()

        # Result List
        self.result_list_label_template = "Filtered list word count "
        self.result_list_label = QLabel("Filtered list word count 0")
        self.resultList = QListWidget()
        self.resultList.setMaximumWidth(200)
        self.result_refresh_button = QPushButton("Refresh")
        self.result_save_button = QPushButton("Save wordlist.txt")

        listsLayout.addLayout(vertical_layout)
        result_layout.addWidget(self.result_list_label)
        result_layout.addWidget(self.resultList)
        result_layout.addWidget(self.result_refresh_button)
        result_layout.addWidget(self.result_save_button)
        listsLayout.addLayout(result_layout)


        self.saveChangesButton.clicked.connect(self.saveAppState)

        self.websiteListWidget.fetchButton.clicked.connect(self.fetchHashtags)

        self.hashtagListWidget.requestRefresh.connect(self.refresh_result_list)

        self.result_refresh_button.clicked.connect(self.refresh_result_list)

        self.result_save_button.clicked.connect(self.save_result_list)

        self.loadAppState()


    def loadAppState(self):
        data = settings.load_settings(self.settings_file)
        blacklist = data.get('blacklist', [])
        hashtags = data.get('hashtags', [])
        websites = data.get('websites', [])
        transforms = data.get('transforms', [])
        min_len_input = data.get('min_len_input', 0)
        max_len_input = data.get('max_len_input', 0)

        self.hashtagListWidget.add_hashtags(hashtags)

        for word in blacklist:
            self.hashtagListWidget.add_to_blacklist(word)  # Use the method to add to blacklist

        for word_transform in transforms:
            self.hashtagListWidget.addItemToList(self.hashtagListWidget.transform_list_widget, word_transform)  # Use the method to add to blacklist

        self.hashtagListWidget.min_len_input.setValue(min_len_input)
        self.hashtagListWidget.max_len_input.setValue(max_len_input)

        self.websiteListWidget.add_links(websites)

        self.hashtagListWidget.applyFilter()

    def saveAppState(self):
        data = {
            'blacklist': list(self.hashtagListWidget.blacklist),
            'hashtags': list(self.hashtagListWidget.fetched_hashtags),
            'websites': self.websiteListWidget.get_links(),
            'transforms': list([self.hashtagListWidget.transform_list_widget.item(i).text() for i in range(self.hashtagListWidget.transform_list_widget.count())]),
            'min_len_input': self.hashtagListWidget.min_len_input.value(),
            'max_len_input': self.hashtagListWidget.max_len_input.value()
        }
        settings.save_settings(self.settings_file, data)

    def fetchHashtags(self):
        selected_urls = self.websiteListWidget.get_links()
        for url in selected_urls:
            self.hashtagFetcher.fetch_hashtags(url)
        
        self.hashtagListWidget.add_hashtags(self.hashtagFetcher.unique_hashtags)

    def refresh_result_list(self):
        # Refresh the result list
        self.resultList.clear()
        word_list = [self.hashtagListWidget.hashtag_list_widget.item(i).text() for i in range(self.hashtagListWidget.hashtag_list_widget.count())]
        for word in sorted(word_list):
            self.resultList.addItem(word)

        self.result_list_label.setText(self.result_list_label_template + str(self.resultList.count()))

    def save_result_list(self):
        word_list = [self.resultList.item(i).text() for i in range(self.resultList.count())]
        with open(self.export_filename, 'w') as openfile:
            for word in word_list:
                openfile.write(word + "\n")
