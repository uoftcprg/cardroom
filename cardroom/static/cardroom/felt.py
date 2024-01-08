from __future__ import annotations

from dataclasses import dataclass, field
from math import pi, sqrt, tan
from typing import Any

from pyodide.ffi import create_proxy, JsProxy
from js import cancelAnimationFrame, document, requestAnimationFrame


SUIT_CHARACTERS = {
    'c': '♣',
    'd': '♦',
    'h': '♥',
    's': '♠',
    '?': ' ',
}
SUIT_COLOR_KEYS = {
    'c': 'club_color',
    'd': 'diamond_color',
    'h': 'heart_color',
    's': 'spade_color',
    '?': 'unknown_color',
}
DEFAULT_TEXT_HEIGHT = 1


def resolve_ellipse(width, height, angle):
    if isinstance(angle, int):
        angle = float(angle)

    a = width / 2
    b = height / 2

    try:
        x = a * b / sqrt(b ** 2 + a ** 2 * tan(angle) ** 2)
    except ZeroDivisionError:
        x = 0

    try:
        y = a * b / sqrt(a ** 2 + b ** 2 / tan(angle) ** 2)
    except ZeroDivisionError:
        y = 0

    if pi / 2 <= angle < 3 * pi / 2:
        x *= -1

    if pi <= angle < 2 * pi:
        y *= -1

    return x, -y


