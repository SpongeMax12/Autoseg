<h1 align="center">
  Advanced Auto Segmenter (Autoseg)
</h1>

<p align="center">
  <b>A GUI tool for intelligent audio/video transcription and segmentation using Whisper.</b>
</p>

<p align="center">
    <a href="https://github.com/[YOUR_GITHUB_USERNAME]/[YOUR_REPOSITORY_NAME]/releases">
        <img src="https://img.shields.io/github/v/release/[YOUR_GITHUB_USERNAME]/[YOUR_REPOSITORY_NAME]?style=for-the-badge" alt="Release">
    </a>
    <a href="https://github.com/[YOUR_GITHUB_USERNAME]/[YOUR_REPOSITORY_NAME]/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/[YOUR_GITHUB_USERNAME]/[YOUR_REPOSITORY_NAME]?style=for-the-badge&color=blue" alt="License">
    </a>
    <a href="https://github.com/[YOUR_GITHUB_USERNAME]/[YOUR_REPOSITORY_NAME]/issues">
        <img src="https://img.shields.io/github/issues/[YOUR_GITHUB_USERNAME]/[YOUR_REPOSITORY_NAME]?style=for-the-badge&color=brightgreen" alt="Downloads">
    </a>
</p>

## 👋 Introduction

**Advanced Auto Segmenter** is a user-friendly desktop application designed to automatically transcribe audio and video files. It uses the power of OpenAI's Whisper model to provide highly accurate transcriptions.

Its standout feature is **smart segmentation**: instead of just providing a wall of text, the tool intelligently splits the transcription into meaningful chunks based on sentence structure and natural pauses. This makes it perfect for creating subtitles, summarizing content, or navigating long recordings.

![Application Screenshot](https://i.imgur.com/your-screenshot-url.png)
*(Note: A real screenshot of the application's GUI should be placed here.)*

## ✨ Key Features

*   **🖥️ Intuitive GUI:** A clean and simple graphical interface built with Tkinter, making it accessible for all users.
*   **🤖 High-Quality Transcription:** Powered by the `faster-whisper` library for efficient and accurate speech-to-text.
*   **🧠 Smart Segmentation:** Automatically breaks down transcriptions into logical segments, complete with timestamps.
*   **🎵 Wide Format Support:** Process a variety of audio (`.mp3`, `.wav`, `.m4a`) and video (`.mp4`, `.mov`, `.avi`) files.
*   **⚡ Hardware Acceleration:** Supports both CPU and NVIDIA GPU (CUDA) processing for significantly faster results.
*   **📁 Export Options:** Save your transcriptions as plain text (`.txt`) or subtitle files (`.srt`).
*   **▶️ Interactive Results:** Play back the audio for each specific segment directly from the results window to verify the transcription.
*   **⚙️ Model Selection:** Choose from various Whisper model sizes (from `tiny` to `large-v3`) to balance speed and accuracy.

## 💻 Tech Stack

*   **Core:** Python 3
*   **GUI:** Tkinter (`ttkthemes` for styling)
*   **AI Model:** `faster-whisper` (an optimized implementation of OpenAI's Whisper)
*   **ML Framework:** PyTorch
*   **Audio Processing:** `ffmpeg-python` and `pydub`

## 🛠️ Getting Started

Follow these instructions to get the application running on your local machine.

### Prerequisites

You must have the following software installed:

1.  **Python:** Version 3.8 or higher.
    *   **Download:** [python.org](https://www.python.org/downloads/)
    *   **Important:** During installation on Windows, make sure to check the box that says **"Add Python to PATH"**.

2.  **FFmpeg:** A required tool for audio/video conversion.
    *   **Windows:**
        1.  Download a release build from [BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds/releases).
        2.  Unzip the file (e.g., into `C:\ffmpeg`).
        3.  Add the `bin` folder (e.g., `C:\ffmpeg\bin`) to your system's `PATH` environment variable.
    *   **macOS:** `brew install ffmpeg`
    *   **Linux (Ubuntu/Debian):** `sudo apt update && sudo apt install ffmpeg`

### Installation & Usage

The application includes helper scripts to automatically install Python dependencies like `torch` and `faster-whisper`.

#### 🚀 For Windows Users

We offer two convenient ways to run the application:

**Option 1: Global Command (Recommended)**
This method creates a global `autoseg` command that you can run from anywhere.

1.  Navigate to the project directory and double-click `setup_autoseg_command.bat`.
2.  Approve the prompts. This will add the necessary script to your system's PATH.
3.  **Re-open your terminal** (CMD or PowerShell) and simply run:
    ```bash
    autoseg
    ```

**Option 2: Direct Launch**
If you prefer not to modify your system PATH, you can launch the app directly.

1.  Navigate to the project directory.
2.  Double-click `启动AutoSeg.bat`.
3.  The script will handle dependency checks and launch the application.

#### 🐧 For macOS & Linux Users

1.  Open your terminal and navigate to the project directory.
2.  Make the startup script executable:
    ```bash
    chmod +x start_autoseg.sh
    ```
3.  Run the script:
    ```bash
    ./start_autoseg.sh
    ```
    The script will handle dependency checks and launch the application.

## 🐛 Troubleshooting

*   **`'python' is not recognized...` (Windows)**
    *   **Cause:** Python is not in your system's PATH.
    *   **Solution:** Re-install Python and ensure you check the "Add Python to PATH" box during setup.

*   **`FFmpeg not found`**
    *   **Cause:** The application cannot find the `ffmpeg` executable.
    *   **Solution:** Ensure FFmpeg is installed and that its `bin` directory is correctly added to your system's PATH. Restart your terminal or PC after adding it.

*   **Dependency Installation Fails**
    *   **Cause:** Often due to network issues or an outdated `pip`.
    *   **Solution:** Open a terminal and try upgrading pip and installing manually:
        ```bash
        python -m pip install --upgrade pip
        pip install faster-whisper torch ffmpeg-python pydub
        ```

*   **CUDA Errors / Out of Memory**
    *   **Cause:** Your GPU may not have enough VRAM for the selected model.
    *   **Solution:** In the application's GUI, select a smaller model (e.g., `base` or `small`) or choose "cpu" as the run device.

*   **Logs:** For detailed error information, check the log file located at `logs/autoseg.log`.

## 🤝 Contributing

Contributions are welcome! If you have suggestions or want to fix a bug, please feel free to open an issue or submit a pull request.

1.  **Fork the repository.**
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes and commit them.
4.  Push to your branch and open a Pull Request.

## 📜 License

This project is licensed under the **[MIT License]**. See the `LICENSE` file for more details.
*(Note: License type is a placeholder and should be confirmed.)*
