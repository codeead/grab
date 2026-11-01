"""영수증 조각 만들기: python3 make_receipt.py <NotoSansKR[wght].ttf 경로>

asset/사전이벤트용 바코드만.png 를 곡 목록 위·아래로 잘라 receipt/top.png, bottom.png 로,
곡 줄은 receipt/n1~5.png(번호) + receipt/s1~20.png(곡명·길이) 로 미리 그려둔다.
폰트 파일을 웹에 올리지 않으려고 글자를 이미지로 굽는 것. 곡이 바뀌면 SONGS 고치고 다시 실행.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

SRC = "asset/사전이벤트용 바코드만.png"
ROCKWELL = "/System/Library/Fonts/Supplemental/Rockwell.ttc"
TOP, ROW, ROWS = 532, 52, 5     # 원본에서 곡 목록이 532~792px, 줄 높이 52
BASE = 48                       # 줄 안에서 글자 기준선 (한글은 아래로 길어서 2px 위)
X_NO, X_TITLE, X_TIME = 98, 243, 923
SQUEEZE = 0.92                  # 캔바 Rockwell이 맥 Rockwell보다 살짝 좁음

# index.html 의 SONGS 와 같은 순서
SONGS = [
    ("NOVEMBER SONG", "3:15"), ("이유", "5:08"), ("무희", "3:54"), ("사랑을 전하고 싶다든가", "4:06"),
    ("순혈주의자", "4:09"), ("INFERNO", "3:32"), ("CLIFFS OF DOVER", "4:12"), ("퇴사할게여", "3:32"),
    ("SUPERNOVA", "3:30"), ("BLACK MAMBA", "3:34"), ("들려주고 싶었던", "4:52"), ("SUB CHARACTER", "3:38"),
    ("MONSTER", "3:35"), ("STARGAZING", "4:08"), ("HIGH TIDE", "4:08"), ("너와 나", "3:38"),
    ("내 방안은 푸른 바다", "7:57"), ("DETOX", "4:14"), ("SCHOOL FICTION", "6:03"), ("질주", "4:38"),
]

rock = ImageFont.truetype(ROCKWELL, 42, index=0)
kr = ImageFont.truetype(sys.argv[1], 42)
kr.set_variation_by_name(b"Regular")
W = Image.open(SRC).width


def word(text, font):
    """글자 한 덩어리를 투명 이미지로. Rockwell은 가로로 살짝 눌러서 원본 폭에 맞춤"""
    l, t, r, b = font.getbbox(text, anchor="ls")
    im = Image.new("RGBA", (r - l, ROW), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-l, BASE if font is rock else BASE - 2), text, font=font, fill="black", anchor="ls")
    if font is rock:
        im = im.resize((round(im.width * SQUEEZE), ROW), Image.LANCZOS)
    return im


def row(parts):
    im = Image.new("RGBA", (W, ROW), (0, 0, 0, 0))
    for text, x, right in parts:
        w = word(text, kr if any("가" <= c <= "힣" for c in text) else rock)
        im.alpha_composite(w, (x - w.width if right else x, 0))
    return im


src = Image.open(SRC).convert("RGB")
src.crop((0, 0, W, TOP)).save("receipt/top.png", optimize=True)
src.crop((0, TOP + ROW * ROWS, W, src.height)).save("receipt/bottom.png", optimize=True)
for i in range(ROWS):
    row([(f"{i + 1:02}", X_NO, False)]).save(f"receipt/n{i + 1}.png", optimize=True)
for i, (title, time) in enumerate(SONGS):
    row([(title, X_TITLE, False), (time, X_TIME, True)]).save(f"receipt/s{i + 1}.png", optimize=True)

# 확인용: 원본과 같은 5곡(1,3,9,14,16번)으로 다시 조립
check = Image.new("RGB", src.size, "white")
check.paste(src.crop((0, 0, W, TOP)), (0, 0))
for i, n in enumerate([1, 3, 9, 14, 16]):
    for f in (f"receipt/n{i + 1}.png", f"receipt/s{n}.png"):
        check.paste(p := Image.open(f), (0, TOP + i * ROW), p)
check.paste(src.crop((0, TOP + ROW * ROWS, W, src.height)), (0, TOP + ROW * ROWS))
check.save(sys.argv[2] if len(sys.argv) > 2 else "/dev/null", "PNG")
