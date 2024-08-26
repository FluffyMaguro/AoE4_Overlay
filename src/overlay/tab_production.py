from PyQt5 import QtWidgets, QtGui, QtCore
from typing import Dict
import os


class ProductionTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_buttons = []
        self.production_buttons = []
        self.cost_fields = {}
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Units Section
        units_layout = QtWidgets.QGridLayout()
        unit_names = ["villager", "archer", "spearman", "horseman", "keshik", "man_at_arms", "crossbowman", "handcannoneer", "mangudai", "trader", "scout"]
        
        for i, unit_name in enumerate(unit_names):
            button = QtWidgets.QPushButton(unit_name.capitalize())
            icon_path = os.path.join("src/img/build_order/unit_mongols", f"{unit_name}-2.png")
            button.setIcon(QtGui.QIcon(icon_path))
            button.setIconSize(QtCore.QSize(50, 50))
            button.clicked.connect(lambda _, unit=unit_name: self.add_to_production(unit))
            self.unit_buttons.append(button)
            units_layout.addWidget(button, i // 6, i % 6)  # Display units on different rows

        layout.addLayout(units_layout)

        # Production Section
        production_layout = QtWidgets.QHBoxLayout()
        self.production_section = QtWidgets.QWidget()
        self.production_section.setLayout(production_layout)
        layout.addWidget(self.production_section)

        # Costs Section
        costs_layout = QtWidgets.QFormLayout()
        self.cost_fields["food"] = QtWidgets.QLineEdit("0")
        self.cost_fields["wood"] = QtWidgets.QLineEdit("0")
        self.cost_fields["gold"] = QtWidgets.QLineEdit("0")
        self.cost_fields["stone"] = QtWidgets.QLineEdit("0")

        for resource in ["food", "wood", "gold", "stone"]:
            self.cost_fields[resource].setReadOnly(True)
            costs_layout.addRow(f"{resource.capitalize()}: ", self.cost_fields[resource])

        layout.addLayout(costs_layout)

        # Automation Section
        automation_layout = QtWidgets.QVBoxLayout()
        self.automation_toggle = QtWidgets.QPushButton("Automate")
        self.automation_toggle.setCheckable(True)
        automation_layout.addWidget(self.automation_toggle)
        layout.addLayout(automation_layout)

    def add_to_production(self, unit):
        button = QtWidgets.QPushButton(unit.capitalize())
        icon_path = os.path.join("src/img/build_order/unit_mongols", f"{unit}-2.png")
        button.setIcon(QtGui.QIcon(icon_path))
        button.setIconSize(QtCore.QSize(50, 50))
        self.production_buttons.append(button)
        self.production_section.layout().addWidget(button)
        self.update_costs(unit)

    def update_costs(self, unit):
        unit_costs = self.get_unit_costs(unit)
        for resource, cost in unit_costs.items():
            current_cost = int(self.cost_fields[resource].text())
            new_cost = current_cost + cost
            self.cost_fields[resource].setText(str(new_cost))

    def get_unit_costs(self, unit) -> Dict[str, int]:
        # Placeholder unit costs; these would be dynamic or from a data source in a real app
        costs = {
            "villager": {"food": 50, "wood": 0, "gold": 0, "stone": 0},
            "archer": {"food": 0, "wood": 25, "gold": 45, "stone": 0},
            # Add costs for other units
        }
        return costs.get(unit, {"food": 0, "wood": 0, "gold": 0, "stone": 0})
