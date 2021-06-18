import pygame
from pygame.locals import *
import math
import time
import random
import os
import json

#importing modules


sourceFileDir = os.path.dirname(os.path.abspath(__file__)) + "/images/"
#get file directory

flags =  DOUBLEBUF

pygame.init()
clock = pygame.time.Clock()

fileName = "gameSave.json"

displayWidth = 1000
displayHeight = 750

waterLevel = 350

#pygame display
storageSize = 10
balance = 0
maxBalance = 1000
debt = 0
balanceInterest = 1.05
debtInterest = 1.05

currentLocation = "pond"

selectedTextbox = None


fishNames = ["goldfish", "bass", "flounder", "salmon", "shark", "anglerfish"]

fishCounts = {"goldfish": 0, "bass": 0, "flounder": 0, "shark": 0, "anglerfish": 0, "salmon": 0}

fishPrices = {"goldfish": 10, "bass": 20, "flounder": 50, "salmon": 100, "shark": 200, "anglerfish": 500}

upgradeNames = ["fishing rod", "bait", "backpack", "bank", "boat"]

upgradeLevels = {"fishing rod": 0, "bait": 0, "backpack": 0, "bank": 0, "boat": 10}

locationNames = ["pond", "river", "lake", "waterfall", "beach", "ocean"]

boatImage = pygame.image.load(os.path.join(sourceFileDir, "bigBoat.png"))

gameDisplay = pygame.display.set_mode((displayWidth, displayHeight), flags)
 
fishRightImages = {}
fishLeftImages = {}

upgradeImages = {}

for name in fishNames:
    fishRightImages[name] = pygame.image.load(os.path.join(sourceFileDir, name + ".png"))
    fishLeftImages[name] = pygame.transform.flip(fishRightImages[name], True, False)

for name in upgradeNames:
    upgradeImages[name] = pygame.image.load(os.path.join(sourceFileDir, name + ".png"))

fishermanImage = pygame.image.load(os.path.join(sourceFileDir, "fisherman.png"))
backgroundImage = pygame.image.load(os.path.join(sourceFileDir, "background.png")).convert()
skyImage = pygame.image.load(os.path.join(sourceFileDir, "sky.png")).convert()
waterImage = pygame.image.load(os.path.join(sourceFileDir, "water.png"))

#displaying text

fishItemPositions = [(350, 100), (460, 100), (570, 100), (680, 100), (790, 100), (900, 100)]
sellButtonPositions = [(350, 175), (460, 175), (570, 175), (680, 175), (790, 175), (900, 175)]

upgradePositions = [(350, 250), (460, 250), (570, 250), (680, 250), (790, 250)]
upgradeButtonPositions = [(350, 325), (460, 325), (570, 325), (680, 325), (790, 325)]

font = pygame.font.SysFont('Calibri', 15)

fishList = []
textboxList = []
locationButtonList = []

def displayText(text, x, y):
    surface = font.render(text, True, (0, 0, 0))
    gameDisplay.blit(surface, (x, y))

class FishingRod():
    def __init__(self):
        self.startY = 182
        self.x = 300
        self.y = 182
        self.fish = None
    
    def update(self):
        pygame.draw.rect(gameDisplay, (102, 57, 49), (self.x - 2, self.startY, 4, (self.y - self.startY)))

        if self.fish:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)

        pygame.draw.rect(gameDisplay, color, (self.x - 8, self.y, 16, 16))

    def move(self, amount):
        self.y += amount
        self.y = max(self.y, self.startY)

class Textbox():
    def __init__(self, x, y, function, width = 100, height = 20,thickness = 3):
        self.x = x 
        self.y = y
        self.function = function
        self.width = width
        self.height = height
        self.thickness = thickness
        self.text = ""
        textboxList.append(self)

    def update(self):
        if selectedTextbox == self:
            color = (0, 255, 0)
        else:
            color = (0, 0, 0)

        pygame.draw.rect(gameDisplay, color, (self.x, self.y, self.width, self.height), self.thickness)
        displayText(self.text, self.x + 10, self.y)

