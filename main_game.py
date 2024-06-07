import io
import json
import pygame
import forced_alignment
import time

# helper function

def read_from_sync_json(readData="begin", filePath="syncmap.json"):
    with open(filePath, 'r') as file:
        data = json.load(file)
    arrayOfData = []
    for fragment in data["fragments"]:
        if readData == "begin":
            arrayOfData.append(float(fragment["end"]) - float(fragment["begin"]))
        else:
            arrayOfData.append(fragment[readData])
    return arrayOfData

# question setup
answer = forced_alignment.generate_sync_map()
text_array = []
with io.open('myFile.txt', 'r', encoding='utf-8') as questions:
    text_array = questions.read().split("\n")
intervals = read_from_sync_json()

# pygame setup
pygame.init()
length, height = 1280, 720

screen = pygame.display.set_mode((length, height))
clock = pygame.time.Clock()
running = True
audio_file = "audio.mp3"

pygame.mixer.music.load(audio_file)

# used variables
displayedText = []
currentLine = ""
currentWord = 0
currentYLocation = 10
paused = False
pause_duration = 2  # in seconds
start = False
nextQuestion = False

font = pygame.font.Font(None, 20)

# Track audio and text display timing
audio_start_time = time.time()
text_start_time = time.time()

while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and not start:
                start = True
                if nextQuestion:
                    displayedText = []
                    currentLine = ""
                    currentWord = 0
                    forced_alignment.generate_sync_map()
                    print("Made Sync Map")
                    text_array = []
                    with io.open('myFile.txt', 'r', encoding='utf-8') as questions:
                        print("Splitting and processing text")
                        text_array = questions.read().split("\n")
                    intervals = read_from_sync_json()
                    pygame.mixer.music.load(audio_file)

                print("Played audio")
                pygame.mixer.music.play()
            if event.key == pygame.K_SPACE:
                paused = not paused
                if paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
                    audio_start_time = time.time() - (pygame.mixer.music.get_pos() / 1000)  # Adjust text start time based on audio position

    # game logic
    if not paused:
        if start:
            if currentWord >= len(intervals):
                start = False
                nextQuestion = True
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                continue
            audio_elapsed = time.time() - audio_start_time
            text_elapsed = time.time() - text_start_time

            #print(audio_elapsed, text_elapsed)

            # Synchronize text display with audio playback position
            if text_elapsed >= intervals[currentWord] - 0.01:
                currentLine += " " + str(text_array[currentWord])
                currentWord += 1
                text_start_time = time.time()

            if font.size(currentLine)[0] >= 500:
                displayedText.append(currentLine)
                currentLine = ""

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # RENDER YOUR GAME HERE
    previousYLocation = currentYLocation
    topLine = font.render(str(currentLine), True, (0, 0, 0))
    screen.blit(topLine, (30, currentYLocation + (20 * (len(displayedText) + 1))))
    for line in displayedText:
        currentYLocation += 20
        screen.blit(font.render(str(line), True, (0, 0, 0)), (30, currentYLocation))
    currentYLocation = previousYLocation

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(120)  # limits FPS to 60

pygame.quit()