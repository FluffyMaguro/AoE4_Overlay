import json
from PyQt5 import QtWidgets, QtGui, QtCore
from typing import Dict, List, Union

class ProductionTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Production Tab")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # Units section
        units_groupbox = QtWidgets.QGroupBox("Units:")
        units_layout = QtWidgets.QGridLayout()
        units_groupbox.setLayout(units_layout)
        main_layout.addWidget(units_groupbox)

        # Buildings section
        buildings_groupbox = QtWidgets.QGroupBox("Buildings:")
        buildings_layout = QtWidgets.QGridLayout()
        buildings_groupbox.setLayout(buildings_layout)
        main_layout.addWidget(buildings_groupbox)

        # Load units and buildings from JSON
        json_data_path = "AoE4_Overlay/src/data/units.json"
        self.units = self.load_from_json(json_data_path, 'units')
        self.buildings = self.load_from_json(json_data_path, 'buildings')

        # Add units to the Units section
        self.unit_buttons = {}
        for i, unit in enumerate(self.units):
            btn = QtWidgets.QPushButton(unit['name'].capitalize())
            icon_path = unit['icon_path']
            btn.setIcon(QtGui.QIcon(icon_path))
            btn.clicked.connect(lambda _, u=unit: self.add_to_production(u))
            units_layout.addWidget(btn, i // 5, i % 5)
            self.unit_buttons[unit['name']] = btn

        # Add buildings to the Buildings section
        self.building_buttons = {}
        for i, building in enumerate(self.buildings):
            btn = QtWidgets.QPushButton(building['name'].capitalize())
            icon_path = building['icon_path']
            btn.setIcon(QtGui.QIcon(icon_path))
            btn.clicked.connect(lambda _, b=building: self.add_to_production(b))
            buildings_layout.addWidget(btn, i // 5, i % 5)
            self.building_buttons[building['name']] = btn

        # Production section
        production_groupbox = QtWidgets.QGroupBox("Production:")
        self.production_layout = QtWidgets.QGridLayout()
        production_groupbox.setLayout(self.production_layout)
        main_layout.addWidget(production_groupbox)

        self.production_items = {}  # Dictionary to manage production items with count

        # Costs section
        costs_groupbox = QtWidgets.QGroupBox("Costs:")
        costs_layout = QtWidgets.QFormLayout()
        costs_groupbox.setLayout(costs_layout)
        main_layout.addWidget(costs_groupbox)

        self.food_cost = QtWidgets.QLineEdit("0.00")
        self.wood_cost = QtWidgets.QLineEdit("0.00")
        self.gold_cost = QtWidgets.QLineEdit("0.00")
        self.stone_cost = QtWidgets.QLineEdit("0.00")
        for label, widget in [("Food:", self.food_cost), ("Wood:", self.wood_cost), ("Gold:", self.gold_cost), ("Stone:", self.stone_cost)]:
            costs_layout.addRow(label, widget)

        # Automation section
        automation_groupbox = QtWidgets.QGroupBox("Automation:")
        automation_layout = QtWidgets.QHBoxLayout()
        automation_groupbox.setLayout(automation_layout)
        main_layout.addWidget(automation_groupbox)

        self.automation_button = QtWidgets.QPushButton("Automate")
        self.automation_button.setCheckable(True)
        self.automation_button.toggled.connect(self.toggle_automation)
        automation_layout.addWidget(self.automation_button)

        # Flag to check if automation is active
        self.automation_active = False

    def load_from_json(self, file_path: str, key: str) -> List[Dict[str, Union[str, Dict[str, float]]]]:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get(key, [])

    def add_to_production(self, item: Dict[str, Union[str, Dict[str, float]]]):
        name = item['name']
        if name in self.production_items:
            self.production_items[name]['count'] += 1
            self.update_production_button(name)
        else:
            # Create the production icon button with name
            btn = QtWidgets.QPushButton(f"{name.capitalize()} x1")
            btn.setIcon(QtGui.QIcon(item['icon_path']))
            btn.clicked.connect(lambda: self.remove_from_production(btn, item))
            self.production_items[name] = {
                'data': item,
                'button': btn,
                'count': 1
            }
            # Update the production layout
            row = len(self.production_items) // 5
            col = len(self.production_items) % 5
            self.production_layout.addWidget(btn, row, col)
        # Update costs based on the item's cost in JSON
        cost = item.get('cost', {"food": 0, "wood": 0, "gold": 0, "stone": 0})
        self.update_costs(cost['food'], cost['wood'], cost['gold'], cost['stone'])

    def remove_from_production(self, btn: QtWidgets.QPushButton, item: Dict[str, Union[str, Dict[str, float]]]):
        name = item['name']
        if name in self.production_items:
            if self.production_items[name]['count'] > 1:
                self.production_items[name]['count'] -= 1
                self.update_production_button(name)
            else:
                # Remove the button if count is 1
                self.production_items[name]['button'].deleteLater()
                del self.production_items[name]
            # Update costs when item is removed
            cost = item.get('cost', {"food": 0, "wood": 0, "gold": 0, "stone": 0})
            self.update_costs(-cost['food'], -cost['wood'], -cost['gold'], -cost['stone'])

    def update_production_button(self, name: str):
        item = self.production_items[name]
        button = item['button']
        count = item['count']
        button.setText(f"{name.capitalize()} x{count}")

    def update_costs(self, food: float, wood: float, gold: float, stone: float):
        current_food = round(float(self.food_cost.text()) + food, 2)
        current_wood = round(float(self.wood_cost.text()) + wood, 2)
        current_gold = round(float(self.gold_cost.text()) + gold, 2)
        current_stone = round(float(self.stone_cost.text()) + stone, 2)
        self.food_cost.setText(f"{current_food:.2f}")
        self.wood_cost.setText(f"{current_wood:.2f}")
        self.gold_cost.setText(f"{current_gold:.2f}")
        self.stone_cost.setText(f"{current_stone:.2f}")

    def toggle_automation(self, checked: bool):
        self.automation_active = checked

    def print_shortcuts(self):
        shortcuts = []
        for item in self.production_items.values():
            shortcuts.extend([item['data']['hotkey']] * item['count'])
        print("Current shortcuts in production:", shortcuts)

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if self.automation_active and event.key() == QtCore.Qt.Key_O:
            self.print_shortcuts()

# Example usage
app = QtWidgets.QApplication([])
window = ProductionTab()
window.show()
app.exec_()
