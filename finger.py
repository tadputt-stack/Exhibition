# Finger / hand scan glitch effect - TouchDesigner
# วิธีใช้: สร้าง Text DAT -> วางโค้ดนี้ -> คลิกขวา Run Script

root = op('/project1') or op('/')
old = root.op('finger_scan')
if old:
    old.destroy()
c = root.create(baseCOMP, 'finger_scan')

def setp(o, **kw):
    for k, v in kw.items():
        try:
            setattr(o.par, k, v)
        except Exception as e:
            print('[skip]', o.name, k, '->', e)

def make(typ, name, x, y, src=None, **kw):
    o = c.create(typ, name)
    o.nodeX, o.nodeY = x, y
    setp(o, **kw)
    if src is not None:
        srcs = src if isinstance(src, (list, tuple)) else [src]
        for i, s in enumerate(srcs):
            o.inputConnectors[i].connect(s)
    return o

# ---------- 1) กล้อง ----------
cam   = make(videodeviceinTOP, 'cam', 0, 0)
flip  = make(flipTOP, 'flip', 200, 0, cam, flipx=1)
mono  = make(monochromeTOP, 'mono', 400, 0, flip)

# ---------- 2) ตรวจจับการเคลื่อนไหว (มือ/นิ้ว) ----------
prev   = make(feedbackTOP, 'prev_frame', 400, -200)
setp(prev, top=mono.name)
diff   = make(compositeTOP, 'motion_diff', 600, 0, [mono, prev], operand='difference')
blur   = make(blurTOP, 'blur', 800, 0, diff, size=6)
boost  = make(levelTOP, 'boost', 1000, 0, blur, brightness1=2.5, contrast=2.0)
thr    = make(thresholdTOP, 'threshold', 1200, 0, boost, threshold=0.25)

# ---------- 3) เส้นหางตกค้าง (trail) ----------
trail_fb  = make(feedbackTOP, 'trail_fb', 1200, -250)
trail_lv  = make(levelTOP, 'trail_decay', 1400, -250, trail_fb, opacity=0.93)
trail_add = make(compositeTOP, 'trail_add', 1600, 0, [thr, trail_lv], operand='add')
setp(trail_fb, top=trail_add.name)

# ---------- 4) ลุคบล็อกพิกเซล ----------
pix = make(resolutionTOP, 'pixelate', 1800, 0, trail_add,
           outputresolution='custom', resolutionw=48, resolutionh=27,
           filtertype='nearest')
up  = make(resolutionTOP, 'upscale', 2000, 0, pix,
           outputresolution='custom', resolutionw=1280, resolutionh=720,
           filtertype='nearest')

# ---------- 5) ใส่สี แดงเข้ม/ชมพู ----------
tint = make(constantTOP, 'tint_color', 2000, -250,
            colorr=0.55, colorg=0.03, colorb=0.12,
            outputresolution='custom', resolutionw=1280, resolutionh=720)
colored = make(compositeTOP, 'colorize', 2200, 0, [up, tint], operand='multiply')

# ---------- 6) สี่เหลี่ยมโปร่งแสงซ้อนทับ ----------
rect1 = make(rectangleTOP, 'rect_pink', 2200, -250,
             outputresolution='custom', resolutionw=1280, resolutionh=720,
             fillcolorr=1.0, fillcolorg=0.85, fillcolorb=0.88, fillalpha=0.55)
rect2 = make(rectangleTOP, 'rect_outline', 2200, -450,
             outputresolution='custom', resolutionw=1280, resolutionh=720,
             fillcolorr=1.0, fillcolorg=1.0, fillcolorb=1.0, fillalpha=0.12)

# ---------- 7) ประกอบทั้งหมด ----------
base = make(levelTOP, 'cam_dim', 2400, 150, flip, opacity=0.9)
mix1 = make(compositeTOP, 'mix_motion', 2600, 0, [base, colored], operand='screen')
mix2 = make(compositeTOP, 'mix_rect1', 2800, 0, [mix1, rect1], operand='over')
mix3 = make(compositeTOP, 'mix_rect2', 3000, 0, [mix2, rect2], operand='over')
out  = make(nullTOP, 'OUT', 3200, 0, mix3)
out.viewer = True
out.display = True

print('สร้างเสร็จแล้ว: ดูผลที่ /project1/finger_scan/OUT')