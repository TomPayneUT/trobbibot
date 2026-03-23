import pygame
import os

def play_audio(filename):
    if not os.path.exists(filename):
        print(f'File {filename} not found')
        return
    
    try:
        #initialize only the mixer to save resources
        pygame.mixer.init()

        #Load and play
        sound = pygame.mixer.Sound(filename)
        channel = sound.play()


        #Keep the script alive while the robot is spaking
        while channel.get_busy():
            pygame.time.wait(100)

        #optional: clean up to free the audio device
        pygame.mixer.quit()
    except Exception as e:
        print(f'Playback failed {e}')

if __name__=='__main__':
    play_audio('static/sounds/temp_output.wav')


        