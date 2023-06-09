from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.label import Label 
from kivy.uix.button import Button 
from kivy.lang import Builder
from kivy.app import App 
from kivy.clock import Clock 
from kivy.uix.textinput import TextInput
from kivy.uix.switch import Switch 
from jnius import autoclass 
from android.permissions import request_permissions,Permission,check_permission
from kivy.utils import platform
import os

from android.storage import app_storage_path
from datetime import datetime
#import subprocess
import ffmpeg
import time
from android import mActivity
from android.storage import primary_external_storage_path
'''
import moviepy.editor as mp
clip = mp.VideoFileClip('vid.mp4')
audio = clip.audio
audio.write_audiofile('audio.mp3')
'''

'''
from datetime import datetime

d = datetime.now()
d = d.strftime("%d_%m_%Y_%H%M%S")

if platform == 'android':
    from android.storage import primary_external_storage_path
    #dir = primary_external_storage_path()
    #download_dir_path = os.path.join(dir, 'Download') 
    
    path_to_dcim = join(dirname(App.get_running_app()._user_data_dir), 'DCIM')
    print(path_to_dcim)
    
    #storage_path = (path_to_dcim + '/kivy_recording.3gp')
    
    #print(dir) 
'''
  

Builder.load_string('''
<AudioTool>
    orientation: 'vertical'
    Label:
        id: display_label
        text: '00:00'
    BoxLayout:
        size_hint: 1, .2
        TextInput:
            id: user_input
            text: '5'
            disabled: duration_switch.active == False #TUT 3 IF SWITCH IS OFF TEXTINPUT IS DISABLED 
            on_text: root.enforce_numeric()
              
        Switch:
            id: duration_switch
                        
    BoxLayout:
        Button:
            id: start_button
            text: 'Start Recording'
            on_release: root.startRecording_clock()
 
        Button:
            id: stop_button
            text: 'Stop Recording'
            on_release: root.stopRecording()
            disabled: True
''')
 
class MyRecorder:
    def __init__(self):
        #storage_file = App.get_running_app().storage
        #get_app = App.get_running_app()
        #self.user_dir = get_app.getattr(self, 'user_data_dir') 
        #print(storage_file)
        
        
        '''Recorder object To access Android Hardware'''
        self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        self.OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
        self.AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')
 
        # create out recorder
        self.mRecorder = self.MediaRecorder()
        self.mRecorder.setAudioSource(self.AudioSource.MIC)
        self.mRecorder.setOutputFormat(self.OutputFormat.MPEG_4)
        self.mRecorder.setOutputFile('testaudio.mp4')
        #self.mRecorder.setOutputFile(storage_file)
        #self.mRecorder.setOutputFile('/sdcard/MYAUDIO_{}.3gp'.format(d))
        self.mRecorder.setAudioEncoder(self.AudioEncoder.AMR_NB)
        self.mRecorder.prepare()
        #print(mRecorder)
 
 
 
class AudioApp(App):
    def build(self):
        request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO,Permission.READ_EXTERNAL_STORAGE,Permission.WRITE_EXTERNAL_STORAGE])
        settings_path = app_storage_path()
        print("path")
        print(settings_path)
        dirCheck = primary_external_storage_path()
        print("external path")
        print(dirCheck)
        
        #self.appdir = self.user_data_dir
        #print(self.appdir)
        #data_dir = getattr(self, 'user_data_dir')
        #store = JsonStore(join(data_dir,'user.json'))
        return AudioTool()
        
     
 
 
 