class LocationButton():
    def __init__(self, x, y, location, width = 100, height = 20):
        self.x = x 
        self.y = y
        self.location = location
        self.width = width
        self.height = height
        locationButtonList.append(self)

    def update(self):
        if currentLocation == self.location:
            color = (0, 255, 0)
        else:
            color = (255, 0, 0)

        pygame.draw.rect(gameDisplay, color, (self.x, self.y, self.width, self.height))
        displayText(self.location, self.x + 10, self.y)


class Fish():
    def __init__(self, x, y, name):
        #initialise
        self.maxSpeedX = 2
        self.maxSpeedY = 1
        self.velocityX = self.maxSpeedX
        self.velocityY = self.maxSpeedY
        self.rect = pygame.Rect(x, y, 60, 59)
        self.state = "wander"
        self.name = name
        
        fishList.append(self)
    def update(self):
        fishingRodDistance = math.sqrt((fishingRod.x - self.rect.centerx) ** 2 + (fishingRod.y - self.rect.centery) ** 2)
        if fishingRodDistance <= (2 ** upgradeLevels["fishing rod"]) * 100 and fishingRod.fish == None:
            self.state = "follow"
        elif self.state != "caught":
            self.state == "wander"
        if self.state == "wander":
            if random.random() > 0.9:
                self.velocityX *= random.choice((1, -1))
            if random.random() > 0.9:
                self.velocityY = random.choice((1, 0, -1)) * self.maxSpeedY

        if self.state == "follow":
            if fishingRodDistance <= 10:
                if fishingRod.fish == None:
                    self.state = "caught"
                    fishingRod.fish = self
            else:
                self.velocityX = self.maxSpeedX * (fishingRod.x - self.rect.centerx)/fishingRodDistance
                self.velocityY = self.maxSpeedY * (fishingRod.y - self.rect.centery)/fishingRodDistance

        #check collisions with tiles, projectiles
        self.rect.x += self.velocityX
        self.rect.y += self.velocityY

        if self.rect.x <= -250 or self.rect.x >= 1250 or self.rect.y >= 1000:
            fishList.remove(self)

        self.rect.y = max(waterLevel, self.rect.y)

        if self.state == "caught":
            self.rect.centerx = fishingRod.x
            self.rect.centery = fishingRod.y
            if self.rect.y < waterLevel - 100:
                fishingRod.fish = None
                fishList.remove(self)
                if fishCounts[self.name] < storageSize:
                    fishCounts[self.name] += 1


        #newImage = pygame.transform.rotate(fishImage, math.degrees(self.angle))
        if (self.velocityX > 0):
            gameDisplay.blit(fishRightImages[self.name], (self.rect.x, self.rect.y))
        else:
            gameDisplay.blit(fishLeftImages[self.name], (self.rect.x, self.rect.y))


fishingRod = FishingRod()

