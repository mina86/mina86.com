use std::io::Write;

const WIDTH: usize = 1080;
const BAR_HEIGHT: usize = 100;
const HEIGHT: usize = 3 * BAR_HEIGHT;
const ROW_STRIDE: usize = WIDTH * 3;

type UninitImage = [std::mem::MaybeUninit<u8>; HEIGHT * ROW_STRIDE];
type ImageBuffer = [u8; HEIGHT * ROW_STRIDE];


fn draw_bar(
    img: &mut UninitImage,
    n: usize,
    make_rgb: &dyn Fn(f32, f32) -> [u8; 3],
) {
    let y = n * BAR_HEIGHT;
    let bar = &mut img[y * ROW_STRIDE..(y + BAR_HEIGHT) * ROW_STRIDE];
    for (y, row) in bar.chunks_exact_mut(ROW_STRIDE).enumerate() {
        let y = y as f32 / (BAR_HEIGHT - 1) as f32;
        for (pos, px) in row.chunks_exact_mut(3).enumerate() {
            let [mut r, mut g, mut b] = make_rgb(y, pos as f32 / WIDTH as f32);

            if r > g && g == b {
                r = 255;
                g = 0;
                b = 0;
            } else if g > r && r == b {
                r = 0;
                g = 255;
                b = 0;
            } else if b > r && r == g {
                r = 0;
                g = 0;
                b = 255;
            }

            px[0] = std::mem::MaybeUninit::new(r);
            px[1] = std::mem::MaybeUninit::new(g);
            px[2] = std::mem::MaybeUninit::new(b);
        }
    }
}


fn draw_lch_bar(
    img: &mut UninitImage,
    n: usize,
    lch_from_rgb: &dyn Fn([u8; 3]) -> [f32; 3],
    rgb_from_lch: &dyn Fn(f32, f32, f32) -> [u8; 3],
) {
    let blue_lstar = lch_from_rgb([0, 0, 255])[0];
    let green_chroma = lch_from_rgb([0, 255, 0])[1];
    let red_hue = lch_from_rgb([64, 0, 0])[2];
    eprintln!(
        "LCh(ab): L*: {:.2}…{:.2}; C: {:.2}…{:.2}; h: {:.2}°…",
        blue_lstar,
        80.0,
        green_chroma * 0.65 * 0.5,
        green_chroma * 0.65,
        red_hue * 360.0 / std::f32::consts::TAU
    );
    draw_bar(img, n, &|y, turn| {
        let d = 1.0 - (y - 0.5).abs();
        let l = blue_lstar + (80.0 - blue_lstar) * y;
        let c = green_chroma * (d * 0.65);
        let h = red_hue + turn * std::f32::consts::TAU;
        rgb_from_lch(l, c, h)
    });
}


fn generate_bars() -> ImageBuffer {
    // SAFETY: MaybeUninit don’t need to be initialised and we’re just going to
    // be writing into them.
    let mut img: UninitImage =
        unsafe { std::mem::MaybeUninit::uninit().assume_init() };

    let red = hsl::HSL::from_rgb(&[64, 0, 0]);
    eprintln!("hsl: h: {:.2}°…; s: 0.5; l: 0.2…0.8", red.h);
    draw_bar(&mut img, 0, &|y, turn| {
        let hsl = hsl::HSL {
            h: turn as f64 * 360.0 + red.h,
            s: 0.5,
            l: (0.2 + y * 0.6) as f64,
        };
        let (r, g, b) = hsl.to_rgb();
        [r, g, b]
    });

    draw_lch_bar(
        &mut img,
        1,
        &|rgb| {
            let lch = lab::LCh::from_rgb(&rgb);
            [lch.l, lch.c, lch.h]
        },
        &|l, c, h| lab::LCh { l, c, h }.to_rgb(),
    );

    draw_lch_bar(
        &mut img,
        2,
        &|rgb| {
            let lch = luv::LCh::from_rgb(&rgb);
            [lch.l, lch.c, lch.h]
        },
        &|l, c, h| luv::LCh { l, c, h }.to_rgb(),
    );

    // SAFETY: All elements have been initialised
    unsafe { std::mem::transmute::<_, ImageBuffer>(img) }
}


fn save_image(path: &str, img: &[u8]) {
    let enc = webp::Encoder::from_rgb(img, WIDTH as u32, HEIGHT as u32)
        .encode_lossless();
    std::fs::File::create(path)
        .and_then(|mut fd| fd.write_all(&enc))
        .err()
        .map(|e| eprintln!("{}: {}", path, e));
}


fn main() {
    let img = generate_bars();
    save_image("out.webp", &img[..]);
}
