
style={
'main': '''
QMainWindow {
  width: 100%;
  margin: 0;
  font-family: Arial;
  margin-left: auto;
  margin-right: auto;
  background-color:#1A64B7;
}''',

'button': '''
QPushButton {
  background-color: #555;
  color: white;
  border: 1px solid white;
  outline: none;
  text-align: center;
  font-size: 28px; 
  font-weight: bold;
  border-radius: 10px;
}
QPushButton::hover {
  background-color: #888;
}
''',

'tabsel': '''
QPushButton {
  background-color: red;
  color: white;
  border: 1px solid white;
  outline: none;
  text-align: center;
  font-size: 28px; 
  font-weight: bold;
  border-radius: 10px;
}
QPushButton::hover {
  background-color: #F33;
}
''',

'cmdbutton': '''
QPushButton {
  background-color: blue;
  color: white;
  border: 1px solid white;
  outline: none;
  text-align: center;
  font-size: 28px; 
  font-weight: bold;
  border-radius: 10px;
}
QPushButton::hover {
  background-color: #33F;
}
''',

'actbutton': '''
QPushButton {
  background-color: red;
  color: white;
  border: 1px solid white;
  outline: none;
  text-align: center;
  font-size: 28px; 
  font-weight: bold;
  border-radius: 10px;
}
QPushButton::hover {
  background-color: #F33;
}
''',

'warnbutton': '''
QPushButton {
  background-color: red;
  color: white;
  border: 1px solid white;
  outline: none;
  text-align: center;
  font-size: 28px; 
  font-weight: bold;
  border-radius: 10px;
}
QPushButton::hover {
  background-color: #F33;
}
''',

'text': '''
QTextEdit {
  background-color: lightgray;
  font-size: 20px;
  color:red;
}
''',

'label': '''
QLabel {
  font-size: 20px;
  color:#333;
}
''',

'scroll': '''
QScrollBar {
  border-radius: 10px;
  border: 10px solid blue;
  background-color: white;
}
QScrollBar::handle{
    background: maroon;
    border-radius: 10px;
    min-width: 50px;
    min-height:50px;
}
QScrollBar::handle::pressed {
    background : maroon;
}
''',

'list': '''
QListWidget {
    font-size: 20px;
    color: lightgray;
    line-height:30px;
}
QListWidget::item:hover {
    background-color: #EC7063;
}
QListWidget::item { margin: 6px; }
QScrollBar {
  border-radius: 10px;
  border: 1px solid blue;
  background-color: white;
  width: 40px;
}
QScrollBar::handle{
    background: maroon;
    border-radius: 10px;
    min-width: 50px;
    min-height:50px;
}
QScrollBar::handle::pressed {
    background : maroon;
}
''',

'dialog': '''
QDialog {
    background-color: #48C9B0;
}
QLabel {
    color: red;
    background-color: #48C9B0;
}
QScrollBar {
  border-radius: 10px;
  border: 10px solid #48C9B0;
  background-color: white;
}
QScrollBar::handle{
    background: maroon;
    border-radius: 10px;
    min-width: 50px;
    min-height:50px;
}
QScrollBar::handle::pressed {
    background : maroon;
}
'''
}
