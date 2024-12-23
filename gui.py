from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFileDialog, QHeaderView, QDialogButtonBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from database import update_database, fetch_bridge_costs

def format_currency(amount):
    """Formats a number with commas for thousands."""
    return f"{amount:,.2f}" if not amount.is_integer() else f"{int(amount):,}"

class DatabaseUpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Database")
        
        # Layout
        layout = QVBoxLayout()
        
        # Input Fields
        self.material_input = QLineEdit(self)
        self.base_rate_input = QLineEdit(self)
        self.maintenance_rate_input = QLineEdit(self)
        self.repair_rate_input = QLineEdit(self)
        self.demolition_rate_input = QLineEdit(self)
        self.environmental_factor_input = QLineEdit(self)
        self.social_factor_input = QLineEdit(self)
        self.delay_factor_input = QLineEdit(self)

        layout.addWidget(QLabel("Material:"))
        layout.addWidget(self.material_input)
        layout.addWidget(QLabel("Base Rate (₹/m²):"))
        layout.addWidget(self.base_rate_input)
        layout.addWidget(QLabel("Maintenance Rate (₹/m²/year):"))
        layout.addWidget(self.maintenance_rate_input)
        layout.addWidget(QLabel("Repair Rate (₹/m²):"))
        layout.addWidget(self.repair_rate_input)
        layout.addWidget(QLabel("Demolition Rate (₹/m²):"))
        layout.addWidget(self.demolition_rate_input)
        layout.addWidget(QLabel("Environmental Factor (₹/m²):"))
        layout.addWidget(self.environmental_factor_input)
        layout.addWidget(QLabel("Social Factor (₹/vehicle/year):"))
        layout.addWidget(self.social_factor_input)
        layout.addWidget(QLabel("Delay Factor (₹/vehicle/year):"))
        layout.addWidget(self.delay_factor_input)

        self.setLayout(layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.handle_accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def handle_accept(self):
        material = self.material_input.text()
        try:
            base_rate = float(self.base_rate_input.text())
            maintenance_rate = float(self.maintenance_rate_input.text())
            repair_rate = float(self.repair_rate_input.text())
            demolition_rate = float(self.demolition_rate_input.text())
            environmental_factor = float(self.environmental_factor_input.text())
            social_factor = float(self.social_factor_input.text())
            delay_factor = float(self.delay_factor_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values.")
            return
        
        try:
            update_database(material, base_rate, maintenance_rate, repair_rate, demolition_rate, 
                            environmental_factor, social_factor, delay_factor)
            QMessageBox.information(self, "Success", f"Database updated for {material}.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))
        self.accept()

class BridgeCostApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bridge Cost Comparison")

        # Main Layout
        self.main_layout = QHBoxLayout()

        # Left Input Layout
        self.input_layout = QVBoxLayout()
        self.span_length_input = QLineEdit(self)
        self.width_input = QLineEdit(self)
        self.traffic_volume_input = QLineEdit(self)
        self.design_life_input = QLineEdit(self)

        self.input_layout.addWidget(QLabel("Span Length (m):"))
        self.input_layout.addWidget(self.span_length_input)
        self.input_layout.addWidget(QLabel("Width (m):"))
        self.input_layout.addWidget(self.width_input)
        self.input_layout.addWidget(QLabel("Traffic Volume (vehicles/day):"))
        self.input_layout.addWidget(self.traffic_volume_input)
        self.input_layout.addWidget(QLabel("Design Life (years):"))
        self.input_layout.addWidget(self.design_life_input)

        self.calculate_button = QPushButton("Calculate Costs", self)
        self.calculate_button.clicked.connect(self.calculate_costs)
        self.input_layout.addWidget(self.calculate_button)

        self.update_button = QPushButton("Update Database", self)
        self.update_button.clicked.connect(self.open_database_update_dialog)
        self.input_layout.addWidget(self.update_button)
        self.input_layout.addStretch()

        # Middle Graph Layout
        self.graph_layout = QVBoxLayout()
        self.figure = plt.Figure(figsize=(5, 4))  # Adjusted graph size
        self.canvas = FigureCanvas(self.figure)
        self.graph_layout.addWidget(self.canvas)

        # Export Button
        self.export_button = QPushButton("Export as PNG", self)
        self.export_button.clicked.connect(self.export_graph)
        self.graph_layout.addWidget(self.export_button)

        # Right Output Layout
        self.output_layout = QVBoxLayout()
        self.output_table = QTableWidget(self)
        self.output_table.setColumnCount(2)
        self.output_table.setHorizontalHeaderLabels(["Steel Bridge (₹)", "Concrete Bridge (₹)"])
        
        # Adjust column width
        self.output_table.setColumnWidth(0, 160)
        self.output_table.setColumnWidth(1, 170)
        
        # Adjust row height to fit content
        self.output_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        self.output_layout.addWidget(self.output_table)

        # Combine Layouts
        self.main_layout.addLayout(self.input_layout, 1)
        self.main_layout.addLayout(self.graph_layout, 2)
        self.main_layout.addLayout(self.output_layout, 1)
        self.setLayout(self.main_layout)

    def open_database_update_dialog(self):
        dialog = DatabaseUpdateDialog(self)
        dialog.exec_()

    def calculate_costs(self):
        try:
            span_length = int(self.span_length_input.text())
            width = int(self.width_input.text())
            traffic_volume = int(self.traffic_volume_input.text())
            design_life = int(self.design_life_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values.")
            return

        data = fetch_bridge_costs()
        steel_costs, concrete_costs = [], []
        cost_components = ["Construction Cost", "Maintenance Cost", "Repair Cost", "Demolition Cost", "Environmental Cost", "Social Cost", "User Cost", "Total Cost"]

        for row in data:
            material, base_rate, maintenance_rate, repair_rate, demolition_rate, environmental_factor, social_factor, delay_factor = row

            # Calculate costs
            construction_cost = span_length * width * base_rate
            maintenance_cost = span_length * width * maintenance_rate * design_life
            repair_cost = span_length * width * repair_rate
            demolition_cost = span_length * width * demolition_rate
            environmental_cost = span_length * width * environmental_factor
            social_cost = traffic_volume * social_factor * design_life
            user_cost = traffic_volume * delay_factor * design_life
            total_cost = (construction_cost + maintenance_cost + repair_cost + demolition_cost + environmental_cost + social_cost + user_cost)

            # Store costs in respective lists
            if material == 'Steel':
                steel_costs = [construction_cost, maintenance_cost, repair_cost,
                               demolition_cost, environmental_cost, social_cost, user_cost, total_cost]
            elif material == 'Concrete':
                concrete_costs = [construction_cost, maintenance_cost, repair_cost,
                                  demolition_cost, environmental_cost, social_cost, user_cost, total_cost]

        # Ensure both steel and concrete costs are calculated
        if not steel_costs or not concrete_costs:
            QMessageBox.warning(self, "Data Error", "Could not fetch cost data for both materials.")
            return

        # Update output table with calculated costs
        self.output_table.setRowCount(len(cost_components))
        self.output_table.setVerticalHeaderLabels([c.replace(" ", "\n") for c in cost_components])  # Multi-line labels

        for i, component in enumerate(cost_components):
            self.output_table.setItem(i, 0, QTableWidgetItem(format_currency(steel_costs[i])))
            self.output_table.setItem(i, 1, QTableWidgetItem(format_currency(concrete_costs[i])))

        self.plot_graph(cost_components, steel_costs, concrete_costs)

    def plot_graph(self, components, steel_costs, concrete_costs):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        index = range(len(components))
        bar_width = 0.35

        ax.bar(index, steel_costs, bar_width, label='Steel Bridge')
        ax.bar([i + bar_width for i in index], concrete_costs, bar_width, label='Concrete Bridge')

        ax.set_xlabel('Cost Components')
        ax.set_ylabel('Cost (₹)')
        ax.set_title('Cost Comparison between Steel and Concrete Bridges')
        ax.set_xticks([i + bar_width / 2.5 for i in index])
        ax.set_xticklabels(components, rotation=55, ha="right")
        ax.legend()

        self.canvas.draw()

    def export_graph(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png);;All Files (*)", options=options)
        if file_name:
            self.figure.savefig(file_name)
            QMessageBox.information(self, "Success", "Plot exported successfully.")