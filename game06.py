import os
import sys
import random
import pygame as pg

# 必須条件：カレントディレクトリをこのファイルがある場所に変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------
# 【拡張機能のインポート領域】
# 各メンバーは担当機能が完成したらコメントアウトを外して統合する
# ---------------------------------------------------------
# import feature_player_ex  # 追加1：プレイヤーのダッシュ、アニメーション、残像エフェクト
# import feature_boss       # 追加2：定期的に襲来するボスキャラや妨害ビーム
# import feature_special    # 追加3：磁石や無敵などの特殊効果アイテム
# import feature_combo      # 追加4：連続キャッチによるコンボシステムと高度なスコア計算
# import feature_scene      # 追加5：本格的なタイトル画面、リザルト画面、BGM管理

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((80, 20))
        self.image.fill((0, 100, 255))
        self.rect = self.image.get_rect(center=(400, 550))

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] and self.rect.left > 0:
            self.rect.x -= 8
        if keys[pg.K_RIGHT] and self.rect.right < 800:
            self.rect.x += 8

#追加機能3(C0A25119)
class SpecialItem(pg.sprite.Sprite):
    """
    金のスペシャルアイテムを管理するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((25, 25))
        self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(center=(random.randint(25, 775), 0))
        self.speed = random.randint(6, 10)
    def update(self):
        """
        アイテムの位置の更新,画面外に出たら消去
        """
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill()

class SpecialManager:
    """
    スペシャルアイテムの生成・当たり判定・描画を統括するクラス
    """
    def __init__(self):
        self.specials = pg.sprite.Group()

    def update(self, player):
        """
        ランダム生成とプレイヤーの当たり判定、獲得したボーナススコアを返す
        """
        bonus = 0
        if random.randint(1, 300) == 1:
            self.specials.add(SpecialItem())
        self.specials.update()
        caught = pg.sprite.spritecollide(player, self.specials, True)
        for c in caught:
            bonus += 50
        return bonus
    
    def draw(self, screen):
        """
        画面にスペシャルアイテム群を描画する
        """
        self.specials.draw(screen)

class Apple(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((20, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(random.randint(20, 780), 0))
        self.speed = random.randint(4, 7)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill() # 画面外に出たら消去

def main():
    pg.init()
    screen = pg.display.set_mode((800, 600))
    pg.display.set_caption("アイテムキャッチ・パニック - 完全版ベース")
    clock = pg.time.Clock()
    font = pg.font.SysFont(None, 36)

    all_sprites = pg.sprite.Group()
    apples = pg.sprite.Group()

    player = Player()
    all_sprites.add(player)

    special_manager = SpecialManager() #追加機能3

    score = 0
    start_ticks = pg.time.get_ticks()
    game_duration = 60000 # 60秒

    # ---------------------------------------------------------
    # 【拡張機能の初期化領域】
    # ---------------------------------------------------------
    # boss_manager = feature_boss.BossManager()
    # combo_system = feature_combo.ComboSystem()

    while True:
        # 1. イベント処理
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        # 経過時間の計算
        seconds_left = max(0, (game_duration - (pg.time.get_ticks() - start_ticks)) // 1000)

        # 2. 更新処理
        if seconds_left > 0:
            all_sprites.update()

            score += special_manager.update(player) #追加機能3
            
            # アイテムのランダム生成
            if random.randint(1, 30) == 1:
                apple = Apple()
                all_sprites.add(apple)
                apples.add(apple)

            # 当たり判定（キャッチ）
            caught_apples = pg.sprite.spritecollide(player, apples, True)
            for apple in caught_apples:
                score += 10
                # combo_system.add_combo() # 拡張機能4への連携例
                
            # boss_manager.update(player.rect) # 拡張機能2への連携例
        
        # 3. 描画処理
        screen.fill((240, 255, 240))
        all_sprites.draw(screen)

        special_manager.draw(screen) #追加機能3

        # UI描画
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        time_text = font.render(f"Time: {seconds_left}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (680, 10))

        if seconds_left == 0:
            end_text = font.render("TIME UP!", True, (255, 0, 0))
            screen.blit(end_text, (350, 300))

        pg.display.update()
        clock.tick(60)


if __name__ == "__main__":
    main()