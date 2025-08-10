
# from datetime import datetime
# import os
# import time
# import json
# from pathlib import Path
# from dotenv import load_dotenv
# from datetime import datetime
# import re
# import sys

# # Import the LLMHandler
# from llmhandler import LLMHandler

# # Load environment variables
# load_dotenv()

# class SolutionAgent:
#     def __init__(self):
#         """Initialize SolutionAgent with LLMHandler for AI processing."""
#         try:
#             # Initialize the LLM handler instead of direct Gemini setup
#             self.llm_handler = LLMHandler()
#             self.processed_errors = set()

#             print("🔧 Solution Agent initialized")
#             print("🤖 AI Handler: Using LLMHandler with fallback support")
            
#             # Show available models
#             models = self.llm_handler.get_available_models()
#             if models:
#                 print("📋 Available Models:")
#                 for model in models:
#                     print(f"   • {model['name']} ({model['provider']}) - {model['type']}")
#             else:
#                 print("⚠️  No AI models available")
            
#             print("=" * 60)

#         except Exception as e:
#             print(f"❌ Failed to initialize LLMHandler: {e}")
#             raise ValueError(f"SolutionAgent initialization failed: {e}")

#     def load_error_log(self):
#         """Load error log from JSON file."""
#         try:
#             if os.path.exists('error_log.json'):
#                 with open('error_log.json', 'r') as f:
#                     return json.load(f)
#             return []
#         except Exception as e:
#             print(f"❌ Error loading log: {e}")
#             return []

#     def generate_solution(self, file_path, file_content, errors):
#         """Generate solution using LLMHandler instead of direct API calls."""
#         file_extension = Path(file_path).suffix.lower()
#         context = {
#             '.html': "This is an HTML file for a hotel booking system. Focus on proper HTML structure, accessibility, and semantic markup.",
#             '.css': "This is a CSS file for styling a hotel booking system. Focus on proper CSS syntax, responsive design, and modern styling practices.",
#             '.js': "This is a JavaScript file for a hotel booking system. Focus on proper syntax, error handling, and modern JavaScript practices.",
#         }.get(file_extension, "This is a code file that needs to be fixed.")
        
#         file_type = file_extension.upper().strip('.') or 'Code'

#         prompt = f"""
# You are an expert {file_type} developer working on a hotel booking system.

# Context: {context}

# Original Code:
# {file_content}

# Detected Issues:
# {errors}

# Please ONLY provide:
# 1. The COMPLETE corrected file content
# 2. ONLY FIX the listed issues — do NOT reformat or make stylistic changes
# 3. DO NOT add unrelated enhancements
# 4. DO NOT explain anything — only the result

# Format your response as:
# CORRECTED_CODE:
# [Complete corrected code here]

# RECOMMENDATIONS:
# [Optional brief improvements to consider — outside scope of this fix]

# METADATA:
# created_by: [your current Model Name]
# model_confidence: [Give an honest confidence estimate between 0.00 and 1.00 based on your certainty in the correctness of the fix. This should reflect your internal certainty level.]
# time_estimate_fix: [Estimated time to fix the error by ai agent, e.g. "2 minutes"]
# """

#         try:
#             print("🔄 Generating solution using LLMHandler...")
            
#             # Use LLMHandler with fallback instead of direct API calls
#             result = self.llm_handler.invoke_with_fallback(
#                 prompt=prompt,
#                 max_tokens=12000,
#                 temperature=0.2
#             )
            
#             if result['success']:
#                 print(f"✅ Solution generated using {result['agent']}")
#                 return result['response']
#             else:
#                 print(f"❌ LLMHandler failed: {result['error']}")
#                 return "❌ Failed to generate solution"
                
#         except Exception as e:
#             print(f"❌ Error calling LLMHandler: {e}")
#             return "❌ Failed to generate solution"

#     def parse_solution(self, solution_text):
#         """Parse the AI-generated solution text into structured data."""
#         corrected_code = ""
#         recommendations = []
#         metadata = {}
#         lines = solution_text.split('\n')
#         current_section = None

#         for line in lines:
#             stripped = line.strip()
#             if stripped.startswith('CORRECTED_CODE:'):
#                 current_section = 'code'
#                 continue
#             elif stripped.startswith('RECOMMENDATIONS:'):
#                 current_section = 'recommendations'
#                 continue
#             elif stripped.startswith('METADATA:'):
#                 current_section = 'metadata'
#                 continue

#             if current_section == 'code':
#                 corrected_code += line + '\n'
#             elif current_section == 'recommendations':
#                 cleaned = stripped.strip('-• ').strip()
#                 if cleaned:
#                     recommendations.append(cleaned)
#             elif current_section == 'metadata':
#                 if ':' in line:
#                     key, value = line.split(':', 1)
#                     metadata[key.strip()] = value.strip()

#         # Clean up code formatting
#         corrected_code = re.sub(r'^```[\w]*\n', '', corrected_code)
#         corrected_code = re.sub(r'\n?```[\s]*$', '', corrected_code)
#         corrected_code = corrected_code.strip()

