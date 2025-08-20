import sys
import pygame
import random

class Ship:
    """Player ship that can move and shoot"""
    
    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        
        # Ship appearance
        self.image = pygame.Surface((50, 60))
        self.image.fill((100, 100, 255))
        self.rect = self.image.get_rect()
        
        # Start at bottom center
        self.rect.midbottom = self.screen_rect.midbottom
        
        # Movement
        self.x = float(self.rect.x)
        self.moving_right = False
        self.moving_left = False
        self.speed = 15
    
    def reset_position(self):
        """Reset ship to starting position"""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)
    
    def update(self):
        """Update position based on movement flags"""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.speed
        
        self.rect.x = self.x
    
    def draw(self):
        """Draw ship at current location"""
        self.screen.blit(self.image, self.rect)


class Bullet:
    """Bullets fired from ship"""
    
    def __init__(self, screen, ship):
        self.screen = screen
        self.rect = pygame.Rect(0, 0, 5, 15)
        self.rect.centerx = ship.rect.centerx
        self.rect.bottom = ship.rect.top
        
        self.y = float(self.rect.y)
        self.speed = 15
        self.color = (255, 255, 0)
    
    def update(self):
        """Move bullet up screen"""
        self.y -= self.speed
        self.rect.y = self.y
    
    def draw(self):
        """Draw bullet"""
        pygame.draw.rect(self.screen, self.color, self.rect)


class Alien:
    """Single alien in the fleet"""
    
    def __init__(self, screen, x, y):
        self.screen = screen
        self.rect = pygame.Rect(x, y, 40, 30)
        self.x = float(x)
        self.color = (255, 0, 0)
    
    def draw(self):
        """Draw the alien"""
        pygame.draw.rect(self.screen, self.color, self.rect)
    
    def update(self, direction, drop_speed):
        """Move alien right or left"""
        self.x += direction
        self.rect.x = self.x
    
    def drop_down(self, distance):
        """Drop alien down"""
        self.rect.y += distance


