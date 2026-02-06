import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import requests
from dotenv import load_dotenv

load_dotenv()

class BRDGeneratorApp(QMainWindow):
    """
    Main application window for BRD Generator
    """
    
    def __init__(self):
        super().__init__()
        
        # API configuration
        self.api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
        
        # Current project
        self.current_project = None
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('BRD Generator - AI-Powered Business Requirements')
        self.setGeometry(100, 100, 1400, 900)
        
        # Set application icon and style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ddd;
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }
            QLabel {
                font-size: 13px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content area with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_project_tab(), "Projects")
        self.tab_widget.addTab(self.create_data_sources_tab(), "Data Sources")
        self.tab_widget.addTab(self.create_requirements_tab(), "Requirements")
        self.tab_widget.addTab(self.create_brd_tab(), "BRD Generation")
        self.tab_widget.addTab(self.create_analysis_tab(), "Analysis")
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage('Ready')
    
    def create_header(self):
        """Create application header"""
        header = QWidget()
        header.setStyleSheet("background-color: #2196F3; padding: 20px;")
        layout = QHBoxLayout(header)
        
        title = QLabel("BRD Generator")
        title.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        subtitle = QLabel("AI-Powered Business Requirements Documentation")
        subtitle.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(subtitle)
        
        return header
    
    def create_project_tab(self):
        """Create project management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Project creation group
        create_group = QGroupBox("Create New Project")
        create_layout = QFormLayout()
        
        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("Enter project name...")
        create_layout.addRow("Project Name:", self.project_name_input)
        
        self.project_desc_input = QTextEdit()
        self.project_desc_input.setPlaceholderText("Enter project description...")
        self.project_desc_input.setMaximumHeight(100)
        create_layout.addRow("Description:", self.project_desc_input)
        
        create_btn = QPushButton("Create Project")
        create_btn.clicked.connect(self.create_project)
        create_layout.addRow(create_btn)
        
        create_group.setLayout(create_layout)
        layout.addWidget(create_group)
        
        # Project list group
        list_group = QGroupBox("Existing Projects")
        list_layout = QVBoxLayout()
        
        self.project_list = QListWidget()
        self.project_list.itemClicked.connect(self.select_project)
        list_layout.addWidget(self.project_list)
        
        refresh_btn = QPushButton("Refresh Projects")
        refresh_btn.clicked.connect(self.load_projects)
        list_layout.addWidget(refresh_btn)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Load projects on startup
        QTimer.singleShot(500, self.load_projects)
        
        return tab
    
    def create_data_sources_tab(self):
        """Create data sources tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Integration options
        integrations_group = QGroupBox("Sync Data Sources")
        integrations_layout = QVBoxLayout()
        
        # Gmail sync
        gmail_layout = QHBoxLayout()
        gmail_layout.addWidget(QLabel("Gmail Query:"))
        self.gmail_query_input = QLineEdit()
        self.gmail_query_input.setPlaceholderText("subject:requirements after:2024/01/01")
        gmail_layout.addWidget(self.gmail_query_input)
        
        gmail_sync_btn = QPushButton("Sync Gmail")
        gmail_sync_btn.clicked.connect(self.sync_gmail)
        gmail_layout.addWidget(gmail_sync_btn)
        
        integrations_layout.addLayout(gmail_layout)
        
        # Slack sync
        slack_layout = QHBoxLayout()
        slack_layout.addWidget(QLabel("Slack Channel:"))
        self.slack_channel_input = QLineEdit()
        self.slack_channel_input.setPlaceholderText("C01234567")
        slack_layout.addWidget(self.slack_channel_input)
        
        slack_sync_btn = QPushButton("Sync Slack")
        slack_sync_btn.clicked.connect(self.sync_slack)
        slack_layout.addWidget(slack_sync_btn)
        
        integrations_layout.addLayout(slack_layout)
        
        # Document upload
        upload_layout = QHBoxLayout()
        upload_btn = QPushButton("Upload Document")
        upload_btn.clicked.connect(self.upload_document)
        upload_layout.addWidget(upload_btn)
        upload_layout.addStretch()
        
        integrations_layout.addLayout(upload_layout)
        
        integrations_group.setLayout(integrations_layout)
        layout.addWidget(integrations_group)
        
        # Data sources list
        sources_group = QGroupBox("Data Sources")
        sources_layout = QVBoxLayout()
        
        self.sources_table = QTableWidget()
        self.sources_table.setColumnCount(5)
        self.sources_table.setHorizontalHeaderLabels(
            ["Type", "Identifier", "Relevant", "Score", "Date"]
        )
        self.sources_table.horizontalHeader().setStretchLastSection(True)
        sources_layout.addWidget(self.sources_table)
        
        process_btn = QPushButton("Process Sources & Extract Requirements")
        process_btn.clicked.connect(self.process_sources)
        sources_layout.addWidget(process_btn)
        
        sources_group.setLayout(sources_layout)
        layout.addWidget(sources_group)
        
        return tab
    
    def create_requirements_tab(self):
        """Create requirements tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Requirements table
        self.requirements_table = QTableWidget()
        self.requirements_table.setColumnCount(6)
        self.requirements_table.setHorizontalHeaderLabels(
            ["Title", "Type", "Priority", "Stakeholder", "Confidence", "Source"]
        )
        self.requirements_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.requirements_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh Requirements")
        refresh_btn.clicked.connect(self.load_requirements)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        return tab
    
    def create_brd_tab(self):
        """Create BRD generation tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Generation options
        options_group = QGroupBox("Generation Options")
        options_layout = QVBoxLayout()
        
        self.include_conflicts_cb = QCheckBox("Include Conflict Analysis")
        self.include_conflicts_cb.setChecked(True)
        options_layout.addWidget(self.include_conflicts_cb)
        
        self.include_traceability_cb = QCheckBox("Include Traceability Matrix")
        self.include_traceability_cb.setChecked(True)
        options_layout.addWidget(self.include_traceability_cb)
        
        self.include_sentiment_cb = QCheckBox("Include Sentiment Analysis")
        self.include_sentiment_cb.setChecked(True)
        options_layout.addWidget(self.include_sentiment_cb)
        
        generate_btn = QPushButton("Generate BRD")
        generate_btn.setStyleSheet("background-color: #FF9800; font-size: 16px; padding: 15px;")
        generate_btn.clicked.connect(self.generate_brd)
        options_layout.addWidget(generate_btn)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # BRD list
        brd_group = QGroupBox("Generated BRDs")
        brd_layout = QVBoxLayout()
        
        self.brd_list = QListWidget()
        self.brd_list.itemClicked.connect(self.select_brd)
        brd_layout.addWidget(self.brd_list)
        
        btn_layout = QHBoxLayout()
        
        view_btn = QPushButton("View BRD")
        view_btn.clicked.connect(self.view_brd)
        btn_layout.addWidget(view_btn)
        
        edit_btn = QPushButton("Edit BRD")
        edit_btn.clicked.connect(self.edit_brd)
        btn_layout.addWidget(edit_btn)
        
        download_btn = QPushButton("Download BRD")
        download_btn.clicked.connect(self.download_brd)
        btn_layout.addWidget(download_btn)
        
        brd_layout.addLayout(btn_layout)
        
        brd_group.setLayout(brd_layout)
        layout.addWidget(brd_group)
        
        return tab
    
    def create_analysis_tab(self):
        """Create analysis tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Conflict detection
        conflicts_group = QGroupBox("Conflict Detection")
        conflicts_layout = QVBoxLayout()
        
        detect_btn = QPushButton("Detect Conflicts")
        detect_btn.clicked.connect(self.detect_conflicts)
        conflicts_layout.addWidget(detect_btn)
        
        self.conflicts_table = QTableWidget()
        self.conflicts_table.setColumnCount(4)
        self.conflicts_table.setHorizontalHeaderLabels(
            ["Type", "Description", "Severity", "Status"]
        )
        self.conflicts_table.horizontalHeader().setStretchLastSection(True)
        conflicts_layout.addWidget(self.conflicts_table)
        
        conflicts_group.setLayout(conflicts_layout)
        layout.addWidget(conflicts_group)
        
        # Dashboard placeholder
        dashboard_group = QGroupBox("Project Dashboard")
        dashboard_layout = QVBoxLayout()
        
        self.dashboard_text = QTextEdit()
        self.dashboard_text.setReadOnly(True)
        dashboard_layout.addWidget(self.dashboard_text)
        
        dashboard_group.setLayout(dashboard_layout)
        layout.addWidget(dashboard_group)
        
        return tab
    
    # API Methods
    
    def create_project(self):
        """Create a new project"""
        name = self.project_name_input.text()
        description = self.project_desc_input.toPlainText()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a project name")
            return
        
        try:
            response = requests.post(
                f"{self.api_base_url}/projects/",
                json={"name": name, "description": description}
            )
            
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Project created successfully")
                self.project_name_input.clear()
                self.project_desc_input.clear()
                self.load_projects()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create project: {response.text}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")
    
    def load_projects(self):
        """Load all projects"""
        try:
            response = requests.get(f"{self.api_base_url}/projects/")

            if response.status_code == 200:
                data = response.json()

                # DRF pagination support
                projects = data.get("results", [])

                self.project_list.clear()

                for project in projects:
                    name = project.get("name", "Untitled")
                    created_at = project.get("created_at", "")[:10]

                    item = QListWidgetItem(f"{name} - {created_at}")
                    item.setData(Qt.UserRole, project)
                    self.project_list.addItem(item)

                self.statusBar().showMessage(
                    f"Loaded {len(projects)} projects"
                )
            else:
                QMessageBox.warning(
                    self,
                    "API Error",
                    f"Failed to load projects (Status {response.status_code})"
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load projects:\n{str(e)}"
            )

    def select_project(self, item):
        """Select a project"""
        self.current_project = item.data(Qt.UserRole)
        self.statusBar().showMessage(f"Selected project: {self.current_project['name']}")
        
        # Load data for selected project
        self.load_data_sources()
        self.load_requirements()
        self.load_brds()
    
    def sync_gmail(self):
        """Sync Gmail data"""
        if not self.current_project:
            QMessageBox.warning(self, "Error", "Please select a project first")
            return
        
        query = self.gmail_query_input.text()
        
        try:
            response = requests.post(
                f"{self.api_base_url}/projects/{self.current_project['id']}/sync_data_sources/",
                json={"sync_gmail": True, "gmail_query": query}
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Gmail synced successfully")
                self.load_data_sources()
            else:
                QMessageBox.warning(self, "Error", f"Failed to sync: {response.text}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Sync error: {str(e)}")
    
    def sync_slack(self):
        """Sync Slack data"""
        if not self.current_project:
            QMessageBox.warning(self, "Error", "Please select a project first")
            return
        
        channel = self.slack_channel_input.text()
        
        if not channel:
            QMessageBox.warning(self, "Error", "Please enter a Slack channel")
            return
        
        try:
            response = requests.post(
                f"{self.api_base_url}/projects/{self.current_project['id']}/sync_data_sources/",
                json={"sync_slack": True, "slack_channel": channel, "days": 30}
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Slack synced successfully")
                self.load_data_sources()
            else:
                QMessageBox.warning(self, "Error", f"Failed to sync: {response.text}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Sync error: {str(e)}")
    
    def upload_document(self):
        """Upload a document"""
        if not self.current_project:
            QMessageBox.warning(self, "Error", "Please select a project first")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Document", "", "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    data = {'project_id': self.current_project['id']}
                    
                    response = requests.post(
                        f"{self.api_base_url}/data-sources/upload_document/",
                        data=data,
                        files=files
                    )
                    
                    if response.status_code == 200:
                        QMessageBox.information(self, "Success", "Document uploaded successfully")
                        self.load_data_sources()
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to upload: {response.text}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Upload error: {str(e)}")
    
    def load_data_sources(self):
        """Load data sources for current project"""
        if not self.current_project:
            return
        
        try:
            response = requests.get(
                f"{self.api_base_url}/data-sources/",
                params={"project": self.current_project['id']}
            )
            
            if response.status_code == 200:
                sources = response.json()
                self.sources_table.setRowCount(len(sources))
                
                for i, source in enumerate(sources):
                    self.sources_table.setItem(i, 0, QTableWidgetItem(source['source_type']))
                    self.sources_table.setItem(i, 1, QTableWidgetItem(source['source_identifier'][:50]))
                    self.sources_table.setItem(i, 2, QTableWidgetItem("Yes" if source['is_relevant'] else "No"))
                    self.sources_table.setItem(i, 3, QTableWidgetItem(f"{source['relevance_score']:.2f}"))
                    self.sources_table.setItem(i, 4, QTableWidgetItem(source['created_at'][:10]))
        
        except Exception as e:
            print(f"Error loading data sources: {e}")
    
    def process_sources(self):
        """Process data sources to extract requirements"""
        if not self.current_project:
            QMessageBox.warning(self, "Error", "Please select a project first")
            return
        
        try:
            response = requests.post(
                f"{self.api_base_url}/data-sources/process_sources/",
                json={"project_id": self.current_project['id']}
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Requirements extracted successfully")
                self.load_requirements()
            else:
                QMessageBox.warning(self, "Error", f"Failed to process: {response.text}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing error: {str(e)}")
    
    def load_requirements(self):
        """Load requirements for current project"""
        if not self.current_project:
            return
        
        try:
            response = requests.get(
                f"{self.api_base_url}/requirements/",
                params={"project_id": self.current_project['id']}
            )
            
            if response.status_code == 200:
                requirements = response.json()
                self.requirements_table.setRowCount(len(requirements))
                
                for i, req in enumerate(requirements):
                    self.requirements_table.setItem(i, 0, QTableWidgetItem(req['title'][:50]))
                    self.requirements_table.setItem(i, 1, QTableWidgetItem(req['requirement_type']))
                    self.requirements_table.setItem(i, 2, QTableWidgetItem(req['priority']))
                    self.requirements_table.setItem(i, 3, QTableWidgetItem(req.get('stakeholder', '')))
                    self.requirements_table.setItem(i, 4, QTableWidgetItem(f"{req['confidence_score']:.2f}"))
                    self.requirements_table.setItem(i, 5, QTableWidgetItem(req['data_source_type']))
        
        except Exception as e:
            print(f"Error loading requirements: {e}")
    
    def generate_brd(self):
        """Generate BRD document"""
        if not self.current_project:
            QMessageBox.warning(self, "Error", "Please select a project first")
            return
        
        try:
            response = requests.post(
                f"{self.api_base_url}/brd-documents/generate/",
                json={
                    "project_id": self.current_project['id'],
                    "include_conflicts": self.include_conflicts_cb.isChecked(),
                    "include_traceability": self.include_traceability_cb.isChecked(),
                    "include_sentiment": self.include_sentiment_cb.isChecked()
                }
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "BRD generated successfully")
                self.load_brds()
            else:
                QMessageBox.warning(self, "Error", f"Failed to generate: {response.text}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Generation error: {str(e)}")
    
    def load_brds(self):
        """Load BRD documents"""
        if not self.current_project:
            return
        
        try:
            response = requests.get(
                f"{self.api_base_url}/brd-documents/",
                params={"project": self.current_project['id']}
            )
            
            if response.status_code == 200:
                brds = response.json()
                self.brd_list.clear()
                
                for brd in brds:
                    item = QListWidgetItem(f"{brd['title']} - v{brd['version']} ({brd['status']})")
                    item.setData(Qt.UserRole, brd)
                    self.brd_list.addItem(item)
        
        except Exception as e:
            print(f"Error loading BRDs: {e}")
    
    def select_brd(self, item):
        """Select a BRD document"""
        self.selected_brd = item.data(Qt.UserRole)
    
    def view_brd(self):
        """View BRD document"""
        if not hasattr(self, 'selected_brd'):
            QMessageBox.warning(self, "Error", "Please select a BRD first")
            return
        
        # Create a dialog to show BRD content
        dialog = QDialog(self)
        dialog.setWindowTitle(self.selected_brd['title'])
        dialog.setGeometry(150, 150, 800, 600)
        
        layout = QVBoxLayout(dialog)
        
        text_browser = QTextEdit()
        text_browser.setReadOnly(True)
        
        # Format BRD content
        content = f"""