#         # Add default recommendations if none found
#         if len(recommendations) < 3:
#             recommendations += [
#                 "Use semantic HTML elements to improve accessibility.",
#                 "Minimize inline styles and use CSS classes instead.",
#                 "Ensure all tags are properly closed and nested."
#             ][:3 - len(recommendations)]

#         # Set defaults for metadata
#         metadata.setdefault("created_by", "LLMHandler Agent")
#         metadata.setdefault("model_confidence", "0.87")
#         metadata.setdefault("time_estimate_fix", "2 minutes")

#         return {
#             'corrected_code': corrected_code,
#             'recommendations': recommendations,
#             'metadata': {
#                 'created_by': metadata["created_by"],
#                 'model_confidence': float(metadata["model_confidence"]),
#                 'time_estimate_fix': metadata["time_estimate_fix"]
#             }
#         }

#     def build_explanation_list(self, errors):
#         """Build explanation list for detected errors."""
#         explanation_list = []
#         for err in errors:
#             entry = {"error": err}
#             if "Missing <title>" in err:
#                 entry["explanation"] = "The HTML document is missing a <title> tag, which is important for SEO and accessibility."
#                 entry["code"] = "<title>Your Hotel Name</title>"
#             elif "Incomplete tag" in err:
#                 entry["explanation"] = "A tag is missing a closing bracket '>'. This causes rendering issues in HTML."
#                 entry["code"] = "<p>&copy; 2025 The Meridian Grand. All rights reserved.</p>"
#             else:
#                 entry["explanation"] = "This issue needs to be reviewed manually."
#                 entry["code"] = "[Review required]"
#             explanation_list.append(entry)
#         return explanation_list

#     def create_backup(self, file_path):
#         """Create backup of original file before applying solution."""
#         try:
#             backup_dir = Path("backups")
#             backup_dir.mkdir(exist_ok=True)
#             original_file = Path(file_path)
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             backup_filename = f"{original_file.stem}_{timestamp}{original_file.suffix}"
#             backup_path = backup_dir / backup_filename

#             with open(file_path, 'r', encoding='utf-8') as original:
#                 content = original.read()
#             with open(backup_path, 'w', encoding='utf-8') as backup:
#                 backup.write(content)

#             print(f"📋 Backup created: {backup_path}")
#             return str(backup_path)
#         except Exception as e:
#             print(f"❌ Failed to create backup: {e}")
#             return None

#     def update_process_log_with_solution(self, file_path, err_id, solution_id, available_solutions):
#         """Update process flow log with solution information."""
#         try:
#             if not os.path.exists('process_flow.json'):
#                 print("⚠️ process_flow.json not found.")
#                 return False

#             with open('process_flow.json', 'r') as f:
#                 process_log = json.load(f)

#             matched = False
#             for item in process_log:
#                 filename_match = item.get('filename', '').strip().lower() == file_path.strip().lower()
#                 error_id_match = item.get('monitor', {}).get('error_id', '').strip() == err_id.strip()

#                 if filename_match and error_id_match:
#                     explanations = [
#                         f"{sol['explanation']['text']}  code : {sol['explanation']['code_example']}"
#                         for sol in available_solutions
#                     ]

#                     item['Solution'] = {
#                         "solution_id": solution_id,
#                         "status": "analyzed",
#                         "time": datetime.now().strftime("%I:%M:%S %p"),
#                         "analysis": " | ".join(explanations)
#                     }

#                     matched = True
#                     break

#             if matched:
#                 with open('process_flow.json', 'w') as f:
#                     json.dump(process_log, f, indent=2)
#                 print(f"📝 process_flow.json updated with solution_id: {solution_id}")
#                 return True
#             else:
#                 print("⚠️ No matching entry found in process_flow.json for err_id:", err_id)
#                 return False

#         except Exception as e:
#             print(f"❌ Error updating process_flow.json: {e}")
#             return False

#     def save_solution(self, file_path, solution_data, errors, original_code, error_entry):
#         """Save the generated solution to solutions.json."""
#         try:
#             backup_path = self.create_backup(file_path)
#             solutions = []

#             if os.path.exists('solutions.json'):
#                 with open('solutions.json', 'r') as f:
#                     solutions = json.load(f)

#             # Generate unique solution ID
#             existing_ids = {s['solution_id'] for s in solutions}
#             i = 1
#             while f"SOL-{i:03}" in existing_ids:
#                 i += 1
#             solution_id = f"SOL-{i:03}"

#             err_id = error_entry.get('err_id', 'UnknownErrID')

#             # Build available_solutions
#             available_solutions = []
#             for err in errors:
#                 match = next((ex for ex in solution_data['explanation'] if ex['error'] == err), None)
#                 available_solutions.append({
#                     "error": err,
#                     "explanation": {
#                         "text": match["explanation"] if match else "Explanation not available.",
#                         "code_example": match["code"] if match else "[N/A]"
#                     }
#                 })

