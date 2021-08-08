
style={
'main': '''
QMainWindow {
  width: 100%;
  margin: 0;
  font-family: Arial;
  margin-left: auto;
  margin-right: auto;
  background-color:#1A64B7;
}
QListWidget {
    background-color: #289047;
    font-size: 20px;
    color: lightgray;
    line-height:30px;
}
QListWidget::item:hover {background-color: blue;}
QListWidget::item { margin: 6px; }
QFrame#dataTab {
    background-color: green;
}
''',

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
  background-color: #000080;
  color: white;
  border: 1px solid white;
  outline: none;
  text-align: center;
  font-size: 28px; 
  font-weight: bold;
  border-radius: 10px;
}
QPushButton::hover {
  background-color: #3B86F2;
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
* {
  width: 30px;
  border-radius: 10px;
  border: none;
  background-color: gray;    
}

*::handle:vertical{
    background: maroon;
    border-radius: 10px;
    width: 50px;
    height: 50px;
}

*::handle:horizontal {
    background: maroon;
    border-radius: 10px;
    border: none;
    width: 35px;
    height: 100px;
    margin: -24px -12px;
}
*::handle::pressed {
    background : maroon;
}
*::groove:horizontal {
    border: 1px solid #262626;
    height: 5px;
    background: #393939;
    margin: 0 12px;
}
*::right-arrow, *::left-arrow{
      border: none;
      background: none;
      color: none;
}
*::up-arrow, *::down-arrow{
      border: none;
      background: none;
      color: none;
}
*::add-line {
      border: none;
      background: none;
}

*::sub-line {
      border: none;
      background: none;
}

''',

'list': '''
QListWidget {
    font-size: 20px;
    color: lightgray;
    line-height:30px;
}
QListWidget::item:hover {background-color: blue;}
QListWidget::item { margin: 6px; }
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
''',

'dtime': '''
*{
    background-color: gray;
    font-size: 30px; 
    color: yellow;
}
*::down-button{
    width:30px;
}
*::up-button{
        width:30px;
}
'''

}
