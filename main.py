import sys
import json
import os
import random
import pygame
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QMessageBox, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

# --- CONSTANTS & SETTINGS ---
SETTINGS = {
    "WIDTH": 450,
    "HEIGHT": 700,
    "LANES": [75, 225, 375],
    "SAVE_FILE": "save_data.json"
}

# --- DATA MANAGEMENT ---
def load_data():
    if not os.path.exists(SETTINGS["SAVE_FILE"]):
        data = {"coins": 0, "high_score": 0, "unlocked": ["player_default.png"], "equipped": "player_default.png"}
        save_data(data)
        return data
    with open(SETTINGS["SAVE_FILE"], "r") as f:
        return json.load(f)

def save_data(data):
    with open(SETTINGS["SAVE_FILE"], "w") as f:
        json.dump(data, f)

# --- PYGAME ENGINE ---
class SubwayGame:
    def __init__(self, avatar_path):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SETTINGS["WIDTH"], SETTINGS["HEIGHT"]))
        self.clock = pygame.time.Clock()
        self.avatar_path = f"assets/images/{avatar_path}"
        self.running = True
        self.data = load_data()
        
        # Load Sounds
        try:
            self.coin_sound = pygame.mixer.Sound("assets/sounds/coin.wav")
            self.jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
            pygame.mixer.music.load("assets/sounds/music.mp3")
            pygame.mixer.music.play(-1)
        except:
            print("Sound files missing, skipping audio.")

    def run(self):
        # Player Setup
        player_img = pygame.image.load(self.avatar_path).convert_alpha()
        player_img = pygame.transform.scale(player_img, (80, 110))
        player_rect = player_img.get_rect(center=(225, 600))
        
        lane = 1
        vel_y = 0
        is_jumping = False
        score = 0
        collected_coins = 0
        
        obstacles = []
        coins = []
        speed = 8

        while self.running:
            self.screen.fill((135, 206, 235)) # Sky Blue
            
            # Draw Road
            pygame.draw.rect(self.screen, (50, 50, 50), (50, 0, 350, 700))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT and lane > 0:
                        lane -= 1
                    if event.key == pygame.K_RIGHT and lane < 2:
                        lane += 1
                    if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not is_jumping:
                        is_jumping = True
                        vel_y = -18
                        try: self.jump_sound.play()
                        except: pass

            # Jump Physics
            if is_jumping:
                player_rect.y += vel_y
                vel_y += 1
                if player_rect.y >= 545:
                    player_rect.y = 545
                    is_jumping = False

            # Smooth Lane Movement
            target_x = SETTINGS["LANES"][lane]
            player_rect.centerx += (target_x - player_rect.centerx) * 0.2

            # Spawn Obstacles/Coins
            if random.randint(1, 40) == 1:
                obstacles.append(pygame.Rect(random.choice(SETTINGS["LANES"]) - 35, -50, 70, 50))
            if random.randint(1, 60) == 1:
                coins.append(pygame.Rect(random.choice(SETTINGS["LANES"]) - 15, -50, 30, 30))

            # Move and Draw Obstacles
            for obs in obstacles[:]:
                obs.y += speed
                pygame.draw.rect(self.screen, (200, 0, 0), obs)
                if obs.colliderect(player_rect) and not is_jumping: # Can jump over low obstacles
                    self.running = False # Game Over
                if obs.y > 700: obstacles.remove(obs)

            # Move and Draw Coins
            for coin in coins[:]:
                coin.y += speed
                pygame.draw.ellipse(self.screen, (255, 215, 0), coin)
                if coin.colliderect(player_rect):
                    collected_coins += 1
                    coins.remove(coin)
                    try: self.coin_sound.play()
                    except: pass
                if coin.y > 700: coins.remove(coin)

            self.screen.blit(player_img, player_rect)
            
            # UI
            score += 1
            font = pygame.font.SysFont("Arial", 24, bold=True)
            self.screen.blit(font.render(f"Score: {score//10}", True, (255,255,255)), (10, 10))
            self.screen.blit(font.render(f"Coins: {collected_coins}", True, (255, 215, 0)), (10, 40))

            pygame.display.flip()
            self.clock.tick(60)

        # Save Data
        self.data["coins"] += collected_coins
        if (score//10) > self.data["high_score"]:
            self.data["high_score"] = score//10
        save_data(self.data)
        pygame.quit()

# --- PYQT6 UI (LAUNCHER & SHOP) ---
class Launcher(QWidget):
    def __init__(self):
        super().__init__()
        self.data = load_data()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Dev Runner Launcher")
        self.setFixedSize(400, 500)
        self.setStyleSheet("background-color: #2c3e50; color: white;")

        self.layout = QVBoxLayout()

        self.title = QLabel("DEV RUNNER")
        self.title.setFont(QFont("Impact", 40))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.stats = QLabel(f"High Score: {self.data['high_score']} | Coins: {self.data['coins']}")
        self.stats.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.play_btn = QPushButton("START MISSION")
        self.play_btn.setStyleSheet("background-color: #27ae60; padding: 15px; font-weight: bold;")
        self.play_btn.clicked.connect(self.start_game)

        self.shop_btn = QPushButton("OPEN SHOP")
        self.shop_btn.setStyleSheet("background-color: #2980b9; padding: 15px; font-weight: bold;")
        self.shop_btn.clicked.connect(self.open_shop)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.stats)
        self.layout.addSpacing(50)
        self.layout.addWidget(self.play_btn)
        self.layout.addWidget(self.shop_btn)
        
        self.setLayout(self.layout)

    def start_game(self):
        self.hide() # Hide Launcher
        game = SubwayGame(self.data["equipped"])
        game.run()
        self.data = load_data() # Refresh data
        self.stats.setText(f"High Score: {self.data['high_score']} | Coins: {self.data['coins']}")
        self.show()

    def open_shop(self):
        shop = ShopWindow(self)
        shop.show()

class ShopWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.data = load_data()
        self.setFixedSize(300, 400)
        self.setWindowTitle("The Dev Shop")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Your Balance: {self.data['coins']} Coins"))

        # Skin 1: Default
        btn1 = QPushButton("Equip Default Avatar")
        btn1.clicked.connect(lambda: self.select_skin("player_default.png"))
        layout.addWidget(btn1)

        # Skin 2: Golden Skin (Cost 100)
        skin2_name = "player_gold.png"
        if skin2_name in self.data["unlocked"]:
            btn2 = QPushButton("Equip Golden Avatar")
        else:
            btn2 = QPushButton(f"Buy Golden Avatar (100 Coins)")
        
        btn2.clicked.connect(lambda: self.buy_skin(skin2_name, 100))
        layout.addWidget(btn2)

        self.setLayout(layout)

    def buy_skin(self, name, cost):
        if name in self.data["unlocked"]:
            self.select_skin(name)
        elif self.data["coins"] >= cost:
            self.data["coins"] -= cost
            self.data["unlocked"].append(name)
            save_data(self.data)
            QMessageBox.information(self, "Success", "Skin Purchased!")
            self.close()
        else:
            QMessageBox.warning(self, "Poor Developer", "Not enough coins! Go code more.")

    def select_skin(self, name):
        self.data["equipped"] = name
        save_data(self.data)
        self.parent.data = self.data
        QMessageBox.information(self, "Equipped", f"Ready to run with {name}")
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = Launcher()
    launcher.show()
    sys.exit(app.exec())