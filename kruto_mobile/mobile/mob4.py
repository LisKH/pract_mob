import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.metrics import dp

Window.size = (360, 640)
Window.clearcolor = (0.2, 0.35, 0.6, 1)
DB_PATH = 'study_var.db'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        from kivy.uix.image import Image
        img = Image(source='kruto.png', size_hint_y=None, height=180, allow_stretch=True)
        layout.add_widget(img)

        layout.add_widget(Label(text='Выберите таблицу', size_hint_y=None, height=40, font_size=20, color=(1, 1, 1, 1)))

        scroll = ScrollView()
        grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=5)
        grid.bind(minimum_height=grid.setter('height'))

        self.tables = self.get_tables()
        for table in self.tables:
            btn = Button(
                text=table,
                size_hint_y=None,
                height=44,
                background_color=(0.2, 0.4, 0.6, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_release=self.open_table)
            grid.add_widget(btn)

        scroll.add_widget(grid)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def get_tables(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def open_table(self, instance):
        self.manager.transition = SlideTransition(direction="left")
        table_screen = self.manager.get_screen('table')
        table_screen.load_table(instance.text)
        self.manager.current = 'table'


class TableScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sort_column = None
        self.sort_reverse = False
        self.selected_row = None
        self.columns = []

    def load_table(self, table_name):
        self.clear_widgets()
        self.table_name = table_name

        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        main_layout.add_widget(Label(text=f'Таблица: {table_name}', font_size=18, size_hint_y=None, height=30, color=(1,1,1,1)))

        search_box = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.search_input = TextInput(hint_text="Поиск...")
        search_button = Button(text="Поиск", size_hint_x=None, width=80, background_color=(0.1, 0.5, 0.8, 1))
        search_button.bind(on_release=self.apply_filter)
        search_box.add_widget(self.search_input)
        search_box.add_widget(search_button)
        main_layout.add_widget(search_box)

        scroll = ScrollView(size_hint=(1, 1))
        self.table_container = GridLayout(cols=1, size_hint_y=None, spacing=5, padding=5)
        self.table_container.bind(minimum_height=self.table_container.setter('height'))
        scroll.add_widget(self.table_container)
        main_layout.add_widget(scroll)

        self.action_buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.edit_btn = Button(text="Редактировать", background_color=(0.2, 0.6, 0.3, 1))
        self.delete_btn = Button(text="Удалить", background_color=(0.6, 0.2, 0.2, 1))
        self.edit_btn.bind(on_release=self.edit_record)
        self.delete_btn.bind(on_release=self.delete_record)
        self.edit_btn.disabled = True
        self.delete_btn.disabled = True
        self.action_buttons.add_widget(self.edit_btn)
        self.action_buttons.add_widget(self.delete_btn)
        main_layout.add_widget(self.action_buttons)

        nav_buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)
        add_btn = Button(text="Добавить", background_color=(0, 0.5, 0, 1))
        back_btn = Button(text="Назад", background_color=(0.3, 0.3, 0.3, 1))
        add_btn.bind(on_release=self.add_record)
        back_btn.bind(on_release=self.go_back)
        nav_buttons.add_widget(add_btn)
        nav_buttons.add_widget(back_btn)
        main_layout.add_widget(nav_buttons)

        self.add_widget(main_layout)
        self.refresh_data()

    def apply_filter(self, instance=None):
        self.refresh_data()

    def refresh_data(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({self.table_name})")
        self.columns = [col[1] for col in cursor.fetchall()]

        query = f"SELECT * FROM {self.table_name}"
        params = []
        if self.search_input.text:
            like_expr = " OR ".join([f"{col} LIKE ?" for col in self.columns])
            query += f" WHERE {like_expr}"
            params = [f"%{self.search_input.text}%"] * len(self.columns)

        cursor.execute(query, params)
        self.rows = cursor.fetchall()
        conn.close()

        if self.sort_column:
            index = self.columns.index(self.sort_column)
            self.rows.sort(key=lambda x: str(x[index]), reverse=self.sort_reverse)

        self.table_container.clear_widgets()
        self.selected_row = None
        self.edit_btn.disabled = True
        self.delete_btn.disabled = True

        for row in self.rows:
            row_text = " | ".join([str(cell) for cell in row])
            btn = Button(
                text=row_text,
                size_hint_y=None,
                height=44,
                halign='left',
                text_size=(Window.width - 40, None),
                background_color=(0.3, 0.3, 0.4, 1),
                color=(1, 1, 1, 1)
            )
            btn.bind(on_release=lambda inst, r=row: self.select_row(r, inst))
            self.table_container.add_widget(btn)

    def select_row(self, row, instance):
        self.selected_row = row
        self.edit_btn.disabled = False
        self.delete_btn.disabled = False

        for widget in self.table_container.children:
            widget.background_color = (0.3, 0.3, 0.4, 1)
        instance.background_color = (0.1, 0.6, 0.6, 1)

    def sort_by(self, column):
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        self.refresh_data()

    def go_back(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'main'

    def add_record(self, instance):
        self.manager.get_screen('form').load_form(self.table_name, self.columns)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = 'form'

    def edit_record(self, instance):
        if self.selected_row:
            self.manager.get_screen('form').load_form(self.table_name, self.columns, self.selected_row)
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = 'form'

    def delete_record(self, instance):
        if not self.selected_row:
            return
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        pk_column = self.columns[0]
        cursor.execute(f"DELETE FROM {self.table_name} WHERE {pk_column}=?", (self.selected_row[0],))
        conn.commit()
        conn.close()
        self.refresh_data()

class FormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inputs = []

    def load_form(self, table_name, columns, row=None):
        self.clear_widgets()
        self.inputs = []
        self.table_name = table_name
        self.existing_row = row

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        for i, col in enumerate(columns):
            line = BoxLayout(size_hint_y=None, height=40)
            label = Label(text=col, size_hint_x=0.3, color=(1,1,1,1))
            input_field = TextInput()
            if row:
                input_field.text = str(row[i])
                if i == 0:
                    input_field.disabled = True
            self.inputs.append((col, input_field))
            line.add_widget(label)
            line.add_widget(input_field)
            layout.add_widget(line)

        save_btn = Button(text="Сохранить", size_hint_y=None, height=44)
        cancel_btn = Button(text="Отмена", size_hint_y=None, height=44)
        save_btn.bind(on_release=self.save_record)
        cancel_btn.bind(on_release=self.cancel_form)

        layout.add_widget(save_btn)
        layout.add_widget(cancel_btn)
        self.add_widget(layout)

    def cancel_form(self, instance):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'table'

    def save_record(self, instance):
        values = [ti.text for _, ti in self.inputs]
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        if self.existing_row:
            set_clause = ', '.join([f"{col}=?" for col, _ in self.inputs[1:]])
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.inputs[0][0]}=?"
            data = [ti.text for _, ti in self.inputs[1:]] + [self.inputs[0][1].text]
        else:
            placeholders = ','.join(['?'] * len(values))
            query = f"INSERT INTO {self.table_name} VALUES ({placeholders})"
            data = values

        cursor.execute(query, data)
        conn.commit()
        conn.close()

        self.manager.get_screen('table').refresh_data()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = 'table'


class DBApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(TableScreen(name='table'))
        sm.add_widget(FormScreen(name='form'))
        return sm

if __name__ == '__main__':
    DBApp().run()
