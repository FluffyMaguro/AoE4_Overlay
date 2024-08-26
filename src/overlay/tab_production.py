from PyQt5 import QtWidgets, QtCore, QtGui

class ProductionTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Main Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.setSpacing(15)

        # Units Section
        units_layout = self.create_units_section()
        layout.addLayout(units_layout)

        # Production Section
        self.production_layout = self.create_production_section()
        layout.addLayout(self.production_layout)

        # Costs Section
        self.costs_layout = self.create_costs_section()
        layout.addLayout(self.costs_layout)

        # Automation Section
        automation_layout = self.create_automation_section()
        layout.addLayout(automation_layout)

        # Initialize costs dictionary
        self.costs = {'food': 0, 'wood': 0, 'gold': 0, 'stone': 0}

    def create_units_section(self):
        units_layout = QtWidgets.QGridLayout()
        units_layout.setContentsMargins(10, 10, 10, 10)

        units = {
            'villager': {'food': 50, 'wood': 0, 'gold': 0, 'stone': 0},
            'archer': {'food': 0, 'wood': 25, 'gold': 45, 'stone': 0},
            'spearman': {'food': 35, 'wood': 25, 'gold': 0, 'stone': 0},
            # Add more units with their corresponding costs
        }

        for i, (unit, cost) in enumerate(units.items()):
            btn = QtWidgets.QPushButton(unit.capitalize())
            btn.clicked.connect(lambda _, u=unit, c=cost: self.add_to_production(u, c))
            units_layout.addWidget(btn, 0, i)

        return units_layout

    def create_production_section(self):
        production_layout = QtWidgets.QVBoxLayout()
        production_layout.setContentsMargins(10, 10, 10, 10)

        self.production_label = QtWidgets.QLabel("Production: ")
        production_layout.addWidget(self.production_label)

        return production_layout

    def create_costs_section(self):
        costs_layout = QtWidgets.QVBoxLayout()
        costs_layout.setContentsMargins(10, 10, 10, 10)

        self.cost_labels = {
            'food': QtWidgets.QLabel("Food: 0"),
            'wood': QtWidgets.QLabel("Wood: 0"),
            'gold': QtWidgets.QLabel("Gold: 0"),
            'stone': QtWidgets.QLabel("Stone: 0")
        }

        for label in self.cost_labels.values():
            costs_layout.addWidget(label)

        return costs_layout

    def create_automation_section(self):
        automation_layout = QtWidgets.QHBoxLayout()
        automation_layout.setContentsMargins(10, 10, 10, 10)

        self.automation_button = QtWidgets.QPushButton("Automate")
        self.automation_button.setCheckable(True)
        self.automation_button.clicked.connect(self.toggle_automation)
        automation_layout.addWidget(self.automation_button)

        return automation_layout

    def add_to_production(self, unit, cost):
        # Update production label
        current_text = self.production_label.text()
        new_text = f"{current_text} {unit.capitalize()},"
        self.production_label.setText(new_text)

        # Update costs
        for resource, amount in cost.items():
            self.costs[resource] += amount
            self.cost_labels[resource].setText(f"{resource.capitalize()}: {self.costs[resource]}")

    def toggle_automation(self):
        if self.automation_button.isChecked():
            self.automation_button.setText("Automate (On)")
            # Add automation logic here
        else:
            self.automation_button.setText("Automate (Off)")
            # Add logic to stop automation here