def gameLoop():

    global fishList
    global currentLocation
    global balance 
    global maxBalance
    global storageSize
    global debt
    global fishCounts 
    global fishPrices 
    global upgradeLevels

    global selectedTextbox


    with open(os.path.join(sourceFileDir, fileName), 'r') as jsonFile:
        data = json.load(jsonFile)
    
    newFishList = data["fishList"].copy()

    for fish in newFishList:
        Fish(fish[0], fish[1], fish[2])

    currentLocation = data["currentLocation"]
    balance = data["balance"]
    maxBalance = data["maxBalance"]
    storageSize = data["storageSize"]
    debt = data["debt"]
    fishCounts = data["fishCounts"].copy()
    fishPrices = data["fishPrices"].copy()
    upgradeLevels = data["upgradeLevels"].copy()


    Textbox(650, 40, "borrow", 100, 20, 3)
    Textbox(850, 40, "repay", 100, 20, 3)

    for index, name in enumerate(locationNames):
        LocationButton(index * 150 + 75, 700, name)

    #enemy spawn positions, and cooldown

    fishSpawnCooldown = 2

    fishSpawnTimer = time.time() + fishSpawnCooldown
    
    interestCooldown = 10
    interestTimer = time.time() + interestCooldown

    randomEventCooldown = 15
    randomEventTimer = time.time() + randomEventCooldown

    randomEventText = ""

    #game loop, separate to main game loop
    while True:
        keys = pygame.key.get_pressed() 

        if keys[pygame.K_UP] or keys[pygame.K_w] :
            fishingRod.move(-5)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            fishingRod.move(5)

        mouseX, mouseY = pygame.mouse.get_pos()

        for event in pygame.event.get():
            #handling event and input

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if selectedTextbox:
                    if event.unicode.isnumeric() and len(selectedTextbox.text) < 10:
                        selectedTextbox.text += event.unicode 
                    
                    if event.key == pygame.K_BACKSPACE and len(selectedTextbox.text) > 0:
                        selectedTextbox.text = selectedTextbox.text[:-1]

                    if event.key == pygame.K_RETURN:
                        if selectedTextbox.function == "borrow":
                            balance += int(selectedTextbox.text)
                            balance = min(balance, maxBalance)
                            debt += int(selectedTextbox.text)
                        if selectedTextbox.function == "repay":
                            if int(selectedTextbox.text) <= balance:
                                balance -= int(selectedTextbox.text)
                                debt -= int(selectedTextbox.text)
                                debt = max(debt, 0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                for index, position in enumerate(sellButtonPositions):
                    if position[0] <= mouseX <= position[0] + 85 and position[1] <= mouseY <= position[1] + 25:
                        if fishCounts[fishNames[index]] > 0:
                            fishCounts[fishNames[index]] -= 1
                            balance += fishPrices[fishNames[index]]
                            balance = min(balance, maxBalance)

                for index, position in enumerate(upgradeButtonPositions):
                    if position[0] <= mouseX <= position[0] + 85 and position[1] <= mouseY <= position[1] + 25:
                        if balance >= (2 ** upgradeLevels[upgradeNames[index]]) * 1000:
                            balance -= (2 ** upgradeLevels[upgradeNames[index]]) * 1000
                            upgradeLevels[upgradeNames[index]] += 1

                for textbox in textboxList:
                    if textbox.x <= mouseX <= textbox.x + textbox.width and textbox.y <= mouseY <= textbox.y + textbox.height:
                        selectedTextbox = textbox

                for locationButton in locationButtonList:
                    if locationButton.x <= mouseX <= locationButton.x + locationButton.width and locationButton.y <= mouseY <= locationButton.y + locationButton.height:
                        if upgradeLevels["boat"] >= locationNames.index(locationButton.location):
                            currentLocation = locationButton.location
                            fishList.clear()
                
                if 450 <= mouseX <= 550 and 15 <= mouseY <= 35:
                    newFishList = []
                    for fish in fishList:
                        newFishList.append([fish.rect.x, fish.rect.y, fish.name])
                    data = {
                                "fishList": newFishList,
                                "currentLocation": currentLocation,
                                "balance": balance,
                                "maxBalance": maxBalance,
                                "storageSize": storageSize,
                                "debt": debt,
                                "fishCounts": fishCounts,
                                "fishPrices": fishPrices,
                                "upgradeLevels": upgradeLevels

                            }
                    with open(os.path.join(sourceFileDir, fileName), 'w') as jsonFile:
                        json.dump(data, jsonFile)

            if event.type == pygame.KEYUP:
                pass

        storageSize = (2 ** upgradeLevels["backpack"]) * 10
        maxBalance = (2 ** upgradeLevels["bank"]) * 1000

        #spawning fish at constant cooldown rate
        if time.time() > fishSpawnTimer:
            randomX = random.choice((0, 1000))
            randomY = random.randint(350, 750)
            fish = Fish(randomX, randomY, fishNames[locationNames.index(currentLocation)])
            fishSpawnCooldown = (2 ** -upgradeLevels["bait"])
            fishSpawnTimer += fishSpawnCooldown

        if time.time() > interestTimer:
            balance *= balanceInterest
            balance = min(balance, maxBalance)
            debt *= debtInterest
            interestTimer += interestCooldown
            
        if time.time() > randomEventTimer:
            if random.random() > 0.7:
                randomAmount = int(balance * 0.3)
                if random.random() > 0.5:
                    randomEventText = "You have found " + str(randomAmount)
                    balance += randomAmount

                else:
                    randomEventText = "You have lost " + str(randomAmount)
                    balance -= randomAmount
                    
                balance = min(maxBalance, balance)
                balance = max(0, balance)

            else:
                name = random.choice(fishNames)
                randomAmount = int(fishPrices[name] * 0.1)
                if random.random() > 0.5:
                    randomEventText = name + " price increased by " + str(randomAmount)
                    fishPrices[name] += randomAmount
                else:
                    randomEventText = name + " price decreased by " + str(randomAmount)
                    fishPrices[name] -= randomAmount

                fishPrices[name] = max(fishPrices[name], 0)

            randomEventTimer += randomEventCooldown

        #display background, and game objects
        gameDisplay.blit(backgroundImage, (0, 0))
        gameDisplay.blit(skyImage, (0, -500))
        gameDisplay.blit(waterImage, (0, 350))
        gameDisplay.blit(fishermanImage, (170, 150))
        gameDisplay.blit(boatImage, (-15, 290))

        fishingRod.update()
        for fish in fishList:
            fish.update()

        displayText("Sell Fish:", 350, 50)
        displayText("Buy Upgrades:", 350, 200)

        for index, position in enumerate(fishItemPositions):
            x, y = position
            gameDisplay.blit(fishRightImages[fishNames[index]], position)
            displayText(str(fishCounts[fishNames[index]]) + "/" + str(storageSize), x - 7, y + 50)
            displayText(fishNames[index], x - 7, y - 25)

        for index, position in enumerate(sellButtonPositions):
            x, y = position
            pygame.draw.rect(gameDisplay, (255, 0, 0), (x, y, 85, 20))
            displayText("sell", x, y)
            displayText("$" + str(fishPrices[fishNames[index]]), x + 30, y)

        for index, position in enumerate(upgradePositions):
            x, y = position
            gameDisplay.blit(upgradeImages[upgradeNames[index]], position)
            displayText("Level: " + str(upgradeLevels[upgradeNames[index]]), x - 7, y + 50)
            displayText(upgradeNames[index], x - 7, y - 25)

        for index, position in enumerate(upgradeButtonPositions):
            x, y = position
            pygame.draw.rect(gameDisplay, (255, 0, 0), (x, y, 100, 20))
            displayText("buy", x, y)
            displayText("$" + str((2 ** upgradeLevels[upgradeNames[index]]) * 1000), x + 30, y)

        displayText("Balance: $" + str(round(balance, 2)) + "/" + str(maxBalance), 25, 15)
        displayText("Debt: $" + str(round(debt, 2)), 250, 15)

        displayText("Borrow: (type amount below)", 650, 15)
        displayText("Repay Loans:", 850, 15)

        pygame.draw.rect(gameDisplay, (150, 150, 150), (75, 675, 100, 20))
        displayText("Locations: ", 80, 675)

        displayText("Messages: ", 25, 50)
        displayText(randomEventText, 25, 75)

        for textbox in textboxList:
            textbox.update()

        for locationButton in locationButtonList:
            locationButton.update()

        pygame.draw.rect(gameDisplay, (255, 0, 0), (450, 15, 100, 20))
        displayText("Save Game", 455, 15)

        #display screen 60 times per second
        pygame.display.update()

        clock.tick(60)



gameLoop()