# 🚀 Mostaql Project Monitor

An open-source Python tool that runs in the background to monitor the **Mostaql** freelancing platform. It instantly alerts you via desktop notifications when a new project matching your specialization (e.g., logos, visual identities, or any custom keywords) is posted. This tool aims to keep you ahead of the competition, allowing you to submit your proposals quickly.

![Notification Demo](https://via.placeholder.com/600x200.png?text=Mostaql+Monitor+Notification)

---

## ✨ Key Features
- **Instant Alerts:** Receive native desktop notifications the moment a new project is published.
- **Audio Alerts:** Plays a distinct sound to notify you even when you're away from the screen.
- **Smart Filtering:** Supports smart Arabic keyword matching (normalizes text to ignore diacritics, hamzas, etc.).
- **Easy Control:** Comes with a custom command-line tool `mostaql` for full control (start, stop, status, logs).
- **Auto-Start:** Automatically configures itself to run in the background upon system startup.
- **Duplicate Prevention:** Remembers previously notified projects to avoid spamming you with the same project.

---

## 🛠️ Prerequisites
This tool is primarily designed for **Linux** environments (such as Ubuntu, Linux Mint, and Debian). It requires:
- **Python 3**
- `python3-venv` (for creating an isolated virtual environment)
- Basic system utilities: `notify-send` for notifications, and `paplay` or `canberra-gtk-play` for audio.

---

## 📥 Installation & Setup
The installation process has been simplified to a single command. Just clone the repository and run the setup script.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/USERNAME/Mostaql-Monitor.git
   cd Mostaql-Monitor
   ```

2. **Make the script executable and run it:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

The setup script will automatically:
- Create a Python virtual environment (`venv`) to isolate dependencies.
- Install the required packages (`requests`, `beautifulsoup4`) from `requirements.txt`.
- Add the program to your system's Autostart applications so it runs on boot.
- Configure the `mostaql` CLI command so you can manage the tool from anywhere in your terminal.
- Send a test notification and sound alert to verify that everything works correctly.

---

## 🎮 Usage (CLI Commands)

After a successful installation, you can use the `mostaql` command from any terminal window:

| Command | Description |
|---------|-------------|
| `mostaql start` | **Starts** the monitoring tool in the background (if stopped). |
| `mostaql stop` | **Stops** the tool completely. |
| `mostaql status`| Checks if the tool is currently running or stopped. |
| `mostaql logs` | Views real-time monitoring logs. *(Press **Ctrl + C** to exit logs)* |

---

## ⚙️ Configuration (Keywords & Settings)

You can easily customize the keywords you are targeting by editing the `config.json` file.
The file has the following structure:

```json
{
  "check_interval_seconds": 120,
  "keywords": [
    "شعار",
    "شعارات",
    "هوية",
    "logo",
    "branding"
  ],
  "enable_sound": true,
  "sound_file": "/usr/share/sounds/freedesktop/stereo/complete.oga"
}
```
- **check_interval_seconds:** Time between checks in seconds. It's recommended to leave it at `120` (2 minutes) to prevent getting blocked by the website.
- **keywords:** The list of keywords to trigger notifications. Add or remove keywords based on your niche.
- **enable_sound:** Set to `false` if you want to mute the sound and only receive visual desktop notifications.

> **Note:** You do not need to restart the tool after modifying the configuration file. It will automatically read the updated settings during the next check cycle.

---

## 🤝 Contributing
This project is open-source! If you're a developer and want to improve the code, add new features (like Windows support or Telegram notifications), your Pull Requests are highly welcome.

## 📄 License
This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute it as you see fit.