class AudioTool(BoxLayout):
    def __init__(self, **kwargs):
        super(AudioTool, self).__init__(**kwargs)
        
        self.start_button = self.ids['start_button']
        self.stop_button = self.ids['stop_button']
        self.display_label = self.ids['display_label']
        self.switch = self.ids['duration_switch'] # Tutorial 3
        self.user_input = self.ids['user_input']
            
 
    def enforce_numeric(self): 
        '''Make sure the textinput only accepts numbers'''
        if self.user_input.text.isdigit() == False: 
            digit_list = [num for num in self.user_input.text if num.isdigit()]
            self.user_input.text = "".join(digit_list)
 
    def startRecording_clock(self):
        
        self.mins = 0 #Reset the minutes
        self.zero = 1 # Reset if the function gets called more than once
        self.duration = int(self.user_input.text) #Take the input from the user and convert to a number
        Clock.schedule_interval(self.updateDisplay, 1)
        self.start_button.disabled = True # Prevents the user from clicking start again which may crash the program
        self.stop_button.disabled = False
        self.switch.disabled = True #TUT Switch disabled when start is pressed
        Clock.schedule_once(self.startRecording) ## NEW start the recording 
    
    def startRecording(self, dt): #NEW start the recorder
        self.r = MyRecorder()
        self.r.mRecorder.start()
        print("started recording")
        #For future to read from buffer
        #https://stackoverflow.com/questions/54763550/android-audiorecord-buffer-starts-with-a-number-of-0s-before-meaningful-values
        #audio[]
        #self.r.mRecorder.read(new short[10000], 0, 10000); // have to include this to remove redundant values
        #self.r.mRecorder.read(audio, 0, 500);
        
        #For future get max amplitude - use clock to call often
        #start recording and listen for max amplitude. When it occurs stop recording, dont save file
        #have a max time of example 10 seconds if no large amplitude then stop and start again
        #and start recording again for 1.5 seconds then stop, save file and check for match.
        Clock.schedule_interval(self.startGetMaxAmplitude,0.001) ## NEW start the recording 
        

        
    def startGetMaxAmplitude(self, dt):     
        amplitude = self.r.mRecorder.getMaxAmplitude();
        print('amplitude')
        print(amplitude)    
    
       
    
    def stopRecording(self):
    
        Clock.unschedule(self.updateDisplay)
        Clock.unschedule(self.startGetMaxAmplitude)
        self.r.mRecorder.stop() #NEW RECORDER VID 6
        self.r.mRecorder.release() #NEW RECORDER VID 6
        
        Clock.unschedule(self.startRecording) #NEW stop the recording of audio VID 6 
        self.display_label.text = 'Finished Recording!'
        self.start_button.disabled = False
        self.stop_button.disabled = True #TUT 3
        self.switch.disabled = False #TUT 3 re enable the switch
        print("stopped recording")
  
        d = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
       
        print("time of recording finished")
        print(d)
        
        


        
        context = mActivity.getApplicationContext()
        result =  context.getExternalFilesDir(None)   # don't forget the argument
        #result =  context.getExternalCacheDir()
        if result:
            self.storage_path =  str(result.toString())       
            print("storage path")
            print(self.storage_path)
        
 
        #input_file = 'testaudio.mp4'
        #output_file = 'output2.wav'
        #subprocess.run(['ffmpeg', '-i', input_file, '-acodec', 'pcm_s16le', '-ar', '44100', output_file])
        #self.outPutFile = self.storage_path + "/wav/output2.wav"
        
        
        #self.outPutFile  = "/data/data/org.example.c4k_tflite_audio1/files/app/wav/output2.wav"
        #self.inPutFile  = "/data/data/org.example.c4k_tflite_audio1/files/app/wav/testaudio.mp4"
        
        self.outPutFile  = "/data/data/org.example.c4k_tflite_audio1/files/app/output2.wav"
        self.inPutFile  = "/data/data/org.example.c4k_tflite_audio1/files/app/testaudio.mp4"
        print("self.outPutFile")
        print(self.outPutFile)
        
        
        '''
        command2wav = "ffmpeg -i " + self.inPutFile + " " + self.outPutFile
        #ffmpeg -i <infile> -ac 2 -f wav <outfile>
        #ffmpeg_cmd = 'ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 output.wav'
        result_code = os.system(command2wav + ' > output.txt')
        '''
        
        #os.system(f"""ffmpeg -i testaudio.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 output3.wav""")  
        
        #result = os.system('ffmpeg -i testaudio.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 ' + self.outPutFile) 
        
        
        input = ffmpeg.input('10.mp4')
        audio = input.audio.filter("aecho", 0.8, 0.9, 1000, 0.3)
        video = input.video.hflip()
        out = ffmpeg.output(audio, video, 'out.mp4')
        
        
        
      
        
        
        time.sleep(10)
        print("files in pwd")
        print(os.listdir())
        print("finished creating wav file")
        
        '''
        if os.path.exists('output.txt'):
            fp = open('output.txt', "r")
            output = fp.read()
            fp.close()
            os.remove('output.txt')
            print("command output")
            print(output)        
        '''
        
        
        
        self.play()
        
        
        
    def play(self):
        MediaPlayer = autoclass('android.media.MediaPlayer')
        AudioManager = autoclass('android.media.AudioManager')

        self.sound = MediaPlayer()
        #self.sound.setDataSource(yourDataSource) #you can provide any data source, if its on the devie then the file path, or its url if you are playing online
        #self.sound.setDataSource('testaudio.mp4') 
        #self.audio_path = self.storage_path + "/wav/output2.wav"
        #self.audio_path = self.storage_path + "/wav/output1.wav" ##cant find folder
        
        dirCheck1 = primary_external_storage_path()
        print("external path1")
        print(dirCheck1)        
        
        
        
        #self.audio_path = dirCheck1 + "/wav/output1.wav"
        #self.audio_path = "/storage/emulated/0/org.example.c4k_tflite_audio1/wav/output1.wav"##Not found
        #self.audio_path = "/data/data/org.example.c4k_tflite_audio1/files/app/wav/output2.wav"
        #self.audio_path = "/data/data/org.example.c4k_tflite_audio1/files/app/output2.wav"        
        self.audio_path  = "/data/data/org.example.c4k_tflite_audio1/files/app/testaudio.mp4"
     
        self.sound.setDataSource(self.audio_path) 
        self.sound.prepare()
        self.sound.setLooping(False) #you can set it to true if you want to loop
        self.sound.start()
        print("start play")

        e = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
       
        print("time of start playing audio")
        print(e)
        # You can also use the following according to your needs
        #self.sound.pause()
        #self.sound.stop()
        #self.sound.release()
        #self.sound.getCurrentPosition()
        #self.sound.getDuration()       
        
         
    def updateDisplay(self,dt):   
        if self.switch.active == False:
            if self.zero < 60 and len(str(self.zero)) == 1:
                self.display_label.text = '0' + str(self.mins) + ':0' + str(self.zero)
                self.zero += 1
                
            elif self.zero < 60 and len(str(self.zero)) == 2:
                    self.display_label.text = '0' + str(self.mins) + ':' + str(self.zero)
                    self.zero += 1
            
            elif self.zero == 60:
                self.mins +=1
                self.display_label.text = '0' + str(self.mins) + ':00'
                self.zero = 1
        
        elif self.switch.active == True:
            if self.duration == 0: # 0
                self.display_label.text = 'Recording Finished!'
                self.stopRecording() # NEW VID 6 / THIS ONE LINE SHOULD TAKE CARE OF THE RECORDING NOT STOPPING. 
                
                #self.start_button.disabled = False # Re enable start
                #self.stop_button.disabled = True # Re disable stop
                #Clock.unschedule(self.updateDisplay) #DELETE FOR VID 6 
                
                #self.switch.disabled = False # Re enable the switch
                
            elif self.duration > 0 and len(str(self.duration)) == 1: # 0-9
                self.display_label.text = '00' + ':0' + str(self.duration)
                self.duration -= 1
 
            elif self.duration > 0 and self.duration < 60 and len(str(self.duration)) == 2: # 0-59
                self.display_label.text = '00' + ':' + str(self.duration)
                self.duration -= 1
 
            elif self.duration >= 60 and len(str(self.duration % 60)) == 1: # EG 01:07
                self.mins = self.duration / 60
                self.display_label.text = '0' + str(self.mins) + ':0' + str(self.duration % 60)
                self.duration -= 1
 
            elif self.duration >= 60 and len(str(self.duration % 60)) == 2: # EG 01:17
                self.mins = self.duration / 60
                self.display_label.text = '0' + str(self.mins) + ':' + str(self.duration % 60)
                self.duration -= 1
 
 
if __name__ == '__main__':
    AudioApp().run()