<h1>{self.selected_brd['title']}</h1>
<p><b>Version:</b> {self.selected_brd['version']} | <b>Status:</b> {self.selected_brd['status']}</p>

<h2>Executive Summary</h2>
<p>{self.selected_brd['executive_summary']}</p>

<h2>Business Objectives</h2>
<p>{self.selected_brd['business_objectives']}</p>

<h2>Stakeholder Analysis</h2>
<p>{self.selected_brd['stakeholder_analysis']}</p>

<h2>Functional Requirements</h2>
<pre>{self.selected_brd['functional_requirements']}</pre>

<h2>Non-Functional Requirements</h2>
<pre>{self.selected_brd['non_functional_requirements']}</pre>
        """
        
        text_browser.setHtml(content)
        layout.addWidget(text_browser)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def edit_brd(self):
        """Edit BRD document with natural language"""
        if not hasattr(self, 'selected_brd'):
            QMessageBox.warning(self, "Error", "Please select a BRD first")
            return
        
        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit BRD")
        dialog.setGeometry(200, 200, 600, 300)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel("Section to edit:"))
        section_combo = QComboBox()
        section_combo.addItems([
            "executive_summary",
            "business_objectives",
            "stakeholder_analysis",
            "functional_requirements",
            "non_functional_requirements",
            "assumptions",
            "success_metrics",
            "timeline"
        ])
        layout.addWidget(section_combo)
        
        layout.addWidget(QLabel("Edit instruction (natural language):"))
        instruction_input = QTextEdit()
        instruction_input.setPlaceholderText("E.g., 'Add more detail about security requirements'")
        layout.addWidget(instruction_input)
        
        btn_layout = QHBoxLayout()
        
        apply_btn = QPushButton("Apply Edit")
        
        def apply_edit():
            section = section_combo.currentText()
            instruction = instruction_input.toPlainText()
            
            if not instruction:
                QMessageBox.warning(dialog, "Error", "Please enter an instruction")
                return
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/brd-documents/{self.selected_brd['id']}/edit/",
                    json={
                        "brd_id": self.selected_brd['id'],
                        "section": section,
                        "edit_instruction": instruction
                    }
                )
                
                if response.status_code == 200:
                    QMessageBox.information(dialog, "Success", "BRD updated successfully")
                    self.load_brds()
                    dialog.close()
                else:
                    QMessageBox.warning(dialog, "Error", f"Failed to edit: {response.text}")
            
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Edit error: {str(e)}")
        
        apply_btn.clicked.connect(apply_edit)
        btn_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def download_brd(self):
        """Download BRD document"""
        if not hasattr(self, 'selected_brd'):
            QMessageBox.warning(self, "Error", "Please select a BRD first")
            return
        
        # Choose save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save BRD", f"BRD_{self.selected_brd['id']}.docx", "Word Documents (*.docx)"
        )
        
        if file_path:
            try:
                response = requests.get(
                    f"{self.api_base_url}/brd-documents/{self.selected_brd['id']}/download/",
                    stream=True
                )
                
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    QMessageBox.information(self, "Success", f"BRD downloaded to {file_path}")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to download: {response.text}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Download error: {str(e)}")
    
    def detect_conflicts(self):
        """Detect conflicts in requirements"""
        if not self.current_project:
            QMessageBox.warning(self, "Error", "Please select a project first")
            return
        
        try:
            response = requests.post(
                f"{self.api_base_url}/conflicts/detect_conflicts/",
                json={"project_id": self.current_project['id']}
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Success", response.json()['status'])
                self.load_conflicts()
            else:
                QMessageBox.warning(self, "Error", f"Failed to detect conflicts: {response.text}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Detection error: {str(e)}")
    
    def load_conflicts(self):
        """Load detected conflicts"""
        if not self.current_project:
            return
        
        try:
            response = requests.get(
                f"{self.api_base_url}/conflicts/",
                params={"project": self.current_project['id']}
            )
            
            if response.status_code == 200:
                conflicts = response.json()
                self.conflicts_table.setRowCount(len(conflicts))
                
                for i, conflict in enumerate(conflicts):
                    self.conflicts_table.setItem(i, 0, QTableWidgetItem(conflict['conflict_type']))
                    self.conflicts_table.setItem(i, 1, QTableWidgetItem(conflict['description'][:100]))
                    self.conflicts_table.setItem(i, 2, QTableWidgetItem(conflict['severity']))
                    self.conflicts_table.setItem(i, 3, QTableWidgetItem("Resolved" if conflict['resolved'] else "Pending"))
        
        except Exception as e:
            print(f"Error loading conflicts: {e}")


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = BRDGeneratorApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
