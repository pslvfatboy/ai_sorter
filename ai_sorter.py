---

### 5. Final Script Logic (`ai_sorter.py`)
This version includes the **Audit Table Summary** in the log as a final professional touch.



```python
import os
import shutil
import argparse
import sys
import psutil
import yaml
import logging
from datetime import datetime
from pathlib import Path
from llama_cpp import Llama
import pymupdf as fitz
from collections import Counter

def setup_logging(args):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"sort_log_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
    )
    logging.info("--- SESSION START ---")
    logging.info(f"Command Params: {args}")
    return log_file

def load_config(config_path):
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
        active = data.get('active_bundle')
        return active, data.get('bundles', {}).get(active)

class LocalAI:
    def __init__(self, model_path, bundle, categories):
        self.categories = categories
        self.bundle = bundle
        self.llm = Llama(model_path=model_path, n_ctx=2048, n_gpu_layers=-1, verbose=False)

    def classify(self, filename, text):
        prompt = f"""<|start_header_id|>system<|end_header_id|>
        Choose ONE category from: {", ".join(self.categories)}.
        Respond with CATEGORY NAME ONLY.<|eot_id|>
        <|start_header_id|>user<|end_header_id|>
        File: {filename} | Content: {text if text else 'None'}
        Category:<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""
        
        output = self.llm(prompt, max_tokens=25, stop=["<|eot_id|>"], echo=False)
        return output['choices'][0]['text'].strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Folder to sort")
    parser.add_argument("--model", default="./models/llama-3.1-8b-instruct.Q4_K_M.gguf")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--move", action="store_true")
    args = parser.parse_args()

    log_path = setup_logging(args)
    active_name, categories = load_config(args.config)
    ai = LocalAI(args.model, active_name, categories)
    root_path = Path(args.path)
    
    stats = Counter()

    for item in root_path.iterdir():
        if item.is_dir() or item.name == "Organized": continue

        text = None
        if item.suffix.lower() == ".pdf":
            try:
                doc = fitz.open(item)
                text = doc[0].get_text().strip()[:1000]
                doc.close()
            except: pass
            
        prediction = ai.classify(item.name, text)
        matched = next((c for c in categories if c.lower() in prediction.lower()), None)

        if matched:
            dest = root_path / "Organized" / matched
            dest.mkdir(parents=True, exist_ok=True)
            try:
                if args.move: shutil.move(str(item), str(dest / item.name))
                else: shutil.copy2(str(item), str(dest / item.name))
                logging.info(f"SUCCESS: {item.name} -> {matched}")
                stats[matched] += 1
            except Exception as e: logging.error(f"IO ERROR: {item.name} | {e}")
        else:
            logging.warning(f"UNCERTAIN: {item.name} | AI said: {prediction}")

    logging.info("--- SUMMARY TABLE ---")
    for cat, count in stats.items():
        logging.info(f"{cat}: {count} files")
    logging.info(f"Log saved to: {log_path}")

if __name__ == "__main__":
    main()