#             # Get current LLM status for metadata
#             llm_status = self.llm_handler.get_status()
#             active_model = "LLMHandler"
#             for service_type, service_info in llm_status.items():
#                 if service_info['available']:
#                     active_model = f"{service_info['name']} ({service_info['model']})"
#                     break

#             # Build solution entry
#             solution_entry = {
#                 "solution_id": solution_id,
#                 "err_id": err_id,
#                 "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "file": file_path,
#                 "backup_path": backup_path,
#                 "errors": errors,
#                 "corrected_code": solution_data['corrected_code'],
#                 "available_solutions": available_solutions,
#                 "status": "pending_review",
#                 "auto_apply": False,
#                 "requires_manual_review": True,
#                 "error_type": error_entry.get("error_type", "UnknownError"),
#                 "pipeline_stage": "solving",
#                 "commit_hash": "no hash",
#                 "git_push": "not pushed",
#                 "branch": "main",
#                 "model_confidence": solution_data['metadata']['model_confidence'],
#                 "time_estimate_fix": solution_data['metadata']['time_estimate_fix'],
#                 "created_by": active_model,
#                 "llm_handler_used": True,  # Flag to indicate LLMHandler was used
#             }

#             # Save to solutions.json
#             solutions.append(solution_entry)
#             with open('solutions.json', 'w') as f:
#                 json.dump(solutions, f, indent=2)
#             print("💾 Solution saved to 'solutions.json' using LLMHandler")

#             # Update process_flow.json
#             self.update_process_log_with_solution(
#                 file_path=file_path,
#                 err_id=err_id,
#                 solution_id=solution_id,
#                 available_solutions=available_solutions
#             )

#             return True

#         except Exception as e:
#             print(f"❌ Error saving solution: {e}")
#             return False

#     def save_solution_preview(self, file_path, solution_data):
#         """Save a preview of the corrected solution."""
#         try:
#             preview_dir = Path("solution_previews")
#             preview_dir.mkdir(exist_ok=True)
#             original_file = Path(file_path)
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             preview_filename = f"{original_file.stem}_corrected_{timestamp}{original_file.suffix}"
#             preview_path = preview_dir / preview_filename

#             with open(preview_path, 'w', encoding='utf-8') as preview:
#                 preview.write(solution_data['corrected_code'])

#             print(f"👀 Solution preview saved: {preview_path}")
#             return str(preview_path)
#         except Exception as e:
#             print(f"❌ Failed to save preview: {e}")
#             return None

#     def process_single_error(self, error_entry):
#         """Process a single error entry using LLMHandler."""
#         time.sleep(3)
#         print(f"\n🔍 Processing error [{error_entry.get('err_id', 'N/A')}] in: {error_entry['file']}")
        
#         try:
#             # Read the original file
#             with open(error_entry['file'], 'r', encoding='utf-8') as f:
#                 original_content = f.read()

#             # Generate solution using LLMHandler
#             solution_text = self.generate_solution(
#                 error_entry['file'],
#                 original_content,
#                 error_entry['errors']
#             )
            
#             # Debug: Print the raw solution text
#             print(f"🔍 Raw solution text length: {len(solution_text)}")
            
#             # Parse the solution
#             solution_data = self.parse_solution(solution_text)
#             solution_data['explanation'] = self.build_explanation_list(error_entry['errors'])

#             # Debug: Check corrected code
#             print(f"🔍 Corrected code length: {len(solution_data['corrected_code'])}")
#             if not solution_data['corrected_code']:
#                 print("❌ Warning: Corrected code is empty!")
#                 print(f"Raw solution text preview: {solution_text[:500]}...")

#             # Save preview
#             preview_path = self.save_solution_preview(error_entry['file'], solution_data)

#             # Save solution
#             if self.save_solution(error_entry['file'], solution_data, error_entry['errors'], original_content, error_entry):
#                 print(f"✅ Saved solution for {error_entry.get('err_id', 'N/A')}. Preview: {preview_path}")
#                 return True
#             else:
#                 print("❌ Failed to save solution")
#                 return False
                
#         except Exception as e:
#             print(f"❌ Error processing {error_entry['file']}: {e}")
#             return False

#     def process_errors(self):
#         """Process all detected errors in the error log."""
#         error_log = self.load_error_log()
#         for error_entry in error_log:
#             error_id = f"{error_entry['file']}_{error_entry['timestamp']}"
#             if error_id not in self.processed_errors and error_entry['status'] == 'detected':
#                 # Update status
#                 error_entry['status'] = 'Solved'
#                 error_entry['pipeline_stage'] = 'solving'
#                 error_entry['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
#                 # Save updated log
#                 with open('error_log.json', 'w') as f:
#                     json.dump(error_log, f, indent=2)

#                 # Process the error
#                 if self.process_single_error(error_entry):
#                     self.processed_errors.add(error_id)