@dataclass
class Felt:
    settings: dict[str, Any]
    element_id: str
    animation_id: int | None = field(default=None, init=False)
    proxy: JsProxy | None = field(default=None, init=False)

    @property
    def element(self):
        return document.getElementById(self.element_id)

    @property
    def width(self):
        return self.element.width

    @width.setter
    def width(self, value):
        self.element.width = value

    @property
    def height(self):
        return self.element.height

    @height.setter
    def height(self, value):
        self.element.height = value

    def setup(self):
        return self.element.getContext('2d')

    def draw(self, ctx, data_getter):
        data = data_getter()
        count = len(data['names'])
        indices = range(count)
        angles = []
        unit = min(self.width, self.height)

        for i in indices:
            angle = (-2 * pi * i / count) % (2 * pi)

            angles.append(angle)

        ctx.save()

        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        ctx.direction = 'ltr'
        ctx.lineWidth = 0

        ctx.fillStyle = self.settings['background_color']

        ctx.fillRect(0, 0, self.width, self.height)

        ctx.translate(self.width / 2, self.height / 2)
        ctx.scale(unit, unit)

        ctx.fillStyle = self.settings['outer_table_color']

        ctx.beginPath()
        ctx.ellipse(
            0,
            0,
            self.settings['outer_table_width'] / 2,
            self.settings['outer_table_height'] / 2,
            0,
            0,
            2 * pi,
        )
        ctx.fill()

        ctx.fillStyle = self.settings['inner_table_color']

        ctx.beginPath()
        ctx.ellipse(
            0,
            0,
            self.settings['inner_table_width'] / 2,
            self.settings['inner_table_height'] / 2,
            0,
            0,
            2 * pi,
        )
        ctx.fill()

        if data['button'] is not None:
            x, y = resolve_ellipse(
                self.settings['button_ring_width'],
                self.settings['button_ring_height'],
                angles[data['button']] + self.settings['button_angle'],
            )

            ctx.fillStyle = self.settings['button_color']

            ctx.beginPath()
            ctx.arc(x, y, self.settings['button_diameter'] / 2, 0, 2 * pi)
            ctx.fill()

            ctx.fillStyle = self.settings['button_text_color']
            ctx.font = self.settings['button_text_font'].format(
                self.settings['button_text_height'],
            )

            ctx.fillText(
                self.settings['button_text'],
                x,
                y,
            )

        for i in indices:
            if data['bets'][i]:
                x, y = resolve_ellipse(
                    self.settings['bet_ring_width'],
                    self.settings['bet_ring_height'],
                    angles[i] + self.settings['bet_angle'],
                )
                height = self.settings['bet_box_height']
                text = self.settings['bet_text'].format(data['bets'][i])
                ctx.font = self.settings['bet_text_font'].format(
                    self.settings['bet_text_height'],
                )
                width = ctx.measureText(text).width + height

                ctx.fillStyle = self.settings['bet_box_color']

                ctx.beginPath()
                ctx.roundRect(
                    x - width / 2,
                    y - height / 2,
                    width,
                    height,
                    height / 2,
                )
                ctx.fill()

                ctx.fillStyle = self.settings['bet_text_color']

                ctx.fillText(text, x, y)

        ctx.fillStyle = self.settings['board_color']

        ctx.beginPath()
        ctx.roundRect(
            -self.settings['board_width'] / 2,
            self.settings['board_y'] - self.settings['board_height'] / 2,
            self.settings['board_width'],
            self.settings['board_height'],
            self.settings['board_radius'],
        )
        ctx.fill()

        ctx.fillStyle = self.settings['board_text_color']
        ctx.font = self.settings['board_text_font'].format(
            self.settings['board_text_height'],
        )
        text = self.settings['board_text'].format(
            ', '.join(map(str, data['pots'])),
        )

        ctx.fillText(text, 0, self.settings['board_y'])

        if data['board']:
            width = (
                (
                    self.settings['board_width']
                    - (
                        (2 + data['board_count'])
                        * self.settings['board_card_margin']
                    )
                )
                / data['board_count']
            )
            x = (
                -self.settings['board_width'] / 2
                + self.settings['board_card_margin']
                + width / 2
            )
            height = width
            y = (
                self.settings['board_y']
                - self.settings['board_height'] / 2
                - height / 2
            )
            ctx.font = self.settings['board_card_text_font'].format(
                (1 - 2 * self.settings['board_card_padding_percentage'])
                * height,
            )

            for card in data['board']:
                ctx.fillStyle = self.settings['board_card_color']

                ctx.beginPath()
                ctx.roundRect(
                    x - width / 2,
                    y - height / 2,
                    width,
                    height,
                    [
                        self.settings['board_card_radius'],
                        self.settings['board_card_radius'],
                        0,
                        0,
                    ],
                )
                ctx.fill()

                ctx.fillStyle = self.settings[SUIT_COLOR_KEYS[card['suit']]]

                text = card['rank'] + SUIT_CHARACTERS[card['suit']]

                ctx.fillText(text, x, y)

                x += width + self.settings['board_card_margin']

        for i, name in enumerate(data['names']):
            if name is None:
                continue

            x, y = resolve_ellipse(
                self.settings['seat_ring_width'],
                self.settings['seat_ring_height'],
                angles[i],
            )

            ctx.fillStyle = self.settings['name_color']

            ctx.beginPath()
            ctx.roundRect(
                x - self.settings['name_width'] / 2,
                y + self.settings['name_y'] - self.settings['name_height'] / 2,
                self.settings['name_width'],
                self.settings['name_height'],
                [
                    self.settings['name_radius'],
                    self.settings['name_radius'],
                    0,
                    0,
                ],
            )
            ctx.fill()

            ctx.fillStyle = self.settings['name_text_color']
            ctx.font = self.settings['name_text_font'].format(
                self.settings['name_text_height'],
            )
            text = self.settings['name_text'].format(name)

            ctx.fillText(text, x, y + self.settings['name_y'])

            ctx.fillStyle = self.settings['stack_color']

            ctx.fillRect(
                x - self.settings['stack_width'] / 2,
                (
                    y
                    + self.settings['stack_y']
                    - self.settings['stack_height'] / 2
                ),
                self.settings['stack_width'],
                self.settings['stack_height'],
            )

            ctx.fillStyle = self.settings['stack_text_color']
            ctx.font = self.settings['stack_text_font'].format(
                self.settings['stack_text_height'],
            )
            text = self.settings['stack_text'].format(data['stacks'][i])

            ctx.fillText(text, x, y + self.settings['stack_y'])

            ctx.fillStyle = self.settings['acted_color']

            ctx.beginPath()
            ctx.roundRect(
                x - self.settings['acted_width'] / 2,
                (
                    y
                    + self.settings['acted_y']
                    - self.settings['acted_height'] / 2
                ),
                self.settings['acted_width'],
                self.settings['acted_height'],
                [
                    0,
                    0,
                    self.settings['acted_radius'],
                    self.settings['acted_radius'],
                ],
            )
            ctx.fill()

            ctx.fillStyle = self.settings['acted_text_color']
            ctx.font = self.settings['acted_text_font'].format(
                self.settings['acted_text_height'],
            )

            if data['acted'] is not None and data['acted'][0] == i:
                text = self.settings['acted_text'].format(data['acted'][1])
            else:
                text = ''

            ctx.fillText(text, x, y + self.settings['acted_y'])

            if data['hole'][i]:
                card_count = max(
                    data['hole_statuses'].count(True),
                    data['hole_statuses'].count(False),
                )
                width = (
                    (
                        self.settings['name_width']
                        - (2 + card_count) * self.settings['hole_card_margin']
                    )
                    / card_count
                )
                x_init = (
                    x
                    + (
                        -self.settings['name_width'] / 2
                        + self.settings['hole_card_margin']
                        + width / 2
                    )
                )
                height = width
                y += (
                    self.settings['name_y']
                    - self.settings['name_height'] / 2
                    - height / 2
                )
                ctx.font = self.settings['hole_card_text_font'].format(
                    (1 - 2 * self.settings['hole_card_padding_percentage'])
                    * height,
                )

                for status in [False, True]:
                    x = x_init
                    radii = [
                        self.settings['hole_card_radius'],
                        self.settings['hole_card_radius'],
                        self.settings['hole_card_radius'] if status else 0,
                        self.settings['hole_card_radius'] if status else 0,
                    ]

                    for j, card in enumerate(data['hole'][i]):
                        if data['hole_statuses'][j] is not status:
                            continue

                        ctx.fillStyle = self.settings['hole_card_color']

                        ctx.beginPath()
                        ctx.roundRect(
                            x - width / 2,
                            y - height / 2,
                            width,
                            height,
                            radii,
                        )
                        ctx.fill()

                        ctx.fillStyle = (
                            self.settings[SUIT_COLOR_KEYS[card['suit']]]
                        )
                        text = card['rank'] + SUIT_CHARACTERS[card['suit']]

                        ctx.fillText(text, x, y)

                        x += width + self.settings['hole_card_margin']

                    y -= height + self.settings['hole_card_margin']

        ctx.restore()

    def animate(self, data_getter):

        def callback(ms=0):
            self.animation_id = requestAnimationFrame(self.proxy)

            self.draw(ctx, data_getter)

        self.proxy = create_proxy(callback)
        ctx = self.setup()

        callback()

    def stop(self):
        if self.animation_id is not None:
            cancelAnimationFrame(self.animation_id)

            self.animation_id = None

        if self.proxy is not None:
            self.proxy.destroy()

            self.proxy = None
