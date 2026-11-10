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

# ---------------------------------------------------------
# 画像を安全に探して読み込む補助関数
# ---------------------------------------------------------
def load_image(filename_stem, size):
    """png/jpg や fig/ フォルダの有無に対応して画像を自動探索して読み込む"""
    candidates = [
        os.path.join("fig", f"{filename_stem}.png"),
        os.path.join("fig", f"{filename_stem}.jpg"),
        os.path.join("fig", f"{filename_stem}.jpeg"),
        f"{filename_stem}.png",
        f"{filename_stem}.jpg",
        f"{filename_stem}.jpeg",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                img = pg.image.load(path)
                return pg.transform.scale(img, size).convert_alpha()
            except Exception:
                pass
    # 画像がない場合はNoneを返して図形描写に切り替える
    return None

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

# =========================================================
# ★追記：1. エネルギーシールド（取ったら5秒間バリア）
# =========================================================
class EnergyShield(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        # 画面サイズ40x40でシールド画像を読み込み（見つからない場合は水色枠）
        img = load_image("shi-rudo", (40, 40))
        if img:
            self.image = img
        else:
            self.image = pg.Surface((40, 40))
            self.image.fill((50, 200, 255))
        
        # 横軸ランダム、画面最上部から落下開始
        self.rect = self.image.get_rect(center=(random.randint(30, 770), 0))
        self.speed = random.randint(4, 7)

    def update(self):
        # 下方向に落下移動させて、画面外（y>600）に出たら自動削除
        self.rect.y += self.speed
        if self.rect.top > 600:  # 画面下に落ちたら消滅
            self.kill()


class ShieldManager:

    def __init__(self):
        self.shields = pg.sprite.Group()
        self.duration = 5000  # バリアの持続時間：5秒（5000ミリ秒）
        self.active_until = 0 #バリア終了タイマーの保管場所

    def update(self, player):
        # 1/600の確率でシールドアイテムを出現させる
        if random.randint(1, 600) == 1:
            self.shields.add(EnergyShield())

        self.shields.update()

        # プレイヤーと当たったら5秒後の時刻を計算して保持
        if pg.sprite.spritecollide(player, self.shields, True):
            self.active_until = pg.time.get_ticks() + self.duration

    def is_active(self):
        # 現在時刻が終了予定時刻より前なら有効状態と判定
        return pg.time.get_ticks() < self.active_until

    def draw(self, screen, player):
        self.shields.draw(screen)
        # バリア有効中はプレイヤーを囲む青い四角枠を描画
        if self.is_active():
            pg.draw.rect(
                screen, (50, 200, 255), player.rect.inflate(16, 16), 3
            )

# =========================================================
# ★追記：2. データチップ（画像: tippu.jpg / 即時+100点）
# =========================================================
class DataChip(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        # tippu.jpg を読み込み（無ければ青四角）
        img = load_image("tippu", (40, 40))
        if img:
            self.image = img
        else:
            self.image = pg.Surface((40, 40))
            self.image.fill((0, 200, 255))

        self.rect = self.image.get_rect(center=(random.randint(30, 770), 0))
        self.speed = random.randint(5, 8) # 他のアイテムより少し速く落ちる

    def update(self):
        # 落下処理（画面外で消去）
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill()

class DataChipManager:

    def __init__(self):
        self.chips = pg.sprite.Group()

    def update(self, player):
        # 出現率：1/1000
        if random.randint(1, 1000) == 1:
            self.chips.add(DataChip())

        self.chips.update()
        # プレイヤーがキャッチしたら 1個につき+100点 加算
        caught = pg.sprite.spritecollide(player, self.chips, True)
        return len(caught) * 100

    def draw(self, screen):
        self.chips.draw(screen)


# =========================================================
# ★追記：3. ブラックホール（画像: kokuu.jpg / 取ったら5秒間吸引効果）
# =========================================================
class BlackHole(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        # kokuu.jpg を読み込み
        img = load_image("kokuu", (40, 40))
        if img:
            self.image = img
        else:
            self.image = pg.Surface((40, 40))
            self.image.fill((150, 0, 200))

        self.rect = self.image.get_rect(center=(random.randint(30, 770), 0))
        self.speed = random.randint(4, 7)

    def update(self):
        # 落下処理（画面外で消去）
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.kill()
class BlackHoleManager:

    def __init__(self):
        self.blackholes = pg.sprite.Group()
        self.duration = 2500  # 持続時間: 2.5秒
        self.active_until = 0

        # オーラ用画像の読み込み（60x60サイズ）
        self.aura_img = load_image("kokuu", (60, 60))

    def update(self, player, item_groups):
        # 出現率：1/1500
        if random.randint(1, 1500) == 1:
            self.blackholes.add(BlackHole())

        self.blackholes.update()

        # キャッチしたら 2.5秒間 吸引モードを発動
        if pg.sprite.spritecollide(player, self.blackholes, True):
            self.active_until = pg.time.get_ticks() + self.duration

        # 吸引モード発動中：半径350px以内のリンゴを自機へ強力移動させる
        if self.is_active():
            for group in item_groups:
                for target in group:
                    dx = player.rect.centerx - target.rect.centerx
                    dy = player.rect.centery - target.rect.centery
                    dist = (dx**2 + dy**2) ** 0.5
                    if 0 < dist < 350:
                        target.rect.x += int(dx / dist * 6)
                        target.rect.y += int(dy / dist * 6)

    def is_active(self):
        # 2.5秒経過前かどうかチェック
        return pg.time.get_ticks() < self.active_until

    def draw(self, screen, player):
        self.blackholes.draw(screen)

        # 吸引バフ中はプレイヤーの周りに kokuu.jpg の渦オーラを表示
        if self.is_active():
            if self.aura_img:
                aura_rect = self.aura_img.get_rect(center=player.rect.center)
                screen.blit(self.aura_img, aura_rect)
            else:
                pg.draw.circle(
                    screen, (150, 0, 200), player.rect.center, 40, 2
                )

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

    shield_manager = ShieldManager()
    datachip_manager = DataChipManager()
    blackhole_manager = BlackHoleManager()

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
            shield_manager.update(player)  # 追加 シールドの移動・生成・当たり判定を実行
            score += datachip_manager.update(player)
            blackhole_manager.update(
                player, item_groups=[apples]
            )  # リンゴを引き寄せる
            
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
        shield_manager.draw(screen, player)  # 追加 シールド本体とバリア枠を描画
        datachip_manager.draw(screen)
        blackhole_manager.draw(screen, player)

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