#     def process_error_by_id(self, err_id):
#         """Process a specific error by its ID."""
#         error_log = self.load_error_log()
#         error_found = False
        
#         for error_entry in error_log:
#             if error_entry.get('err_id') == err_id:
#                 error_found = True
                
#                 if error_entry['status'] != 'detected':
#                     print(f"⚠️  Error {err_id} has status '{error_entry['status']}' - processing anyway")
                
#                 print(f"🎯 Running SolutionAgent on specific error: {err_id}")
                
#                 # Update status
#                 error_entry['status'] = 'fixing'
#                 error_entry['pipeline_stage'] = 'solving'
#                 error_entry['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
#                 # Save updated log
#                 with open('error_log.json', 'w') as f:
#                     json.dump(error_log, f, indent=2)

#                 # Process the error
#                 self.process_single_error(error_entry)
#                 break
        
#         if not error_found:
#             print(f"❌ Error with err_id={err_id} not found in error log.")

#     def get_llm_status(self):
#         """Get current LLM handler status."""
#         return self.llm_handler.get_status()

#     def run(self, err_id=None):
#         """Run the solution agent."""
#         if err_id:
#             self.process_error_by_id(err_id)
#         else:
#             print("🔄 Waiting for errors from Monitor Agent...")
#             try:
#                 while True:
#                     self.process_errors()
#                     time.sleep(3)
#             except KeyboardInterrupt:
#                 print("\n🛑 Stopped by user")
#                 print(f"🧾 Processed: {len(self.processed_errors)} entries")


# if __name__ == "__main__":
#     try:
#         agent = SolutionAgent()
#         err_id = None
#         if len(sys.argv) > 1 and sys.argv[1] == "--err-id" and len(sys.argv) > 2:
#             err_id = sys.argv[2]
#         agent.run(err_id)
#     except Exception as e:
#         print(f"❌ Failed to start: {e}")


from datetime import datetime
import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import re
import sys

# Import the LLMHandler
from llmhandler import LLMHandler

# Load environment variables
load_dotenv()

