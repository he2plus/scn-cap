from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but you can fine-tune them
build_exe_options = {
    "packages": ["os", "tkinter", "PIL", "threading", "time"],
    "excludes": ["node-fetch"],
    "include_files": ["4nfavicon.jpeg"]  # Include any additional files needed
}

setup(
    name="ScreenCaptureTool",
    version="1.0",
    description="A simple screen capture tool",
    options={"build_exe": build_exe_options},
    executables=[Executable("screen_capture_tool.py", base="Win32GUI")]
)
