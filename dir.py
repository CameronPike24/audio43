from kivy.app import App
from kivy.uix.label import Label
from os.path import abspath
from os import getcwd

class MyApp(App):

    def build(self):
        text = App.get_running_app().user_data_dir + '\n'
        text += self.user_data_dir + '\n'
        text += app_storage_path() + '\n'
        text += getcwd() + '\n'
        text += abspath('.') + '\n'
        text += abspath('~') + '\n'
        text += abspath(__file__) +'\n'
        return Label(text=text)
        

if __name__ == '__main__':
    MyApp().run()
