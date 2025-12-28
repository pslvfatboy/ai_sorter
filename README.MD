# AI Enterprise File Sorter

An intelligent, local-first file organization tool powered by Llama 3.1. This script categorizes your loose files into a professional folder structure based on industry-specific bundles.

## Features
- **Privacy First**: Runs 100% locally via `llama-cpp-python`. No data leaves your machine.
- **Hybrid Context**: Uses both Filenames and PDF text extraction for high accuracy.
- **Audit Logging**: Every action is logged with a timestamp and command-line parameters.
- **Safety Mode**: Defaults to copying files. Moving files is an optional flag.
- **Flexible**: Swap between Corporate, Legal, Hospital, and Home bundles via `config.yaml`.

## Installation

### 1. Clone the Repo
```bash
git clone https://github.com/pslvfatboy/ai_sorter.git ai-file-sorter


### 2. Environment Setup
conda create -n ai_sort python=3.11 -y
conda activate ai_sort
pip install -r requirements.txt

### 3. Execution
python ai_sorter.py "C:/Path/To/Your/Unorganized/Files"

####To Move files into Organized Folder. <Original File will move to new location>
python ai_sorter.py "C:/Path/To/Files" --move


#### Custom AI Model
python ai_sorter.py "C:/Path" --model "./models/your_model.gguf"

