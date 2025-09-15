import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
import tempfile
import time
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import traceback

# Configure logging
def setup_logging() -> logging.Logger:
    """Set up logging configuration for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging with rotation
    log_file = log_dir / "autoseg.log"

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )

    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler with rotation
        try:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5  # 10MB max, 5 backups
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # Fallback to basic file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

logger = setup_logging()

# --- 依赖项检查 ---
def check_dependencies() -> bool:
    """Check if all required dependencies are available."""
    missing_deps = []

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        missing_deps.append("faster-whisper")

    try:
        import ffmpeg
    except ImportError:
        missing_deps.append("ffmpeg-python")

    try:
        from pydub import AudioSegment
        from pydub.playback import play
    except ImportError:
        missing_deps.append("pydub")

    try:
        import torch
    except ImportError:
        missing_deps.append("torch")

    if missing_deps:
        error_msg = (
            f"缺少必要的依赖库: {', '.join(missing_deps)}\n\n"
            f"请运行以下命令安装:\n"
            f"pip install {' '.join(missing_deps)}"
        )
        logger.error(f"Missing dependencies: {missing_deps}")
        messagebox.showerror("依赖缺失", error_msg)
        return False

    return True

# Check dependencies before proceeding
if not check_dependencies():
    sys.exit(1)

# Import dependencies after checking
from faster_whisper import WhisperModel
import ffmpeg
from pydub import AudioSegment
from pydub.playback import play
import torch

# --- 应用主类 ---
class AutoSegmenterApp:
    """Advanced Auto Segmenter application for audio/video transcription and segmentation."""

    # Supported file formats
    SUPPORTED_FORMATS = {
        'audio': ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg'],
        'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    }

    def __init__(self, root: tk.Tk):
        """Initialize the application.

        Args:
            root: The main tkinter window
        """
        self.root = root
        self.root.title("Advanced Auto Segmenter for Audio/Video")
        self.root.geometry("850x750")
        self.root.minsize(800, 600)

        # Set up proper window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- 成员变量初始化 ---
        self.file_path = tk.StringVar()
        self.max_duration = tk.IntVar(value=60)
        self.language_code = tk.StringVar()

        # Model and Transcription settings
        self.model_size = tk.StringVar(value="base")
        self.device = tk.StringVar()
        self.compute_type = tk.StringVar()
        self.use_vad = tk.BooleanVar(value=True)
        self.beam_size = tk.IntVar(value=5)

        # Threading and processing
        self.processing_thread: Optional[threading.Thread] = None
        self.result_queue: queue.Queue = queue.Queue()
        self.full_audio: Optional[AudioSegment] = None
        self.segments_data: List[Dict[str, Any]] = []
        self.model: Optional[WhisperModel] = None
        self.is_processing = False
        self.temp_files: List[str] = []  # Track temporary files for cleanup

        try:
            # --- 创建 GUI 界面 ---
            self.create_widgets()
            self.root.after(100, self.check_queue)

            # --- 初始化硬件设置 ---
            self.init_hardware_options()

            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            messagebox.showerror("初始化错误", f"应用程序初始化失败: {e}")
            sys.exit(1)

    def on_closing(self) -> None:
        """Handle application closing with proper cleanup."""
        try:
            if self.is_processing and self.processing_thread and self.processing_thread.is_alive():
                if messagebox.askokcancel("退出确认", "正在处理文件，确定要退出吗？"):
                    self.cleanup_resources()
                    self.root.destroy()
            else:
                self.cleanup_resources()
                self.root.destroy()
        except Exception as e:
            logger.error(f"Error during application closing: {e}")
            self.root.destroy()

    def cleanup_resources(self) -> None:
        """Clean up temporary files and resources."""
        try:
            # Clean up temporary files
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.info(f"Cleaned up temporary file: {temp_file}")
            self.temp_files.clear()

            # Clear audio data
            self.full_audio = None
            self.segments_data.clear()

            logger.info("Resources cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def validate_file_path(self, file_path: str) -> bool:
        """Validate if the selected file is supported.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file is valid and supported, False otherwise
        """
        if not file_path:
            return False

        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            messagebox.showerror("文件错误", "选择的文件不存在")
            return False

        # Check if it's a file (not directory)
        if not path.is_file():
            messagebox.showerror("文件错误", "请选择一个文件，而不是文件夹")
            return False

        # Check file extension
        file_ext = path.suffix.lower()
        all_supported = self.SUPPORTED_FORMATS['audio'] + self.SUPPORTED_FORMATS['video']

        if file_ext not in all_supported:
            messagebox.showerror(
                "不支持的文件格式",
                f"不支持的文件格式: {file_ext}\n\n"
                f"支持的格式:\n"
                f"音频: {', '.join(self.SUPPORTED_FORMATS['audio'])}\n"
                f"视频: {', '.join(self.SUPPORTED_FORMATS['video'])}"
            )
            return False

        # Check file size (warn if > 500MB)
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > 500:
            if not messagebox.askyesno(
                "大文件警告",
                f"文件大小为 {file_size_mb:.1f} MB，处理可能需要较长时间。\n是否继续？"
            ):
                return False

        return True

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 1. 模型配置区 ---
        model_frame = ttk.LabelFrame(main_frame, text="第一步：模型配置", padding="10")
        model_frame.pack(fill=tk.X, pady=5)
        self.model_config_widgets = []

        # Model Size
        row1 = ttk.Frame(model_frame)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="模型大小:", width=15).pack(side=tk.LEFT)
        model_combo = ttk.Combobox(row1, textvariable=self.model_size, values=[
            "tiny", "base", "small", "medium", "large-v1", "large-v2", "large-v3"
        ])
        model_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_config_widgets.append(model_combo)

        # Device
        row2 = ttk.Frame(model_frame)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="运行设备:", width=15).pack(side=tk.LEFT)
        self.device_combo = ttk.Combobox(row2, textvariable=self.device)
        self.device_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.device_combo.bind("<<ComboboxSelected>>", self.update_compute_types)
        self.model_config_widgets.append(self.device_combo)

        # Compute Type
        row3 = ttk.Frame(model_frame)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="计算精度:", width=15).pack(side=tk.LEFT)
        self.compute_type_combo = ttk.Combobox(row3, textvariable=self.compute_type)
        self.compute_type_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_config_widgets.append(self.compute_type_combo)
        
        # Load Model Button
        self.load_model_button = ttk.Button(model_frame, text="加载模型", command=self.load_model, style="Accent.TButton")
        self.load_model_button.pack(fill=tk.X, pady=(10, 5), ipady=5)
        self.model_config_widgets.append(self.load_model_button)

        # --- 2. 文件与转录设置 ---
        settings_frame = ttk.LabelFrame(main_frame, text="第二步：文件与转录设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        # File Selection
        file_row = ttk.Frame(settings_frame)
        file_row.pack(fill=tk.X, pady=5)
        ttk.Label(file_row, text="文件路径:", width=15).pack(side=tk.LEFT)
        ttk.Entry(file_row, textvariable=self.file_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(file_row, text="浏览...", command=self.browse_file).pack(side=tk.LEFT, padx=(5, 0))

        # Language
        lang_row = ttk.Frame(settings_frame)
        lang_row.pack(fill=tk.X, pady=5)
        ttk.Label(lang_row, text="转录语言 (可选):", width=15).pack(side=tk.LEFT)
        ttk.Entry(lang_row, textvariable=self.language_code, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(lang_row, text="（留空则自动检测，如 en, zh, ja）").pack(side=tk.LEFT)

        # VAD and Beam Size
        adv_row = ttk.Frame(settings_frame)
        adv_row.pack(fill=tk.X, pady=5)
        self.vad_check = ttk.Checkbutton(adv_row, text="启用 VAD 过滤", variable=self.use_vad)
        self.vad_check.pack(side=tk.LEFT)
        ttk.Label(adv_row, text="Beam Size:").pack(side=tk.LEFT, padx=(20, 5))
        self.beam_spinbox = ttk.Spinbox(adv_row, from_=1, to=20, textvariable=self.beam_size, width=5)
        self.beam_spinbox.pack(side=tk.LEFT)

        # Max Duration
        duration_frame = ttk.Frame(settings_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        ttk.Label(duration_frame, text="最大段长 (秒):", width=15).pack(side=tk.LEFT)
        ttk.Scale(duration_frame, from_=10, to=120, orient=tk.HORIZONTAL, variable=self.max_duration, command=lambda s: self.max_duration.set(int(float(s)))).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(duration_frame, textvariable=self.max_duration, width=4).pack(side=tk.LEFT)
        
        # --- 3. 控制区 ---
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        self.start_button = ttk.Button(control_frame, text="开始处理文件", command=self.start_processing, state="disabled")
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        self.reset_button = ttk.Button(control_frame, text="更换模型", command=self.reset_model_config, state="disabled")
        self.reset_button.pack(side=tk.LEFT, padx=5)
        self.save_button = ttk.Button(control_frame, text="导出为 TXT", command=self.save_to_txt, state="disabled")
        self.save_button.pack(side=tk.RIGHT, ipady=5)

        # --- 4. 结果展示区 ---
        result_frame = ttk.LabelFrame(main_frame, text="处理结果", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.result_text = tk.Text(result_frame, wrap="word", height=15, state="disabled")
        scrollbar = ttk.Scrollbar(result_frame, command=self.result_text.yview)
        self.result_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- 5. 状态栏 ---
        status_frame = ttk.Frame(main_frame, padding=(0, 5))
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_label = ttk.Label(status_frame, text="请先配置并加载模型。")
        self.status_label.pack(side=tk.LEFT)
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    def init_hardware_options(self) -> None:
        """检测硬件并设置默认选项"""
        try:
            devices = ["cpu"]

            # Check CUDA availability
            if torch.cuda.is_available():
                devices.append("cuda")
                gpu_count = torch.cuda.device_count()
                gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
                self.device.set("cuda")
                logger.info(f"CUDA available: {gpu_count} GPU(s), Primary: {gpu_name}")
            else:
                self.device.set("cpu")
                logger.info("CUDA not available, using CPU")

            self.device_combo['values'] = devices
            self.update_compute_types()

        except Exception as e:
            logger.error(f"Error initializing hardware options: {e}")
            # Fallback to CPU only
            self.device.set("cpu")
            self.device_combo['values'] = ["cpu"]
            self.update_compute_types()

    def update_compute_types(self, event=None):
        """根据设备更新可用的计算精度"""
        device = self.device.get()
        if device == "cuda":
            # 对于 Ampere 及更高版本的 GPU，int8_float16 是一个很好的选择
            types = ["float16", "int8_float16", "int8"]
            self.compute_type.set("float16")
        else: # cpu
            types = ["int8", "int16", "float32"]
            self.compute_type.set("int8")
        self.compute_type_combo['values'] = types

    def load_model(self) -> None:
        """启动模型加载线程"""
        try:
            # Validate settings before loading
            if not self.model_size.get():
                messagebox.showerror("配置错误", "请选择模型大小")
                return

            if not self.device.get():
                messagebox.showerror("配置错误", "请选择运行设备")
                return

            if not self.compute_type.get():
                messagebox.showerror("配置错误", "请选择计算精度")
                return

            self.toggle_model_config_widgets(False)
            self.progress_bar.start()
            self.update_status("正在加载模型，请稍候...")

            logger.info(f"Loading model: {self.model_size.get()}, device: {self.device.get()}, compute_type: {self.compute_type.get()}")

            threading.Thread(
                target=self.load_model_thread,
                args=(
                    self.model_size.get(),
                    self.device.get(),
                    self.compute_type.get()
                ),
                daemon=True
            ).start()

        except Exception as e:
            logger.error(f"Error starting model loading: {e}")
            self.progress_bar.stop()
            self.toggle_model_config_widgets(True)
            messagebox.showerror("加载错误", f"启动模型加载失败: {e}")

    def load_model_thread(self, size: str, device: str, compute_type: str) -> None:
        """在工作线程中加载模型"""
        try:
            logger.info(f"Loading Whisper model: size={size}, device={device}, compute_type={compute_type}")

            # Load model with timeout handling
            model = WhisperModel(
                size,
                device=device,
                compute_type=compute_type,
                download_root=None,  # Use default cache directory
                local_files_only=False
            )

            logger.info("Model loaded successfully")
            self.result_queue.put(("model_loaded", model))

        except Exception as e:
            error_msg = f"模型加载失败: {str(e)}"
            logger.error(f"Model loading failed: {e}")
            logger.error(traceback.format_exc())

            # Provide more specific error messages
            if "CUDA" in str(e) and "out of memory" in str(e).lower():
                error_msg = "GPU内存不足，请尝试使用CPU或更小的模型"
            elif "No module named" in str(e):
                error_msg = f"缺少依赖库: {e}"
            elif "Connection" in str(e) or "timeout" in str(e).lower():
                error_msg = "网络连接问题，无法下载模型。请检查网络连接或使用本地模型"

            self.result_queue.put(("error", error_msg))

    def reset_model_config(self):
        """重置模型配置，允许用户重新选择"""
        self.model = None
        self.toggle_model_config_widgets(True)
        self.start_button.config(state="disabled")
        self.reset_button.config(state="disabled")
        self.update_status("模型已卸载。请重新配置并加载模型。")

    def browse_file(self) -> None:
        """Browse and select an audio/video file."""
        try:
            # Create file type filters
            audio_formats = " ".join(f"*{ext}" for ext in self.SUPPORTED_FORMATS['audio'])
            video_formats = " ".join(f"*{ext}" for ext in self.SUPPORTED_FORMATS['video'])
            all_formats = audio_formats + " " + video_formats

            filetypes = [
                ("所有支持的文件", all_formats),
                ("音频文件", audio_formats),
                ("视频文件", video_formats),
                ("所有文件", "*.*")
            ]

            path = filedialog.askopenfilename(
                title="选择音频或视频文件",
                filetypes=filetypes
            )

            if path and self.validate_file_path(path):
                self.file_path.set(path)
                file_size_mb = Path(path).stat().st_size / (1024 * 1024)
                self.update_status(f"已选择文件: {os.path.basename(path)} ({file_size_mb:.1f} MB)")
                logger.info(f"File selected: {path}")

        except Exception as e:
            logger.error(f"Error browsing file: {e}")
            messagebox.showerror("文件选择错误", f"选择文件时发生错误: {e}")

    def start_processing(self) -> None:
        """Start the audio processing workflow."""
        try:
            # Validation checks
            if not self.file_path.get():
                messagebox.showwarning("提示", "请先选择一个文件。")
                return

            if not self.model:
                messagebox.showwarning("提示", "请先加载模型。")
                return

            if self.is_processing:
                messagebox.showwarning("提示", "正在处理中，请等待完成。")
                return

            # Validate file again before processing
            if not self.validate_file_path(self.file_path.get()):
                return

            # Validate parameters
            if self.max_duration.get() < 10 or self.max_duration.get() > 300:
                messagebox.showerror("参数错误", "最大段长必须在10-300秒之间")
                return

            if self.beam_size.get() < 1 or self.beam_size.get() > 20:
                messagebox.showerror("参数错误", "Beam Size必须在1-20之间")
                return

            # Start processing
            self.is_processing = True
            self.toggle_processing_controls(False)
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.config(state="disabled")
            self.segments_data.clear()
            self.progress_bar.start()

            self.update_status("正在启动处理线程...")
            logger.info(f"Starting processing: {self.file_path.get()}")

            self.processing_thread = threading.Thread(
                target=self.process_audio_thread,
                args=(
                    self.file_path.get(),
                    self.max_duration.get(),
                    self.language_code.get().strip(),
                    self.use_vad.get(),
                    self.beam_size.get()
                ),
                daemon=True
            )
            self.processing_thread.start()

        except Exception as e:
            logger.error(f"Error starting processing: {e}")
            self.is_processing = False
            self.progress_bar.stop()
            self.toggle_processing_controls(True)
            messagebox.showerror("处理错误", f"启动处理失败: {e}")

    def process_audio_thread(self, file_path: str, max_duration: int, lang_code: str, use_vad: bool, beam_size: int) -> None:
        """Process audio file in a separate thread."""
        temp_wav_path = None

        try:
            logger.info(f"Starting audio processing: {file_path}")

            # Step 1: Convert audio format
            self.update_status_from_thread("步骤 1/4: 转换音频格式...")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                temp_wav_path = tmp_wav.name
                self.temp_files.append(temp_wav_path)  # Track for cleanup

            try:
                # Convert to WAV format with specific parameters for Whisper
                stream = ffmpeg.input(file_path)
                stream = ffmpeg.output(stream, temp_wav_path, ac=1, ar=16000, acodec='pcm_s16le')
                ffmpeg.run(stream, cmd='ffmpeg', overwrite_output=True, capture_stdout=True, capture_stderr=True)

                logger.info(f"Audio converted successfully: {temp_wav_path}")

            except ffmpeg.Error as e:
                error_msg = f"FFmpeg 转换错误: {e.stderr.decode() if e.stderr else str(e)}"
                logger.error(error_msg)
                self.result_queue.put(("error", error_msg))
                return
            except FileNotFoundError:
                error_msg = "FFmpeg 未找到。请确保已安装 FFmpeg 并添加到系统 PATH"
                logger.error(error_msg)
                self.result_queue.put(("error", error_msg))
                return

            # Verify converted file
            if not os.path.exists(temp_wav_path) or os.path.getsize(temp_wav_path) == 0:
                error_msg = "音频转换失败，生成的文件为空"
                logger.error(error_msg)
                self.result_queue.put(("error", error_msg))
                return

            # Step 2: Load audio for preview
            self.update_status_from_thread("步骤 2/4: 加载音频用于预览...")
            try:
                full_audio_segment = AudioSegment.from_file(temp_wav_path, format="wav")
                duration_minutes = len(full_audio_segment) / 1000 / 60
                logger.info(f"Audio loaded: {duration_minutes:.1f} minutes")

                if duration_minutes > 60:  # Warn for very long files
                    self.update_status_from_thread(f"音频时长 {duration_minutes:.1f} 分钟，处理可能需要较长时间...")

            except Exception as e:
                error_msg = f"音频加载失败: {e}"
                logger.error(error_msg)
                self.result_queue.put(("error", error_msg))
                return

            # Step 3: Transcribe with Whisper
            self.update_status_from_thread("步骤 3/4: 使用 Whisper 进行语音识别...")
            try:
                # Validate language code if provided
                if lang_code and len(lang_code) != 2:
                    logger.warning(f"Invalid language code: {lang_code}, using auto-detection")
                    lang_code = None

                segments, info = self.model.transcribe(
                    temp_wav_path,
                    word_timestamps=True,
                    language=lang_code if lang_code else None,
                    vad_filter=use_vad,
                    beam_size=beam_size,
                    temperature=0.0,  # Use deterministic decoding
                    compression_ratio_threshold=2.4,
                    log_prob_threshold=-1.0,
                    no_speech_threshold=0.6
                )

                detected_lang = info.language
                logger.info(f"Transcription completed. Detected language: {detected_lang}")

            except Exception as e:
                error_msg = f"语音识别失败: {e}"
                logger.error(f"Transcription failed: {e}")
                logger.error(traceback.format_exc())
                self.result_queue.put(("error", error_msg))
                return

            # Step 4: Smart segmentation
            self.update_status_from_thread("步骤 4/4: 智能分段并整理结果...")
            try:
                final_segments = self.perform_smart_segmentation(segments, max_duration)

                if not final_segments:
                    error_msg = "未检测到任何语音内容，请检查音频文件"
                    logger.warning(error_msg)
                    self.result_queue.put(("error", error_msg))
                    return

                logger.info(f"Segmentation completed: {len(final_segments)} segments")

                result_payload = {
                    "detected_lang": detected_lang,
                    "segments": final_segments,
                    "audio": full_audio_segment
                }
                self.result_queue.put(("success", result_payload))

            except Exception as e:
                error_msg = f"分段处理失败: {e}"
                logger.error(f"Segmentation failed: {e}")
                logger.error(traceback.format_exc())
                self.result_queue.put(("error", error_msg))
                return

        except Exception as e:
            error_msg = f"处理过程中发生未知错误: {e}"
            logger.error(f"Unexpected error in processing: {e}")
            logger.error(traceback.format_exc())
            self.result_queue.put(("error", error_msg))

        finally:
            # Clean up temporary file
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                    if temp_wav_path in self.temp_files:
                        self.temp_files.remove(temp_wav_path)
                    logger.info(f"Temporary file cleaned up: {temp_wav_path}")
                except Exception as e:
                    logger.error(f"Failed to clean up temporary file: {e}")

            # Reset processing flag
            self.is_processing = False

    def perform_smart_segmentation(self, whisper_segments, max_len_sec: int) -> List[Dict[str, Any]]:
        """Perform intelligent segmentation of transcribed audio.

        This function takes Whisper transcription segments and intelligently splits them
        into segments of appropriate length, preferring to break at sentence boundaries.

        Args:
            whisper_segments: Iterator of Whisper transcription segments
            max_len_sec: Maximum length of each segment in seconds

        Returns:
            List of segment dictionaries with 'start', 'end', and 'text' keys
        """
        final_segments = []

        # Extract all words from segments
        all_words = []
        for segment in whisper_segments:
            if hasattr(segment, 'words') and segment.words:
                all_words.extend(segment.words)

        if not all_words:
            logger.warning("No words found in transcription segments")
            return []

        logger.info(f"Processing {len(all_words)} words for segmentation")

        current_segment_start = all_words[0].start
        segment_word_start_index = 0

        # Sentence-ending punctuation for different languages
        sentence_endings = {
            'en': '.?!',
            'zh': '。？！',
            'ja': '。？！',
            'ko': '.?!。？！',
            'es': '.?!¿¡',
            'fr': '.?!',
            'de': '.?!',
            'ru': '.?!',
            'ar': '.؟!',
        }

        # Use comprehensive punctuation set
        all_punctuation = ''.join(sentence_endings.values())

        for i, word in enumerate(all_words):
            segment_duration = word.end - current_segment_start
            is_last_word = (i == len(all_words) - 1)

            # Continue if under max duration and not the last word
            if segment_duration < max_len_sec and not is_last_word:
                continue

            # Find the best split point (backtrack from current word)
            best_split_index = i

            if not is_last_word:  # Don't backtrack if forced to split at the end
                # Look for sentence-ending punctuation within reasonable range
                search_range = min(10, i - segment_word_start_index)  # Look back up to 10 words

                for j in range(i, max(segment_word_start_index - 1, i - search_range), -1):
                    word_text = all_words[j].word.strip()
                    if any(p in word_text for p in all_punctuation):
                        best_split_index = j
                        break

                # If no punctuation found, look for natural pauses (longer gaps)
                if best_split_index == i and i > segment_word_start_index:
                    for j in range(i, max(segment_word_start_index - 1, i - search_range), -1):
                        if j > 0:
                            gap = all_words[j].start - all_words[j-1].end
                            if gap > 0.5:  # 500ms pause
                                best_split_index = j - 1
                                break

            # Create segment
            segment_end_word = all_words[best_split_index]
            segment_words = all_words[segment_word_start_index : best_split_index + 1]
            segment_text = "".join(w.word for w in segment_words).strip()

            # Only add non-empty segments
            if segment_text:
                final_segments.append({
                    "start": current_segment_start,
                    "end": segment_end_word.end,
                    "text": segment_text
                })

            # Start new segment
            if best_split_index + 1 < len(all_words):
                next_word = all_words[best_split_index + 1]
                current_segment_start = next_word.start
                segment_word_start_index = best_split_index + 1
            else:  # Processed all words
                break

        logger.info(f"Created {len(final_segments)} segments from smart segmentation")
        return final_segments

    def check_queue(self) -> None:
        """Check for messages from worker threads."""
        try:
            # Process all available messages
            while True:
                try:
                    message_type, data = self.result_queue.get_nowait()

                    if message_type == "model_loaded":
                        self.progress_bar.stop()
                        self.model = data
                        self.update_status(f"模型 '{self.model_size.get()}' 加载成功！请选择文件并开始处理。")
                        self.start_button.config(state="normal")
                        self.reset_button.config(state="normal")
                        logger.info("Model loaded successfully")

                    elif message_type == "success":
                        self.progress_bar.stop()
                        self.is_processing = False
                        self.toggle_processing_controls(True)
                        self.update_status("处理完成！")
                        self.display_results(data)
                        logger.info("Processing completed successfully")

                    elif message_type == "error":
                        self.progress_bar.stop()
                        self.is_processing = False
                        self.update_status("处理失败。")

                        # Show error with more context
                        error_title = "处理错误"
                        if "FFmpeg" in data:
                            error_title = "音频转换错误"
                        elif "模型" in data:
                            error_title = "模型错误"
                        elif "网络" in data or "下载" in data:
                            error_title = "网络错误"

                        messagebox.showerror(error_title, data)
                        logger.error(f"Processing error: {data}")

                        # Re-enable controls after an error
                        self.toggle_model_config_widgets(True)
                        self.toggle_processing_controls(True)

                    elif message_type == "status":
                        self.update_status(data)

                except queue.Empty:
                    break

        except Exception as e:
            logger.error(f"Error in check_queue: {e}")

        finally:
            # Schedule next check
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after(100, self.check_queue)
    
    def display_results(self, data):
        # This function is largely unchanged.
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", tk.END)

        detected_lang = data["detected_lang"]
        self.full_audio = data["audio"]
        self.segments_data = data["segments"]

        self.result_text.insert(tk.END, f"检测到的语言: {detected_lang.upper()}\n")
        self.result_text.insert(tk.END, "=" * 40 + "\n\n")

        for i, seg in enumerate(self.segments_data):
            start_time, end_time, text = seg["start"], seg["end"], seg["text"]
            header = f"Segment {i+1}: {time.strftime('%H:%M:%S', time.gmtime(start_time))}.{int((start_time % 1) * 1000):03d} - {time.strftime('%H:%M:%S', time.gmtime(end_time))}.{int((end_time % 1) * 1000):03d}\n"
            self.result_text.insert(tk.END, header, f"h{i}")
            play_button = ttk.Button(self.result_text, text="▶️ 播放", command=lambda s=start_time, e=end_time: self.play_segment(s, e))
            self.result_text.window_create(tk.END, window=play_button, padx=5)
            self.result_text.insert(tk.END, f" {text}\n", f"t{i}")
            self.result_text.insert(tk.END, "-" * 40 + "\n\n")
            self.result_text.tag_config(f"h{i}", font=("Segoe UI", 10, "bold"))

        self.result_text.config(state="disabled")
        self.save_button.config(state="normal")

    def play_segment(self, start_sec: float, end_sec: float) -> None:
        """Play a specific audio segment.

        Args:
            start_sec: Start time in seconds
            end_sec: End time in seconds
        """
        if not self.full_audio:
            logger.warning("No audio loaded for playback")
            return

        try:
            start_ms = int(start_sec * 1000)
            end_ms = int(end_sec * 1000)

            # Validate time bounds
            if start_ms < 0 or end_ms > len(self.full_audio) or start_ms >= end_ms:
                logger.warning(f"Invalid playback range: {start_ms}-{end_ms}ms")
                return

            audio_segment = self.full_audio[start_ms:end_ms]

            # Play in separate thread to avoid blocking UI
            def play_audio():
                try:
                    play(audio_segment)
                except Exception as e:
                    logger.error(f"Audio playback failed: {e}")
                    # Note: Can't show messagebox from thread, just log

            threading.Thread(target=play_audio, daemon=True).start()
            logger.info(f"Playing segment: {start_sec:.1f}s - {end_sec:.1f}s")

        except Exception as e:
            logger.error(f"Error playing segment: {e}")
            messagebox.showerror("播放错误", f"播放音频段失败: {e}")

    def save_to_txt(self) -> None:
        """Save transcription results to a text file."""
        if not self.segments_data:
            messagebox.showwarning("提示", "没有可保存的数据")
            return

        try:
            # Generate default filename
            source_name = os.path.splitext(os.path.basename(self.file_path.get()))[0]
            default_filename = f"{source_name}_transcription.txt"

            file_path = filedialog.asksaveasfilename(
                title="保存转录结果",
                defaultextension=".txt",
                filetypes=[
                    ("文本文件", "*.txt"),
                    ("SRT字幕文件", "*.srt"),
                    ("所有文件", "*.*")
                ],
                initialfile=default_filename
            )

            if not file_path:
                return

            # Determine file format based on extension
            file_ext = Path(file_path).suffix.lower()

            with open(file_path, 'w', encoding='utf-8') as f:
                if file_ext == '.srt':
                    # Save as SRT subtitle format
                    self._save_as_srt(f)
                else:
                    # Save as plain text
                    self._save_as_txt(f)

            self.update_status(f"成功保存到: {os.path.basename(file_path)}")
            messagebox.showinfo("成功", f"文件已成功保存到:\n{file_path}")
            logger.info(f"Results saved to: {file_path}")

        except PermissionError:
            messagebox.showerror("保存失败", "文件被占用或没有写入权限")
        except Exception as e:
            error_msg = f"保存文件时发生错误: {e}"
            logger.error(error_msg)
            messagebox.showerror("保存失败", error_msg)

    def _save_as_txt(self, file_handle) -> None:
        """Save results in plain text format."""
        # Write header information
        file_handle.write(f"音频转录结果\n")
        file_handle.write(f"=" * 50 + "\n")
        file_handle.write(f"源文件: {self.file_path.get()}\n")
        file_handle.write(f"模型: {self.model_size.get()}\n")
        file_handle.write(f"设备: {self.device.get()}\n")
        file_handle.write(f"计算精度: {self.compute_type.get()}\n")
        file_handle.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        file_handle.write(f"总段数: {len(self.segments_data)}\n\n")

        # Write segments
        for i, seg in enumerate(self.segments_data):
            start_time, end_time, text = seg["start"], seg["end"], seg["text"]
            start_str = f"{time.strftime('%H:%M:%S', time.gmtime(start_time))}.{int((start_time % 1) * 1000):03d}"
            end_str = f"{time.strftime('%H:%M:%S', time.gmtime(end_time))}.{int((end_time % 1) * 1000):03d}"

            file_handle.write(f"段落 {i+1}: {start_str} --> {end_str}\n")
            file_handle.write(f"{text.strip()}\n\n")

    def _save_as_srt(self, file_handle) -> None:
        """Save results in SRT subtitle format."""
        for i, seg in enumerate(self.segments_data):
            start_time, end_time, text = seg["start"], seg["end"], seg["text"]

            # Convert to SRT time format (HH:MM:SS,mmm)
            start_str = f"{time.strftime('%H:%M:%S', time.gmtime(start_time))},{int((start_time % 1) * 1000):03d}"
            end_str = f"{time.strftime('%H:%M:%S', time.gmtime(end_time))},{int((end_time % 1) * 1000):03d}"

            file_handle.write(f"{i+1}\n")
            file_handle.write(f"{start_str} --> {end_str}\n")
            file_handle.write(f"{text.strip()}\n\n")

    def toggle_model_config_widgets(self, enabled: bool) -> None:
        """Enable or disable model configuration widgets.

        Args:
            enabled: True to enable widgets, False to disable
        """
        state = "normal" if enabled else "disabled"
        try:
            for widget in self.model_config_widgets:
                widget.config(state=state)
        except Exception as e:
            logger.error(f"Error toggling model config widgets: {e}")

    def toggle_processing_controls(self, enabled: bool) -> None:
        """Enable or disable processing control widgets.

        Args:
            enabled: True to enable widgets, False to disable
        """
        state = "normal" if enabled else "disabled"
        try:
            self.start_button.config(state=state)
            self.save_button.config(state="disabled")  # Always disable save button until results are ready
            self.reset_button.config(state=state)

            # Also disable transcription settings during processing
            self.vad_check.config(state=state)
            self.beam_spinbox.config(state=state)
        except Exception as e:
            logger.error(f"Error toggling processing controls: {e}")

    def update_status(self, message: str) -> None:
        """Update the status label with a new message.

        Args:
            message: Status message to display
        """
        try:
            self.status_label.config(text=message)
            logger.debug(f"Status updated: {message}")
        except Exception as e:
            logger.error(f"Error updating status: {e}")

    def update_status_from_thread(self, message: str) -> None:
        """Update status from a worker thread by queuing the message.

        Args:
            message: Status message to display
        """
        try:
            self.result_queue.put(("status", message))
        except Exception as e:
            logger.error(f"Error queuing status update: {e}")

def setup_theme(root: tk.Tk) -> None:
    """Setup application theme and styling."""
    try:
        # Try to use ttkthemes for better appearance
        from ttkthemes import ThemedTk
        # Note: We can't change root type after creation, so this is just for styling
        style = ttk.Style()
        style.theme_use("clam")  # Use clam as base

    except ImportError:
        logger.info("ttkthemes not available, using default themes")
        style = ttk.Style()
        available_themes = style.theme_names()

        # Choose best available theme
        if "clam" in available_themes:
            style.theme_use("clam")
        elif "vista" in available_themes:
            style.theme_use("vista")  # Good fallback on Windows
        elif "xpnative" in available_themes:
            style.theme_use("xpnative")  # Windows XP
        else:
            style.theme_use("default")

    # Configure custom styles
    try:
        style.configure("Accent.TButton",
                       foreground="white",
                       background="#0078D7",
                       focuscolor="none")
        style.map("Accent.TButton",
                 background=[('active', '#106ebe'),
                           ('pressed', '#005a9e')])

        # Configure other custom styles
        style.configure("Title.TLabel", font=("Segoe UI", 12, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9))

    except Exception as e:
        logger.warning(f"Failed to configure custom styles: {e}")

def main() -> None:
    """Main application entry point."""
    try:
        # Create main window
        root = tk.Tk()

        # Set up theme and styling
        setup_theme(root)

        # Create and run application
        app = AutoSegmenterApp(root)

        logger.info("Starting application main loop")
        root.mainloop()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        logger.error(traceback.format_exc())
        messagebox.showerror("致命错误", f"应用程序启动失败:\n{e}")
        sys.exit(1)

# --- 主程序入口 ---
if __name__ == "__main__":
    main()