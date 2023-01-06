import pygame


class Text:
    def __init__(self, font_name, font_size, text, color, pos):
        self.font = pygame.font.Font(font_name, font_size)
        self.color = color
        self.rendered = self.font.render(text, True, self.color)
        self.rect = self.rendered.get_rect()
        self.rect.left, self.rect.top = pos

    def set_text(self, text):
        self.rendered = self.font.render(text, True, self.color)
        self.rect = self.rendered.get_rect()

    def get_wh(self):
        return self.rect.width, self.rect.height

    def move(self, pos):
        self.rect.left, self.rect.top = pos

    def draw(self, screen):
        screen.blit(self.rendered, self.rect)


class Button:
    def __init__(self, text: Text, color, rect=None, image=None, image_pos=None):
        self.text = text
        self.color = color
        if rect is None:
            self.is_image = True
            self.image = image
            self.pos = image_pos
        else:
            self.is_image = False
            self.rect = rect
        self.text.move(
            (self.get_pos()[0] + self.get_wh()[0] // 2 - self.text.get_wh()[0] // 2,
             self.get_pos()[1] + self.get_wh()[1] // 2 - self.text.get_wh()[1] // 2)
        )

    def get_wh(self):
        if self.is_image:
            return self.image.get_rect().width, self.image.get_rect().height
        else:
            return self.rect.width, self.rect.height

    def get_pos(self):
        if self.is_image:
            return self.image.get_rect().left, self.image.get_rect().top
        else:
            return self.rect.left, self.rect.top

    def move(self, pos):
        if self.image:
            self.image.get_rect().left, self.image.get_rect().top = pos
        else:
            self.rect.left, self.rect.top = pos

    def get_collide_rect(self):
        if self.is_image:
            return self.image.get_rect()
        return self.rect

    def draw(self, screen):
        if self.is_image:
            screen.blit(self.image, self.pos)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        self.text.draw(screen)
