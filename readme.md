# Langton's Ants

## Usage

Run:

    python3 ants.py

### Argument examples

You can use some arguments when running the program. Multiple arguments can beused at the same time and their order doesn't matter.

#### Behavior:

    python3 ants.py beh_s=rlbn

where `rlbn` can be any sequence shorter than 15 characters long with characters r, l, b and n. Characters correspond to rotations that the ants make:

    r = right = 90°
    l = left = -90°
    b = back = 180°
    n = neutral = 0°

#### Number of ants:

    python3 ants.py ant_n=n

where `n` can be any integer value greater than 0. (`n > 1000` not recommended)

#### Scale:

    python3 ants.py scale=k

where `s` can be any integer value greater than 0. Default 1. (`s = 2^k` recommended, otherwise some graphical problems may appear)

#### Fullscreen:

    python3 ants.py f=1

1 = True, 0 = False. Default 0.

### During run

|Key |Action|
|:---|:-----|
|w/a/s/d|Move around in steps|
|q/e|Increase/decrease step size|
|t/g|Increase/decrease simulation speed|
|p|Pause/continue|
|c|Save image of current screen|
|r|Restart simulation|
|Esc|Quit|



### Performance

creating performance profile

    python3 -m cProfile -o [output file name] ants.py

viewing performance profile (requires cprofilev)

    cprofilev -f [output file name] &
    firefox http://localhost:4000
