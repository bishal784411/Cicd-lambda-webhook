
import os
import cssutils
import subprocess
import time
import json
import hashlib
from pathlib import Path
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

# Import our custom LLM handler
from llmhandler import LLMHandler

load_dotenv()

class MonitorAgent:
    def __init__(self, watch_folder="Hotel-demo"):
        self.watch_folder = Path(watch_folder)
        self.file_hashes = {}
        self.error_log = []
        self.error_counter = 0
        
        # Initialize LLM Handler
        try:
            self.llm = LLMHandler()
            print(f"🤖 LLM Handler initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize LLM Handler: {e}")
            raise
        
        # Show LLM status
        self._display_llm_status()
        
        self.load_existing_error_count()

        print(f"Monitor Agent initialized - Watching: {self.watch_folder}")
        print("=" * 60)

    def _display_llm_status(self):
        """Display the status of available LLM models."""
        status = self.llm.get_status()
        models = self.llm.get_available_models()
        
        print("\n🔍 LLM Configuration:")
        for model in models:
            type_label = model['type'].title()
            print(f"  {type_label}: {model['name']} ({model['provider']})")
        
        if not models:
            print("  ⚠️  No LLM models available!")

    def ai_analyze_error(self, file_path, errors):
        """Analyze errors using the LLM handler with automatic fallback."""
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()

            for error in errors:
                prompt = f"""
You are an AI code reviewer. Analyze the following file and the specific error below.

File: {file_path}
Error: {error}

Code:
{file_content}

Please respond ONLY in this exact format:
---

Error:
[One-line short description of the error if the error is simple, but provide a concise explanation if the error is more complex.]

Error Type:
[A concise error category like "SyntaxError", "HTMLTagError", "AccessibilityError", etc. according to error]

Analysis:
[Brief, clear explanation tailored to error complexity]

Correction:
[One or two sentence explanation of the fix, followed by fix or corrected code snippet, no repetition of error or analysis]

Confidence:
[Rate your confidence in this analysis on a scale of 1-100, where 100 means absolutely certain]

---
"""

                # Use LLM handler with automatic fallback
                llm_result = self.llm.invoke_with_fallback(prompt, max_tokens=1000, temperature=0.1)
                
                if llm_result['success']:
                    # Parse the AI response
                    parsed_result = self._parse_ai_response(
                        llm_result['response'], 
                        error, 
                        llm_result['agent'], 
                        llm_result['model']
                    )
                    results.append(parsed_result)
                else:
                    # Both AI agents failed
                    results.append({
                        "error": error,
                        "error_type": "AIAnalysisError",
                        "analysis": f"All AI agents failed: {llm_result['error']}",
                        "correction": "N/A",
                        "confidence": 0,
                        "confidence_text": "AI analysis failed",
                        "agent_used": llm_result['agent'],
                        "model_name": llm_result['model']
                    })

                time.sleep(1)  # Short delay between requests

        except Exception as e:
            results.append({
                "error": "General Error",
                "error_type": "SystemError",
                "analysis": f"AI analysis system error: {str(e)}",
                "correction": "N/A",
                "confidence": 0,
                "confidence_text": "System error",
                "agent_used": "None (Error)",
                "model_name": "None"
            })

        return results

    def _parse_ai_response(self, ai_response, original_error, agent_used, model_name):
        """Parse the structured AI response."""
        try:
            match = re.search(
                r"Error:\s*(.*?)\n+Error Type:\s*(.*?)\n+Analysis:\s*(.*?)\n+Correction:\s*(.*?)\n+Confidence:\s*(.*?)(?:\n|$)",
                ai_response,
                re.DOTALL
            )
            
            if match:
                confidence_str = match.group(5).strip()
                # Clean up confidence text and extract numeric value
                confidence_clean = re.sub(r'[\n\r\-]+.*$', '', confidence_str).strip()
                confidence_match = re.search(r'(\d+)', confidence_clean)
                confidence_score = int(confidence_match.group(1)) if confidence_match else 85
                
                return {
                    "error": match.group(1).strip(),
                    "error_type": match.group(2).strip(),
                    "analysis": match.group(3).strip(),
                    "correction": match.group(4).strip(),
                    "confidence": confidence_score,
                    "confidence_text": confidence_clean,
                    "agent_used": agent_used,
                    "model_name": model_name
                }
            else:
                return {
                    "error": original_error,
                    "error_type": "ParseError",
                    "analysis": f"AI response parsing failed. Raw response: {ai_response[:200]}...",
                    "correction": "N/A",
                    "confidence": 0,
                    "confidence_text": "Parsing failed",
                    "agent_used": agent_used,
                    "model_name": model_name
                }
        except Exception as e:
            return {
                "error": original_error,
                "error_type": "ParseError",
                "analysis": f"Response parsing error: {str(e)}",
                "correction": "N/A",
                "confidence": 0,
                "confidence_text": "Parse error",
                "agent_used": agent_used,
                "model_name": model_name
            }

    def has_pending_errors(self):
        try:
            if os.path.exists('error_log.json'):
                with open('error_log.json', 'r') as f:
                    error_log = json.load(f)
                return any(error.get('status') == 'detected' for error in error_log)
            return False
        except:
            return False

    def calculate_file_hash(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None

    def validate_html(self, file_path):
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()

            for i, line in enumerate(lines, 1):
                if re.search(r'<[^>]*$', line) and not re.search(r'/>$', line):
                    errors.append(f"Line {i}: Incomplete tag (likely missing '>') -> {line.strip()}")
                for tag in ['link', 'meta', 'img', 'input', 'br', 'hr', 'source']:
                    if re.search(fr'<{tag}[^>]*$', line, re.IGNORECASE):
                        errors.append(f"Line {i}: Possibly malformed <{tag}> tag -> {line.strip()}")
                if re.search(r'<a(\s|>)', line):
                    match = re.search(r'<a[^>]*href\s*=\s*["\']([^"\']*)["\']', line)
                    if match and not match.group(1).strip():
                        errors.append(f"Line {i}: Empty href in <a> tag -> {line.strip()}")
                    elif not match:
                        errors.append(f"Line {i}: Missing href attribute in <a> tag -> {line.strip()}")
                if '<img' in line and not re.search(r'alt\s*=\s*["\'].*?["\']', line):
                    errors.append(f"Line {i}: Missing alt attribute in <img> tag -> {line.strip()}")

            soup = BeautifulSoup(content, 'html.parser')
            if not soup.find('html'):
                errors.append("Missing <html> tag")
            if not soup.find('head'):
                errors.append("Missing <head> tag")
            if not soup.find('body'):
                errors.append("Missing <body> tag")
            if not soup.find('title'):
                errors.append("Missing <title> tag in head")

            open_tags = re.findall(r'<([a-zA-Z][^/> \t\n]*)[^>]*?>', content)
            close_tags = re.findall(r'</([a-zA-Z][^>]*)>', content)
            self_closing = {'link', 'img', 'br', 'hr', 'input', 'meta', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr'}

            for tag in open_tags:
                tag_lower = tag.lower()
                if tag_lower not in self_closing and tag_lower not in [t.lower() for t in close_tags]:
                    errors.append(f"Unclosed tag: <{tag}>")

        except Exception as e:
            errors.append(f"HTML parsing error: {str(e)}")

        return errors

    def validate_css(self, file_path):
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                errors.append(f"Mismatched braces: {open_braces} opening, {close_braces} closing")

            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and ':' in line and not line.endswith((';', '{', '}')) and not line.startswith(('/*', '*', '@')):
                    errors.append(f"Missing semicolon on line {i}: {line}")

            used_vars = set(re.findall(r'var\(\s*(--[\w-]+)', content))
            defined_vars = set()
            root_match = re.search(r':root\s*{([^}]*)}', content, re.DOTALL)
            if root_match:
                root_block = root_match.group(1)
                defined_vars = set(re.findall(r'(--[\w-]+)\s*:', root_block))

            undefined_vars = used_vars - defined_vars
            for var in undefined_vars:
                errors.append(f"CSS variable {var} used but not defined in :root")

        except Exception as e:
            errors.append(f"CSS parsing error: {str(e)}")

        return errors

    def validate_javascript(self, file_path):
        errors = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.count('{') != content.count('}'):
                errors.append("Mismatched braces in JavaScript")
            if content.count('(') != content.count(')'):
                errors.append("Mismatched parentheses in JavaScript")
            if 'console.log' in content:
                errors.append("Found console.log statements (should be removed in production)")
        except Exception as e:
            errors.append(f"JavaScript parsing error: {str(e)}")
        return errors

    def update_process_flow(self, entry_data):
        process_file = 'process_flow.json'
        try:
            if os.path.exists(process_file):
                with open(process_file, 'r') as f:
                    process_flow = json.load(f)
            else:
                process_flow = []

            # Generate next process ID (Pro-001, Pro-002, ...)
            max_id = 0
            for item in process_flow:
                pid = item.get('id')
                if pid and pid.startswith("Pro-"):
                    try:
                        num = int(pid.split('-')[1])
                        if num > max_id:
                            max_id = num
                    except:
                        continue
            next_id = f"Pro-{max_id + 1:03d}"

            # Avoid duplicate entries based on error_id + error string
            duplicate = False
            for item in process_flow:
                if (
                    item.get('monitor', {}).get('error_id') == entry_data['monitor']['error_id'] and
                    item.get('monitor', {}).get('error') == entry_data['monitor']['error']
                ):
                    duplicate = True
                    break
            if duplicate:
                print(f"🔁 Skipping duplicate process entry for error_id: {entry_data['monitor']['error_id']}, error: {entry_data['monitor']['error']}")
                return

            current_time = datetime.now().strftime("%I:%M:%S %p")

            full_entry = {
                "id": next_id,
                "filename": entry_data["filename"],
                "error_type": entry_data["error_type"],
                "monitor": {
                    "error_id": entry_data["monitor"]["error_id"],
                    "status": entry_data["monitor"]["status"],
                    "time": current_time,
                    "error": entry_data["monitor"]["error"],
                },
                "Solution": {
                    "solution_id": "",
                    "status": "pending",
                    "time": "",
                    "analysis": "Waiting for errors from Monitor Agent"
                },
                "Fix": {
                    "fix_id": "",
                    "status": "pending",
                    "time": "",
                    "analysis": "Awaiting solution analysis from the agent."
                },
                "Deploy": {
                    "fix_id": "",
                    "status": "pending",
                    "time": "",
                    "analysis": "Push from the respective fix page."
                }
            }

            process_flow.append(full_entry)

            with open(process_file, 'w') as f:
                json.dump(process_flow, f, indent=2)

            print(f"✅ Added to process_flow.json: {next_id}")

        except Exception as e:
            print(f"❌ Failed to update process_flow.json: {e}")

    def load_existing_error_count(self):
        try:
            if os.path.exists('error_log.json'):
                with open('error_log.json', 'r') as f:
                    errors = json.load(f)
                max_id = 0
                for e in errors:
                    eid = e.get('err_id')
                    if eid and eid.startswith("Err-"):
                        num_part = int(eid.split('-')[1])
                        if num_part > max_id:
                            max_id = num_part
                self.error_counter = max_id
        except Exception as e:
            print(f"Failed to load existing error count: {e}")

    def scan_files(self):
        if not self.watch_folder.exists():
            print(f"Watch folder '{self.watch_folder}' not found!")
            return

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        changes_detected = False

        for file_path in self.watch_folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.html', '.css', '.js']:
                current_hash = self.calculate_file_hash(file_path)
                file_key = str(file_path)

                if file_key not in self.file_hashes or self.file_hashes[file_key] != current_hash:
                    changes_detected = True
                    self.file_hashes[file_key] = current_hash

                    print(f"\nCHANGE DETECTED: {file_path}")
                    print(f"Time: {current_time}")

                    errors = []
                    if file_path.suffix.lower() == '.html':
                        errors = self.validate_html(file_path)
                    elif file_path.suffix.lower() == '.css':
                        errors = self.validate_css(file_path)
                    elif file_path.suffix.lower() == '.js':
                        errors = self.validate_javascript(file_path)

                    if errors:
                        print(f"ERRORS FOUND in {file_path}:")
                        for err in errors:
                            print(f"   • {err}")

                        ai_results = self.ai_analyze_error(file_path, errors)
                        ai_analysis_list = []
                        fix_solution_list = []

                        print("\nAI Analyses and Suggested Fixes:")
                        for i, item in enumerate(ai_results, 1):
                            ai_analysis_list.append({
                                "analysis": item["analysis"],
                                "agent_used": item.get("agent_used", "unknown"),
                                "model_name": item.get("model_name", "unknown"),
                                "confidence": item.get("confidence", 0),
                                "confidence_text": item.get("confidence_text", "unknown")
                            })
                            fix_solution_list.append({
                                "correction": item["correction"]
                            })
                            
                            confidence_display = f"{item.get('confidence', 0)}% ({item.get('confidence_text', 'unknown')})"
                            print(f"\nError {i}: {item['error']}")
                            print(f"  Model: {item.get('model_name', 'unknown')} via {item.get('agent_used', 'unknown')}")
                            print(f"  Confidence: {confidence_display}")
                            print(f"  Analysis: {item['analysis']}")
                            print(f"  Correction: {item['correction']}")
                        
                        self.error_counter += 1
                        err_id_str = f"Err-{self.error_counter:03d}"

                        error_entry = {
                            "err_id": err_id_str,
                            "timestamp": current_time,
                            "last_checked": current_time,
                            "file": str(file_path),
                            "errors": errors,
                            "error_type": ai_results[0].get("error_type", "UnknownError") if ai_results else "UnknownError",
                            "severity": "high" if "unclosed" in ' '.join(errors).lower() else "medium",
                            "pipeline_stage": "monitoring",
                            "commit_hash": "no hash",
                            "git_push": "not pushed",
                            "branch": "main",
                            "ai_analysis": ai_analysis_list,
                            "fix_solution": fix_solution_list,
                            "status": "detected"
                        }

                        self.error_log.append(error_entry)
                        self.save_error_log()
                        print("\nError logged for Solution Agent processing")
                        
                        for error in errors:
                            process_flow_entry = {
                                "filename": str(file_path),
                                "error_type": error_entry["error_type"],
                                "monitor": {
                                    "error_id": err_id_str,
                                    "status": "detected",
                                    "error": error
                                }
                            }
                            self.update_process_flow(process_flow_entry)

                    else:
                        for error_entry in self.error_log:
                            if error_entry['file'] == str(file_path) and error_entry['status'] == 'detected':
                                error_entry['status'] = 'resolved'
                                error_entry['last_checked'] = current_time
                        self.save_error_log()
                        print(f"No errors found in {file_path}")

        if not changes_detected and not self.has_pending_errors():
            print(f"🔍 [{current_time}] No changes detected - System monitoring...")

    def save_error_log(self):
        try:
            existing_errors = []
            if os.path.exists('error_log.json'):
                with open('error_log.json', 'r') as f:
                    existing_errors = json.load(f)

            combined = existing_errors + [
                e for e in self.error_log
                if not any(e['timestamp'] == old['timestamp'] and e['file'] == old['file'] for old in existing_errors)
            ]

            with open('error_log.json', 'w') as f:
                json.dump(combined, f, indent=2)

            self.error_log = combined
        except Exception as e:
            print(f"Error saving log: {e}")

    def load_existing_hashes(self):
        print("Loading existing file states...")
        for file_path in self.watch_folder.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.html', '.css', '.js']:
                self.file_hashes[str(file_path)] = self.calculate_file_hash(file_path)
                print(f"   • {file_path}")

    def run(self):
        print("Starting continuous monitoring...")
        print("Supported file types: HTML, CSS, JavaScript")
        
        # Display LLM status in a user-friendly way
        models = self.llm.get_available_models()
        if models:
            primary_models = [m for m in models if m['type'] == 'primary']
            secondary_models = [m for m in models if m['type'] == 'secondary']
            
            ai_status = ""
            if primary_models:
                ai_status = f"{primary_models[0]['name']} (Primary)"
            if secondary_models:
                ai_status += f" + {secondary_models[0]['name']} (Fallback)" if ai_status else f"{secondary_models[0]['name']} (Only)"
            
            print(f"AI Analysis: {ai_status}")
        else:
            print("AI Analysis: ❌ No models available")
            
        print("Press Ctrl+C to stop monitoring\n")

        self.load_existing_hashes()

        try:
            while True:
                self.scan_files()
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
            print("Session Summary:")
            print(f"   • Total errors detected: {len(self.error_log)}")
            print(f"   • Files monitored: {len(self.file_hashes)}")
            
            # Show LLM usage statistics
            models_used = {}
            for error in self.error_log:
                for analysis in error.get('ai_analysis', []):
                    model = analysis.get('model_name', 'unknown')
                    models_used[model] = models_used.get(model, 0) + 1
            
            if models_used:
                print("   • LLM Usage:")
                for model, count in models_used.items():
                    print(f"     - {model}: {count} analyses")
            
            print("Error log saved to 'error_log.json'")


if __name__ == "__main__":
    try:
        monitor = MonitorAgent()
        monitor.run()
    except Exception as e:
        print(f"Monitor Agent failed to start: {e}")
        print("Make sure you have AWS credentials configured and/or GEMINI_API_KEY in your .env file")



