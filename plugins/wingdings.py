import asyncio
import re

transMap = {' ': ' ', '!': ':black_nib:', '"': ':scissors:', '#': ':haircut:',
            '$': ':eyeglasses:', '%': ':bell:', '&': ':book:', "'": ':flashlight:', 'J': ':smiley:',
            '(': ':phone:', ')': ':telephone_receiver:', '*': ':envelope:', '+': ':love_letter:',
            ',': ':mailbox_closed:', '-': ':mailbox:', '.': ':mailbox_with_mail:', '/': ':mailbox_with_no_mail:',
            '0': ':file_folder:', '1': ':open_file_folder:', '2': ':page_facing_up:', '3': ':page_with_curl:',
            '4': ':clipboard:', '5': ':card_index:', '6': ':hourglass:', '7': ':musical_keyboard:',
            '8': ':video_game:', '9': ':radio_button:', ':': ':computer:', ';': ':minidisc:', '<': ':floppy_disk:',
            '=': ':cd:',
            '>': ':movie_camera:', '?': ':pencil:', '@': ':pencil2:', 'A': ':v:', 'B': ':ok_hand:', 'C': ':thumbsup:',
            'D': ':thumbsdown:', 'E': ':point_left:', 'F': ':point_right:', 'G': ':point_up:',
            'K': ':neutral_face:', 'L': ':frowning:', 'M': ':bomb:', 'N': ':skull:',
            'O': ':checkered_flag:', 'P': ':triangular_flag_on_post:', 'Q': ':airplane:', 'R': ':sunny:',
            'S': ':droplet:', 'T': ':snowflake:', 'U': ':heavy_division_sign:', 'V': ':heavy_plus_sign:',
            'W': ':sparkle:', 'X': ':eight_pointed_black_star:', 'Y': ':six_pointed_star:', 'Z': ':crescent_moon:',
            '[': ':first_quarter_moon:', '\\': ':u6307:', ']': ':anchor:', '^': ':aries:',
            '_': ':taurus:', '`': ':gemini:', 'a': ':cancer:', 'b': ':leo:', 'c': ':virgo:', 'd': ':libra:',
            'e': ':scorpius:', 'f': ':sagittarius:', 'g': ':capricorn:', 'h': ':aquarius:',
            'i': ':pisces:', 'j': ':two_men_holding_hands:', '{': ':white_flower:', '|': ':cherry_blossom:',
            '}': ':end:', '~': ':soon:',
            'k': ':two_women_holding_hands:', 'l': ':black_circle:', 'm': ':white_circle:', 'n': ':black_small_square:',
            'o': ':white_small_square:', 'p': ':black_square_button:', 'q': ':white_medium_square:',
            'r': ':white_square_button:',
            's': ':small_orange_diamond:', 't': ':large_orange_diamond:', 'H': ':point_down:', 'I': ':wave:',
            'u': ':large_blue_diamond:', 'v': ':diamond_shape_with_a_dot_inside:',
            'w': ':small_blue_diamond:', 'x': ':negative_squared_cross_mark:', 'y': ':arrow_up_small:', 'z': ':loop:'}


class WingDings:
    """A plugin for translating to and from WingDings. All credit goes to Dublo.
    !translate <message> : :snowflake::white_square_button::cancer::black_small_square::small_orange_diamond::black_circle::cancer::large_orange_diamond::scorpius::small_orange_diamond:       :cancer:       :white_circle::scorpius::small_orange_diamond::small_orange_diamond::cancer::capricorn::scorpius:       :large_orange_diamond::white_small_square:       :white_small_square::white_square_button:       :sagittarius::white_square_button::white_small_square::white_circle:       :sparkle::pisces::black_small_square::capricorn::thumbsdown::pisces::black_small_square::capricorn::small_orange_diamond:"""
    def __init__(self, client):
        self.client = client

        matchstring = "|".join([re.escape(v) for v in (list(transMap.keys()) + list(transMap.values()))])
        self.matcher = re.compile("(%s)|(?!%s)" % (matchstring, matchstring))  #matching|non matching
        self.map = transMap.update({v: k for k, v in transMap.items()})  #forward and reverse dict

    def translate(self, remainder, messageObj):
        text = remainder.strip()
        msg = ""
        for match in self.matcher.finditer(text):
            msg += transMap[match.group(1)] if match.group(1) else "?"
        asyncio.ensure_future(self.client.send_message(messageObj.channel, msg))

    commandDict = {"!translate": "translate"}

Class = WingDings
