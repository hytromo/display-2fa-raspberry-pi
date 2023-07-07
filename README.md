# Scary Quack

https://user-images.githubusercontent.com/131824/217944674-1608e5ca-1d01-4002-9913-ff53f961b9c4.mp4

# Disclaimer

1. If you leak your 2FA secrets it's like you don't have 2FA turned on. It's a big security risk. Make sure you understand what having your 2FA secrets available inside your RPi means.
2. This is just a pet project written within a few hours. Do not expect to find optimized code or best practices. Feel free to make PRs to improve it.
3. The code as is works only for 2FA codes that rotate every 30 seconds, at :00 and :30 of every minute.

# Hardware Setup

1. [Waveshare display](https://www.waveshare.com/1.44inch-lcd-hat.htm)
2. [RPi 4b](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) - but it should work with any RPi compatible with the screen

# Software Setup

0. Clone this repo inside your RPi.
1. Install all the required drivers for the display. Run some provided example to make sure that the screen works fine.
2. Install python 3 if it's missing from your system.
3. `pip install -r requirements.txt`.
4. Install system dependencies: `sudo apt install fonts-noto-mono oathtool`
5. Find your 2FA secrets. That's the strings required to generate the original QR codes you scan and the 2FA codes that you are presented with. I used [this gist](https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93) to extract them from Authy, which works at the time of writing this. Alternatively, if you reset your 2FA, most websites give you this secret string along with the QR code.
6. Replace the logos and the code to contain the services you want. You may alter any global consts as you see fit.
7. Export your secrets based on the environment variable names in the code, e.g. `export GOOGLE_2FA_SECRET=abcdef..`
8. Run the script `python main.py` and voila.

# Why

2FA codes in phone can be distracting and it looks cool.