class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        
        # Screen settings
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Alien Invasion - 5 Levels")
        self.bg_color = (0, 0, 0)
        
        # Game objects
        self.ship = Ship(self.screen)
        self.bullets = []
        self.aliens = []
        
        # Game settings
        self.clock = pygame.time.Clock()
        
        # Game state
        self.game_active = False
        self.game_over = False
        self.game_won = False
        self.current_level = 1
        self.max_level = 5
        
        # Alien fleet settings
        self.fleet_direction = 1  # 1 for right, -1 for left
        self.alien_speed = 1.0
        self.fleet_drop_speed = 30
        
        # Font for text
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
    
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            
            if self.game_active:
                self._update_game_objects()
            
            self._update_screen()
            self.clock.tick(60)
    
    def _check_events(self):
        """Handle keyboard and mouse events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
    
    def _check_keydown_events(self, event):
        """Respond to key presses"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_SPACE:
            if self.game_active:
                self._fire_bullet()
            elif not self.game_active and not self.game_over and not self.game_won:
                # Start game
                self.game_active = True
                self._create_fleet()
            elif self.game_over or self.game_won:
                # Restart game
                self._reset_game()
        elif event.key == pygame.K_q:
            sys.exit()
    
    def _check_keyup_events(self, event):
        """Respond to key releases"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
    
    def _fire_bullet(self):
        """Create new bullet and add to bullets group"""
        if len(self.bullets) < 3:  # Limit bullets on screen
            new_bullet = Bullet(self.screen, self.ship)
            self.bullets.append(new_bullet)
    
    def _create_fleet(self):
        """Create the fleet of aliens based on current level"""
        self.aliens = []
        
        # Level determines number of rows and speed
        rows = min(2 + self.current_level, 6)  # 3 rows level 1, up to 6 rows
        self.alien_speed = 0.5 + (self.current_level * 0.5)  # Gets faster each level
        
        # Create grid of aliens
        for row in range(rows):
            for col in range(10):
                x = 75 + col * 60
                y = 50 + row * 50
                alien = Alien(self.screen, x, y)
                self.aliens.append(alien)
    
    def _check_fleet_edges(self):
        """Check if fleet has reached edge and respond"""
        for alien in self.aliens:
            if alien.rect.right >= self.screen.get_rect().right or alien.rect.left <= 0:
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Drop fleet and change direction"""
        for alien in self.aliens:
            alien.drop_down(self.fleet_drop_speed)
        self.fleet_direction *= -1
    
    def _update_aliens(self):
        """Update positions of all aliens"""
        self._check_fleet_edges()
        for alien in self.aliens:
            alien.update(self.fleet_direction * self.alien_speed, self.fleet_drop_speed)
    
    def _check_bullet_alien_collisions(self):
        """Check for bullets hitting aliens"""
        for bullet in self.bullets.copy():
            for alien in self.aliens.copy():
                if bullet.rect.colliderect(alien.rect):
                    self.bullets.remove(bullet)
                    self.aliens.remove(alien)
                    break
        
        # Check if all aliens destroyed
        if not self.aliens:
            self.bullets.clear()
            self.current_level += 1
            
            if self.current_level > self.max_level:
                self.game_won = True
                self.game_active = False
            else:
                # Next level
                self._create_fleet()
    
    def _check_aliens_bottom(self):
        """Check if aliens have reached bottom or hit ship"""
        screen_rect = self.screen.get_rect()
        
        for alien in self.aliens:
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break
            if alien.rect.colliderect(self.ship.rect):
                self._ship_hit()
                break
    
    def _ship_hit(self):
        """Respond to ship being hit by alien"""
        self.game_active = False
        self.game_over = True
    
    def _reset_game(self):
        """Reset game to initial state"""
        self.game_active = False
        self.game_over = False
        self.game_won = False
        self.current_level = 1
        self.alien_speed = 1.0
        self.bullets.clear()
        self.aliens.clear()
        self.ship.reset_position()
    
    def _update_game_objects(self):
        """Update positions of all game objects"""
        self.ship.update()
        
        # Update bullets
        for bullet in self.bullets.copy():
            bullet.update()
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        # Update aliens
        self._update_aliens()
        
        # Check collisions
        self._check_bullet_alien_collisions()
        self._check_aliens_bottom()
    
    def _draw_text(self, text, color, y_position, size='large'):
        """Draw text on screen"""
        font = self.font if size == 'large' else self.small_font
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.screen.get_rect().centerx
        text_rect.centery = y_position
        self.screen.blit(text_surface, text_rect)
    
    def _update_screen(self):
        """Update images on screen and flip to new screen"""
        self.screen.fill(self.bg_color)
        
        if self.game_active:
            # Draw game objects
            self.ship.draw()
            for bullet in self.bullets:
                bullet.draw()
            for alien in self.aliens:
                alien.draw()
            
            # Draw level indicator
            level_text = f"Level {self.current_level}"
            self._draw_text(level_text, (255, 255, 255), 30, 'small')
        
        elif self.game_won:
            # Victory screen
            self._draw_text("YOU WIN!", (0, 255, 0), 300)
            self._draw_text("Press SPACE to play again", (255, 255, 255), 400, 'small')
            self._draw_text("Press Q to quit", (255, 255, 255), 450, 'small')
        
        elif self.game_over:
            # Game over screen
            self._draw_text("GAME OVER", (255, 0, 0), 300)
            self._draw_text(f"Died on Level {self.current_level}", (255, 255, 255), 350, 'small')
            self._draw_text("Press SPACE to try again", (255, 255, 255), 400, 'small')
            self._draw_text("Press Q to quit", (255, 255, 255), 450, 'small')
        
        else:
            # Start screen
            self._draw_text("ALIEN INVASION", (255, 255, 255), 300)
            self._draw_text("Press SPACE to start", (255, 255, 255), 400, 'small')
            self._draw_text("Arrow keys to move, SPACE to shoot", (255, 255, 255), 450, 'small')
            self._draw_text("Survive 5 levels to win!", (255, 255, 255), 500, 'small')
        
        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()
            