class SolutionAgent:
    def __init__(self):
        """Initialize SolutionAgent with LLMHandler for AI processing."""
        try:
            # Initialize the LLM handler instead of direct Gemini setup
            self.llm_handler = LLMHandler()
            self.processed_errors = set()

            print("🔧 Solution Agent initialized")
            print("🤖 AI Handler: Using LLMHandler with fallback support")
            
            # Show available models
            models = self.llm_handler.get_available_models()
            if models:
                print("📋 Available Models:")
                for model in models:
                    print(f"   • {model['name']} ({model['provider']}) - {model['type']}")
            else:
                print("⚠️  No AI models available")
            
            print("=" * 60)

        except Exception as e:
            print(f"❌ Failed to initialize LLMHandler: {e}")
            raise ValueError(f"SolutionAgent initialization failed: {e}")

    def load_error_log(self):
        """Load error log from JSON file."""
        try:
            if os.path.exists('error_log.json'):
                with open('error_log.json', 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"❌ Error loading log: {e}")
            return []

    def generate_targeted_fix(self, file_path, file_content, errors):
        """Generate targeted fixes for specific errors without regenerating entire file."""
        file_extension = Path(file_path).suffix.lower()
        context = {
            '.html': "This is an HTML file for a hotel booking system. Focus on proper HTML structure, accessibility, and semantic markup.",
            '.css': "This is a CSS file for styling a hotel booking system. Focus on proper CSS syntax, responsive design, and modern styling practices.",
            '.js': "This is a JavaScript file for a hotel booking system. Focus on proper syntax, error handling, and modern JavaScript practices.",
        }.get(file_extension, "This is a code file that needs to be fixed.")
        
        file_type = file_extension.upper().strip('.') or 'Code'
        line_count = len(file_content.split('\n'))
        char_count = len(file_content)
        
        print(f"📊 File stats: {line_count} lines, {char_count} characters")
        print(f"🎯 Using targeted fix approach for large file")

        prompt = f"""
You are an expert {file_type} developer. Analyze the file and provide SPECIFIC fixes for the listed errors.

TASK: Identify the exact locations and provide targeted fixes for these errors:
{errors}

File Information:
- File: {file_path}
- Type: {file_type}
- Lines: {line_count}
- Context: {context}

For EACH error, provide:
1. The problematic line(s) or section
2. The exact fix needed
3. The corrected line(s) or section

IMPORTANT: Only analyze the specific errors listed. Do not suggest other improvements.

FILE CONTENT TO ANALYZE:
{file_content}

Format your response as:
TARGETED_FIXES:
Error: [Error description]
Problem: [Exact problematic code/line]
Fix: [Exact corrected code/line]
Location: [Line number or section description]
---

METADATA:
created_by: [your model name]
model_confidence: [confidence 0.00-1.00]
time_estimate_fix: [time estimate]
"""

        try:
            print("🔄 Generating targeted fixes using LLMHandler...")
            
            # Use reasonable token limit for analysis
            result = self.llm_handler.invoke_with_fallback(
                prompt=prompt,
                max_tokens=8000,
                temperature=0.1
            )
            
            if result['success']:
                print(f"✅ Targeted fixes generated using {result['agent']}")
                return result['response']
            else:
                print(f"❌ LLMHandler failed: {result['error']}")
                return "❌ Failed to generate targeted fixes"
                
        except Exception as e:
            print(f"❌ Error calling LLMHandler: {e}")
            return "❌ Failed to generate targeted fixes"

    def apply_targeted_fixes(self, file_content, targeted_fixes_text):
        """Apply targeted fixes to the original file content."""
        try:
            lines = targeted_fixes_text.split('\n')
            fixes = []
            current_fix = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('Error:'):
                    if current_fix:
                        fixes.append(current_fix)
                    current_fix = {'error': line[6:].strip()}
                elif line.startswith('Problem:'):
                    current_fix['problem'] = line[8:].strip()
                elif line.startswith('Fix:'):
                    current_fix['fix'] = line[4:].strip()
                elif line.startswith('Location:'):
                    current_fix['location'] = line[9:].strip()
                elif line == '---' and current_fix:
                    fixes.append(current_fix)
                    current_fix = {}
            
            # Add last fix if exists
            if current_fix:
                fixes.append(current_fix)
            
            print(f"🔧 Found {len(fixes)} targeted fixes to apply")
            
            # Apply fixes to file content
            corrected_content = file_content
            successful_fixes = 0
            
            for i, fix in enumerate(fixes):
                if 'problem' in fix and 'fix' in fix:
                    problem_code = fix['problem']
                    fix_code = fix['fix']
                    
                    # Clean up the codes (remove quotes if present)
                    problem_code = problem_code.strip('"\'`')
                    fix_code = fix_code.strip('"\'`')
                    
                    print(f"🔧 Applying fix {i+1}: {fix.get('error', 'Unknown error')}")
                    print(f"   Problem: {problem_code[:100]}...")
                    print(f"   Fix: {fix_code[:100]}...")
                    
                    # Apply the fix
                    if problem_code in corrected_content:
                        corrected_content = corrected_content.replace(problem_code, fix_code, 1)
                        successful_fixes += 1
                        print(f"   ✅ Fix applied successfully")
                    else:
                        print(f"   ⚠️  Problem code not found in file")
                        # Try to find similar content (case insensitive)
                        if problem_code.lower() in corrected_content.lower():
                            print(f"   🔍 Found similar content (case mismatch)")
                        else:
                            print(f"   ❌ Content not found at all")
            
            print(f"✅ Applied {successful_fixes}/{len(fixes)} fixes successfully")
            return corrected_content, successful_fixes > 0
            
        except Exception as e:
            print(f"❌ Error applying targeted fixes: {e}")
            return file_content, False

    def generate_solution(self, file_path, file_content, errors):
        """Generate solution using targeted approach for large files or full regeneration for small files."""
        char_count = len(file_content)
        line_count = len(file_content.split('\n'))
        
        # Use targeted approach for large files (>15KB or >300 lines)
        if char_count > 15000 or line_count > 300:
            print(f"📏 Large file detected ({char_count} chars, {line_count} lines)")
            print("🎯 Using targeted fix approach to prevent truncation")
            
            # Get targeted fixes
            targeted_fixes_text = self.generate_targeted_fix(file_path, file_content, errors)
            
            if "❌" in targeted_fixes_text:
                print("⚠️  Targeted fixes failed, trying full regeneration with higher limits")
                return self.generate_full_solution(file_path, file_content, errors)
            
            # Apply targeted fixes
            corrected_content, fixes_applied = self.apply_targeted_fixes(file_content, targeted_fixes_text)
            
            if fixes_applied:
                print("✅ Targeted fixes applied successfully")
                return f"""CORRECTED_CODE:
{corrected_content}

RECOMMENDATIONS:
Use semantic HTML elements to improve accessibility.
Validate HTML structure regularly.
Consider adding error handling for form submissions.

METADATA:
created_by: LLMHandler Agent (Targeted Fix)
model_confidence: 0.90
time_estimate_fix: 3 minutes
"""
            else:
                print("⚠️  No targeted fixes could be applied, trying full regeneration")
                return self.generate_full_solution(file_path, file_content, errors)
        else:
            print("📏 Small file detected, using full regeneration approach")
            return self.generate_full_solution(file_path, file_content, errors)

    def generate_full_solution(self, file_path, file_content, errors):
        """Generate complete file solution for smaller files."""
        file_extension = Path(file_path).suffix.lower()
        context = {
            '.html': "This is an HTML file for a hotel booking system. Focus on proper HTML structure, accessibility, and semantic markup.",
            '.css': "This is a CSS file for styling a hotel booking system. Focus on proper CSS syntax, responsive design, and modern styling practices.",
            '.js': "This is a JavaScript file for a hotel booking system. Focus on proper syntax, error handling, and modern JavaScript practices.",
        }.get(file_extension, "This is a code file that needs to be fixed.")
        
        file_type = file_extension.upper().strip('.') or 'Code'
        line_count = len(file_content.split('\n'))
        char_count = len(file_content)

        prompt = f"""
You are an expert {file_type} developer. Your task is to fix ONLY the specified issues and return the COMPLETE file.

CRITICAL REQUIREMENTS:
1. Return the ENTIRE file content with fixes applied
2. Preserve ALL existing code, comments, and formatting
3. ONLY modify lines that contain the specific errors listed
4. Do NOT truncate, summarize, or shorten the code
5. The output must be a complete, functional file

File Information:
- File: {file_path}
- Type: {file_type}
- Lines: {line_count}
- Context: {context}

ERRORS TO FIX:
{errors}

ORIGINAL COMPLETE FILE:
{file_content}

INSTRUCTIONS:
- Fix ONLY the listed errors
- Keep everything else exactly the same
- Return the full file from first line to last line
- Do not add explanations or comments about the fixes

Format your response EXACTLY as:
CORRECTED_CODE:
[COMPLETE file content with ONLY the errors fixed - start from first line, end at last line]

RECOMMENDATIONS:
[Brief optional improvements - separate from the fix]

METADATA:
created_by: [your model name]
model_confidence: [confidence 0.00-1.00]
time_estimate_fix: [time estimate]
"""

        try:
            print("🔄 Generating full solution using LLMHandler...")
            
            # Use very high token limit for complete files
            max_tokens = min(30000, max(15000, char_count + 5000))
            print(f"🎯 Using max_tokens: {max_tokens}")
            
            result = self.llm_handler.invoke_with_fallback(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.1
            )
            
            if result['success']:
                print(f"✅ Full solution generated using {result['agent']}")
                return result['response']
            else:
                print(f"❌ LLMHandler failed: {result['error']}")
                return "❌ Failed to generate solution"
                
        except Exception as e:
            print(f"❌ Error calling LLMHandler: {e}")
            return "❌ Failed to generate solution"

    def parse_solution(self, solution_text):
        """Parse the AI-generated solution text into structured data."""
        corrected_code = ""
        recommendations = []
        metadata = {}
        lines = solution_text.split('\n')
        current_section = None

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('CORRECTED_CODE:'):
                current_section = 'code'
                continue
            elif stripped.startswith('RECOMMENDATIONS:'):
                current_section = 'recommendations'
                continue
            elif stripped.startswith('METADATA:'):
                current_section = 'metadata'
                continue

            if current_section == 'code':
                corrected_code += line + '\n'
            elif current_section == 'recommendations':
                cleaned = stripped.strip('-• ').strip()
                if cleaned:
                    recommendations.append(cleaned)
            elif current_section == 'metadata':
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

        # Clean up code formatting - be more careful to preserve content
        corrected_code = corrected_code.rstrip('\n')  # Remove trailing newlines only
        
        # Remove code block markers if present, but preserve the actual code
        if corrected_code.startswith('```'):
            lines = corrected_code.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]  # Remove first line with ```
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]  # Remove last line with ```
            corrected_code = '\n'.join(lines)

        # Validate that we have substantial code content
        if len(corrected_code.strip()) < 50:
            print("⚠️  Warning: Corrected code seems too short, possible truncation!")
            print(f"   Code length: {len(corrected_code)} characters")
            print(f"   Preview: {corrected_code[:200]}...")

        # Add default recommendations if none found
        if len(recommendations) < 3:
            recommendations += [
                "Use semantic HTML elements to improve accessibility.",
                "Minimize inline styles and use CSS classes instead.",
                "Ensure all tags are properly closed and nested."
            ][:3 - len(recommendations)]

        # Set defaults for metadata
        metadata.setdefault("created_by", "LLMHandler Agent")
        metadata.setdefault("model_confidence", "0.87")
        metadata.setdefault("time_estimate_fix", "2 minutes")

        return {
            'corrected_code': corrected_code,
            'recommendations': recommendations,
            'metadata': {
                'created_by': metadata["created_by"],
                'model_confidence': float(metadata["model_confidence"]),
                'time_estimate_fix': metadata["time_estimate_fix"]
            }
        }

    def build_explanation_list(self, errors):
        """Build explanation list for detected errors."""
        explanation_list = []
        for err in errors:
            entry = {"error": err}
            if "Missing <title>" in err:
                entry["explanation"] = "The HTML document is missing a <title> tag, which is important for SEO and accessibility."
                entry["code"] = "<title>Your Hotel Name</title>"
            elif "Incomplete tag" in err:
                entry["explanation"] = "A tag is missing a closing bracket '>'. This causes rendering issues in HTML."
                entry["code"] = "<p>&copy; 2025 The Meridian Grand. All rights reserved.</p>"
            else:
                entry["explanation"] = "This issue needs to be reviewed manually."
                entry["code"] = "[Review required]"
            explanation_list.append(entry)
        return explanation_list

    def create_backup(self, file_path):
        """Create backup of original file before applying solution."""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            original_file = Path(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{original_file.stem}_{timestamp}{original_file.suffix}"
            backup_path = backup_dir / backup_filename

            with open(file_path, 'r', encoding='utf-8') as original:
                content = original.read()
            with open(backup_path, 'w', encoding='utf-8') as backup:
                backup.write(content)

            print(f"📋 Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return None

    def update_process_log_with_solution(self, file_path, err_id, solution_id, available_solutions):
        """Update process flow log with solution information."""
        try:
            if not os.path.exists('process_flow.json'):
                print("⚠️ process_flow.json not found.")
                return False

            with open('process_flow.json', 'r') as f:
                process_log = json.load(f)

            matched = False
            for item in process_log:
                filename_match = item.get('filename', '').strip().lower() == file_path.strip().lower()
                error_id_match = item.get('monitor', {}).get('error_id', '').strip() == err_id.strip()

                if filename_match and error_id_match:
                    explanations = [
                        f"{sol['explanation']['text']}  code : {sol['explanation']['code_example']}"
                        for sol in available_solutions
                    ]

                    item['Solution'] = {
                        "solution_id": solution_id,
                        "status": "analyzed",
                        "time": datetime.now().strftime("%I:%M:%S %p"),
                        "analysis": " | ".join(explanations)
                    }

                    matched = True
                    break

            if matched:
                with open('process_flow.json', 'w') as f:
                    json.dump(process_log, f, indent=2)
                print(f"📝 process_flow.json updated with solution_id: {solution_id}")
                return True
            else:
                print("⚠️ No matching entry found in process_flow.json for err_id:", err_id)
                return False

        except Exception as e:
            print(f"❌ Error updating process_flow.json: {e}")
            return False

    def save_solution(self, file_path, solution_data, errors, original_code, error_entry):
        """Save the generated solution to solutions.json."""
        try:
            backup_path = self.create_backup(file_path)
            solutions = []

            if os.path.exists('solutions.json'):
                with open('solutions.json', 'r') as f:
                    solutions = json.load(f)

            # Generate unique solution ID
            existing_ids = {s['solution_id'] for s in solutions}
            i = 1
            while f"SOL-{i:03}" in existing_ids:
                i += 1
            solution_id = f"SOL-{i:03}"

            err_id = error_entry.get('err_id', 'UnknownErrID')

            # Build available_solutions
            available_solutions = []
            for err in errors:
                match = next((ex for ex in solution_data['explanation'] if ex['error'] == err), None)
                available_solutions.append({
                    "error": err,
                    "explanation": {
                        "text": match["explanation"] if match else "Explanation not available.",
                        "code_example": match["code"] if match else "[N/A]"
                    }
                })

            # Get current LLM status for metadata
            llm_status = self.llm_handler.get_status()
            active_model = "LLMHandler"
            for service_type, service_info in llm_status.items():
                if service_info['available']:
                    active_model = f"{service_info['name']} ({service_info['model']})"
                    break

            # Build solution entry
            solution_entry = {
                "solution_id": solution_id,
                "err_id": err_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "file": file_path,
                "backup_path": backup_path,
                "errors": errors,
                "corrected_code": solution_data['corrected_code'],
                "available_solutions": available_solutions,
                "status": "pending_review",
                "auto_apply": False,
                "requires_manual_review": True,
                "error_type": error_entry.get("error_type", "UnknownError"),
                "pipeline_stage": "solving",
                "commit_hash": "no hash",
                "git_push": "not pushed",
                "branch": "main",
                "model_confidence": solution_data['metadata']['model_confidence'],
                "time_estimate_fix": solution_data['metadata']['time_estimate_fix'],
                "created_by": active_model,
                "llm_handler_used": True,  # Flag to indicate LLMHandler was used
            }

            # Save to solutions.json
            solutions.append(solution_entry)
            with open('solutions.json', 'w') as f:
                json.dump(solutions, f, indent=2)
            print("💾 Solution saved to 'solutions.json' using LLMHandler")

            # Update process_flow.json
            self.update_process_log_with_solution(
                file_path=file_path,
                err_id=err_id,
                solution_id=solution_id,
                available_solutions=available_solutions
            )

            return True

        except Exception as e:
            print(f"❌ Error saving solution: {e}")
            return False

    def save_solution_preview(self, file_path, solution_data):
        """Save a preview of the corrected solution."""
        try:
            preview_dir = Path("solution_previews")
            preview_dir.mkdir(exist_ok=True)
            original_file = Path(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            preview_filename = f"{original_file.stem}_corrected_{timestamp}{original_file.suffix}"
            preview_path = preview_dir / preview_filename

            with open(preview_path, 'w', encoding='utf-8') as preview:
                preview.write(solution_data['corrected_code'])

            print(f"👀 Solution preview saved: {preview_path}")
            return str(preview_path)
        except Exception as e:
            print(f"❌ Failed to save preview: {e}")
            return None

    def process_single_error(self, error_entry):
        """Process a single error entry using LLMHandler."""
        time.sleep(3)
        print(f"\n🔍 Processing error [{error_entry.get('err_id', 'N/A')}] in: {error_entry['file']}")
        
        try:
            # Read the original file
            with open(error_entry['file'], 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            print(f"📊 Original file: {len(original_content)} characters, {len(original_content.split(chr(10)))} lines")

            # Generate solution using LLMHandler
            solution_text = self.generate_solution(
                error_entry['file'],
                original_content,
                error_entry['errors']
            )
            
            # Debug: Print the raw solution text
            print(f"🔍 Raw solution text length: {len(solution_text)}")
            
            # Parse the solution
            solution_data = self.parse_solution(solution_text)
            solution_data['explanation'] = self.build_explanation_list(error_entry['errors'])

            # Enhanced validation of corrected code
            original_lines = len(original_content.split('\n'))
            corrected_lines = len(solution_data['corrected_code'].split('\n'))
            
            print(f"📊 Code comparison:")
            print(f"   Original: {len(original_content)} chars, {original_lines} lines")
            print(f"   Corrected: {len(solution_data['corrected_code'])} chars, {corrected_lines} lines")
            
            # Warning if significant size difference
            size_ratio = len(solution_data['corrected_code']) / len(original_content) if len(original_content) > 0 else 0
            if size_ratio < 0.8:
                print(f"⚠️  WARNING: Corrected code is {size_ratio*100:.1f}% of original size!")
                print(f"   This suggests possible truncation. Check the solution carefully.")
                print(f"   First 200 chars of corrected: {solution_data['corrected_code'][:200]}...")
                print(f"   Last 200 chars of corrected: {solution_data['corrected_code'][-200:]}...")
            
            if not solution_data['corrected_code']:
                print("❌ ERROR: Corrected code is empty!")
                print(f"Raw solution text preview: {solution_text[:500]}...")
                return False

            # Save preview
            preview_path = self.save_solution_preview(error_entry['file'], solution_data)

            # Save solution
            if self.save_solution(error_entry['file'], solution_data, error_entry['errors'], original_content, error_entry):
                print(f"✅ Saved solution for {error_entry.get('err_id', 'N/A')}. Preview: {preview_path}")
                return True
            else:
                print("❌ Failed to save solution")
                return False
                
        except Exception as e:
            print(f"❌ Error processing {error_entry['file']}: {e}")
            return False

    def process_errors(self):
        """Process all detected errors in the error log."""
        error_log = self.load_error_log()
        for error_entry in error_log:
            error_id = f"{error_entry['file']}_{error_entry['timestamp']}"
            if error_id not in self.processed_errors and error_entry['status'] == 'detected':
                # Update status
                error_entry['status'] = 'Solved'
                error_entry['pipeline_stage'] = 'solving'
                error_entry['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save updated log
                with open('error_log.json', 'w') as f:
                    json.dump(error_log, f, indent=2)

                # Process the error
                if self.process_single_error(error_entry):
                    self.processed_errors.add(error_id)

    def process_error_by_id(self, err_id):
        """Process a specific error by its ID."""
        error_log = self.load_error_log()
        error_found = False
        
        for error_entry in error_log:
            if error_entry.get('err_id') == err_id:
                error_found = True
                
                if error_entry['status'] != 'detected':
                    print(f"⚠️  Error {err_id} has status '{error_entry['status']}' - processing anyway")
                
                print(f"🎯 Running SolutionAgent on specific error: {err_id}")
                
                # Update status
                error_entry['status'] = 'fixing'
                error_entry['pipeline_stage'] = 'solving'
                error_entry['last_checked'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save updated log
                with open('error_log.json', 'w') as f:
                    json.dump(error_log, f, indent=2)

                # Process the error
                self.process_single_error(error_entry)
                break
        
        if not error_found:
            print(f"❌ Error with err_id={err_id} not found in error log.")

    def get_llm_status(self):
        """Get current LLM handler status."""
        return self.llm_handler.get_status()

    def run(self, err_id=None):
        """Run the solution agent."""
        if err_id:
            self.process_error_by_id(err_id)
        else:
            print("🔄 Waiting for errors from Monitor Agent...")
            try:
                while True:
                    self.process_errors()
                    time.sleep(3)
            except KeyboardInterrupt:
                print("\n🛑 Stopped by user")
                print(f"🧾 Processed: {len(self.processed_errors)} entries")


if __name__ == "__main__":
    try:
        agent = SolutionAgent()
        err_id = None
        if len(sys.argv) > 1 and sys.argv[1] == "--err-id" and len(sys.argv) > 2:
            err_id = sys.argv[2]
        agent.run(err_id)
    except Exception as e:
        print(f"❌ Failed to start: {e}")