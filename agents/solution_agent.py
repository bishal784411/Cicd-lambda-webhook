# from datetime import datetime
# import os
# import time
# import json
# import requests
# from pathlib import Path
# from dotenv import load_dotenv
# from datetime import datetime
# import re
# import sys

# # Load environment variables
# load_dotenv()

# class SolutionAgent:
#     def __init__(self):
#         self.gemini_api_key = os.getenv('GEMINI_API_KEY')
#         self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_api_key}"
#         self.processed_errors = set()

#         if not self.gemini_api_key:
#             raise ValueError("GEMINI_API_KEY not found in environment variables")

#         print("🔧 Solution Agent initialized")
#         print("🤖 AI Model: Gemini 2.0 Flash")
#         print("=" * 60)

#     def load_error_log(self):
#         try:
#             if os.path.exists('error_log.json'):
#                 with open('error_log.json', 'r') as f:
#                     return json.load(f)
#             return []
#         except Exception as e:
#             print(f" Error loading log: {e}")
#             return []

#     def generate_solution(self, file_path, file_content, errors):
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
# model_confidence: [Give an honest confidence estimate between 0.00 and 1.00 based on your certainty in the correctness of the fix. This should reflect your internal certainty level.
# ]
# time_estimate_fix: [Estimated time to fix the error by ai agent, e.g. "2 minutes"]
# """

#         try:
#             payload = {
#                 "contents": [{"parts": [{"text": prompt}]}],
#                 "generationConfig": {
#                     "temperature": 0.2,
#                     "topK": 40,
#                     "topP": 0.95,
#                     "maxOutputTokens": 12000
#                 }
#             }

#             response = requests.post(self.gemini_url, json=payload)
#             if response.status_code == 200:
#                 result = response.json()
#                 if 'candidates' in result and len(result['candidates']) > 0:
#                     return result['candidates'][0]['content']['parts'][0]['text']
#             else:
#                 print(f" API Error: {response.status_code} - {response.text}")
#         except Exception as e:
#             print(f" Error calling Gemini API: {e}")
        
#         return " Failed to generate solution"

#     def parse_solution(self, solution_text):
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
#         metadata.setdefault("created_by", "Gemini 2.0 Flash")
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
#             print(f" Failed to create backup: {e}")
#             return None

#     def update_process_log_with_solution(self, file_path, err_id, solution_id, available_solutions):
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
#             print(f" Error updating process_flow.json: {e}")
#             return False


#     def save_solution(self, file_path, solution_data, errors, original_code, error_entry):
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

#             # Define context
#             file_extension = Path(file_path).suffix.lower()
#             context = {
#                 '.html': "This is an HTML file for a hotel booking system. Focus on proper HTML structure, accessibility, and semantic markup.",
#                 '.css': "This is a CSS file for styling a hotel booking system. Focus on proper CSS syntax, responsive design, and modern styling practices.",
#                 '.js': "This is a JavaScript file for a hotel booking system. Focus on proper syntax, error handling, and modern JavaScript practices.",
#             }.get(file_extension, "This is a code file that needs to be fixed.")

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
#                 "created_by": solution_data['metadata']['created_by'],
#             }

#             # Save to solutions.json
#             solutions.append(solution_entry)
#             with open('solutions.json', 'w') as f:
#                 json.dump(solutions, f, indent=2)
#             print("💾 Solution saved to 'solutions.json' in full structure")

#             # ✅ Update process_flow.json using a separate method
#             self.update_process_log_with_solution(
#                 file_path=file_path,
#                 err_id=err_id,
#                 solution_id=solution_id,
#                 available_solutions=available_solutions
#             )

#             return True

#         except Exception as e:
#             print(f" Error saving solution: {e}")
#             return False

#     def save_solution_preview(self, file_path, solution_data):
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
#             print(f" Failed to save preview: {e}")
#             return None

#     def process_single_error(self, error_entry):
#         """Process a single error entry"""
#         time.sleep(3)
#         print(f"\n  Processing error [{error_entry.get('err_id', 'N/A')}] in: {error_entry['file']}")
        
#         try:
#             # Read the original file
#             with open(error_entry['file'], 'r', encoding='utf-8') as f:
#                 original_content = f.read()

#             # Generate solution
#             solution_text = self.generate_solution(
#                 error_entry['file'],
#                 original_content,
#                 error_entry['errors']
#             )
            
#             # Debug: Print the raw solution text
#             print(f"  Raw solution text length: {len(solution_text)}")
            
#             # Parse the solution
#             solution_data = self.parse_solution(solution_text)
#             solution_data['explanation'] = self.build_explanation_list(error_entry['errors'])

#             # Debug: Check corrected code
#             print(f"  Corrected code length: {len(solution_data['corrected_code'])}")
#             if not solution_data['corrected_code']:
#                 print(" Warning: Corrected code is empty!")
#                 print(f"Raw solution text preview: {solution_text[:500]}...")

#             # Save preview
#             preview_path = self.save_solution_preview(error_entry['file'], solution_data)

#             # Save solution
#             if self.save_solution(error_entry['file'], solution_data, error_entry['errors'], original_content, error_entry):
#                 print(f"✅ Saved solution for {error_entry.get('err_id', 'N/A')}. Preview: {preview_path}")
#                 return True
#             else:
#                 print(" Failed to save solution")
#                 return False
                
#         except Exception as e:
#             print(f" Error processing {error_entry['file']}: {e}")
#             return False

#     def process_errors(self):
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
#             print(f" Error with err_id={err_id} not found in error log.")

#     def run(self, err_id=None):
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
#         print(f" Failed to start: {e}")


from datetime import datetime
import os
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import re
import sys

# Load environment variables
load_dotenv()

class SolutionAgent:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_api_key}"
        self.processed_errors = set()

        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        print(" Solution Agent initialized")
        print(" AI Model: Gemini 2.0 Flash")
        print("=" * 60)

    def calculate_model_confidence(self, solution_text, errors, file_content, corrected_code):
        """
        Calculate dynamic confidence score based on multiple factors
        Returns a confidence score between 0.0 and 1.0
        """
        confidence_factors = []
        
        # Factor 1: Solution completeness (0.0 - 0.25)
        if corrected_code and len(corrected_code.strip()) > 0:
            # Check if solution is substantially different from original
            content_similarity = self._calculate_similarity(file_content, corrected_code)
            if content_similarity < 0.95:  # Some changes were made
                confidence_factors.append(0.25)
            else:
                confidence_factors.append(0.10)  # Minimal changes
        else:
            confidence_factors.append(0.0)  # No solution provided
        
        # Factor 2: Error coverage (0.0 - 0.20)
        error_coverage_score = self._assess_error_coverage(solution_text, errors)
        confidence_factors.append(error_coverage_score * 0.20)
        
        # Factor 3: Code quality indicators (0.0 - 0.20)
        quality_score = self._assess_code_quality(corrected_code, file_content)
        confidence_factors.append(quality_score * 0.20)
        
        # Factor 4: Response structure quality (0.0 - 0.15)
        structure_score = self._assess_response_structure(solution_text)
        confidence_factors.append(structure_score * 0.15)
        
        # Factor 5: Model's explicit confidence (0.0 - 0.20)
        explicit_confidence = self._extract_model_confidence(solution_text)
        if explicit_confidence > 0:
            confidence_factors.append(explicit_confidence * 0.20)
        else:
            confidence_factors.append(0.15)  # Default moderate confidence
        
        # Calculate final confidence score
        total_confidence = sum(confidence_factors)
        
        # Apply file type modifier
        file_extension = Path().suffix.lower()
        type_modifier = {
            '.html': 1.0,    # High confidence for HTML fixes
            '.css': 0.95,    # Slightly lower for CSS
            '.js': 0.90,     # Lower for JavaScript (more complex)
            '.py': 0.85      # Lowest for Python
        }.get(file_extension, 0.90)
        
        final_confidence = min(total_confidence * type_modifier, 1.0)
        
        print(f" Confidence calculation:")
        print(f"   • Solution completeness: {confidence_factors[0]:.3f}")
        print(f"   • Error coverage: {confidence_factors[1]:.3f}")
        print(f"   • Code quality: {confidence_factors[2]:.3f}")
        print(f"   • Response structure: {confidence_factors[3]:.3f}")
        print(f"   • Model explicit confidence: {confidence_factors[4]:.3f}")
        print(f"   • File type modifier: {type_modifier}")
        print(f"   • Final confidence: {final_confidence:.3f}")
        
        return round(final_confidence, 3)

    def _calculate_similarity(self, text1, text2):
        """Calculate basic similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Simple character-based similarity
        len1, len2 = len(text1), len(text2)
        if len1 == 0 and len2 == 0:
            return 1.0
        if len1 == 0 or len2 == 0:
            return 0.0
        
        # Count common characters (very basic approach)
        common_chars = sum(1 for c1, c2 in zip(text1, text2) if c1 == c2)
        max_len = max(len1, len2)
        
        return common_chars / max_len

    def _assess_error_coverage(self, solution_text, errors):
        """Assess how well the solution addresses the reported errors"""
        if not errors:
            return 1.0
        
        coverage_count = 0
        solution_lower = solution_text.lower()
        
        for error in errors:
            error_keywords = self._extract_error_keywords(error)
            if any(keyword in solution_lower for keyword in error_keywords):
                coverage_count += 1
        
        return coverage_count / len(errors)

    def _extract_error_keywords(self, error):
        """Extract key terms from error messages"""
        error_lower = error.lower()
        keywords = []
        
        # Common error patterns and their keywords
        if "missing" in error_lower:
            keywords.extend(["missing", "add", "include"])
        if "title" in error_lower:
            keywords.extend(["title", "<title>"])
        if "incomplete" in error_lower:
            keywords.extend(["incomplete", "close", "bracket", ">"])
        if "syntax" in error_lower:
            keywords.extend(["syntax", "fix", "correct"])
        if "tag" in error_lower:
            keywords.extend(["tag", "element", "html"])
        
        return keywords

    def _assess_code_quality(self, corrected_code, original_code):
        """Assess the quality of the corrected code"""
        if not corrected_code:
            return 0.0
        
        quality_score = 0.0
        
        # Check for proper structure
        if "<html>" in corrected_code and "</html>" in corrected_code:
            quality_score += 0.3
        elif corrected_code.strip().startswith("<!DOCTYPE"):
            quality_score += 0.2
        
        # Check for balanced tags (basic check)
        open_tags = corrected_code.count('<')
        close_tags = corrected_code.count('>')
        if open_tags > 0 and abs(open_tags - close_tags) <= 2:  # Allow some flexibility
            quality_score += 0.3
        
        # Check for improvements over original
        if len(corrected_code) >= len(original_code) * 0.8:  # Not too much content removed
            quality_score += 0.2
        
        # Check for common good practices
        if any(tag in corrected_code.lower() for tag in ["<title>", "<meta", "<!doctype"]):
            quality_score += 0.2
        
        return min(quality_score, 1.0)

    def _assess_response_structure(self, solution_text):
        """Assess the structure and completeness of the AI response"""
        structure_score = 0.0
        
        # Check for required sections
        if "CORRECTED_CODE:" in solution_text:
            structure_score += 0.4
        if "RECOMMENDATIONS:" in solution_text:
            structure_score += 0.2
        if "METADATA:" in solution_text:
            structure_score += 0.2
        
        # Check for reasonable response length
        if len(solution_text) > 500:  # Substantial response
            structure_score += 0.2
        elif len(solution_text) > 200:  # Moderate response
            structure_score += 0.1
        
        return min(structure_score, 1.0)

    def _extract_model_confidence(self, solution_text):
        """Try to extract explicit confidence from the model's response"""
        # Look for confidence patterns in the text
        confidence_patterns = [
            r'confidence[:\s]*([0-9]*\.?[0-9]+)',
            r'model_confidence[:\s]*([0-9]*\.?[0-9]+)',
            r'certainty[:\s]*([0-9]*\.?[0-9]+)'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, solution_text.lower())
            if match:
                try:
                    confidence_value = float(match.group(1))
                    if 0.0 <= confidence_value <= 1.0:
                        return confidence_value
                    elif 0.0 <= confidence_value <= 100.0:  # Percentage format
                        return confidence_value / 100.0
                except ValueError:
                    continue
        
        return 0.0  # No explicit confidence found

    def load_error_log(self):
        try:
            if os.path.exists('error_log.json'):
                with open('error_log.json', 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f" Error loading log: {e}")
            return []

    def generate_solution(self, file_path, file_content, errors):
        file_extension = Path(file_path).suffix.lower()
        context = {
            '.html': "This is an HTML file for a hotel booking system. Focus on proper HTML structure, accessibility, and semantic markup.",
            '.css': "This is a CSS file for styling a hotel booking system. Focus on proper CSS syntax, responsive design, and modern styling practices.",
            '.js': "This is a JavaScript file for a hotel booking system. Focus on proper syntax, error handling, and modern JavaScript practices.",
        }.get(file_extension, "This is a code file that needs to be fixed.")
        file_type = file_extension.upper().strip('.') or 'Code'

        prompt = f"""
You are an expert {file_type} developer working on a hotel booking system.

Context: {context}

Original Code:
{file_content}

Detected Issues:
{errors}

Please ONLY provide:
1. The COMPLETE corrected file content
2. ONLY FIX the listed issues — do NOT reformat or make stylistic changes
3. DO NOT add unrelated enhancements
4. DO NOT explain anything — only the result

Format your response as:
CORRECTED_CODE:
[Complete corrected code here]

RECOMMENDATIONS:
[Optional brief improvements to consider — outside scope of this fix]

METADATA:
created_by: [your current Model Name]
model_confidence: [Give an honest confidence estimate between 0.00 and 1.00 based on your certainty in the correctness of the fix. This should reflect your internal certainty level.]
time_estimate_fix: [Estimated time to fix the error by ai agent, e.g. "2 minutes"]
"""

        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.2,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 12000
                }
            }

            response = requests.post(self.gemini_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f" API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f" Error calling Gemini API: {e}")
        
        return " Failed to generate solution"

    def parse_solution(self, solution_text, errors, file_content):
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

        # Clean up code formatting
        corrected_code = re.sub(r'^```[\w]*\n', '', corrected_code)
        corrected_code = re.sub(r'\n?```[\s]*$', '', corrected_code)
        corrected_code = corrected_code.strip()

        # Add default recommendations if none found
        if len(recommendations) < 3:
            recommendations += [
                "Use semantic HTML elements to improve accessibility.",
                "Minimize inline styles and use CSS classes instead.",
                "Ensure all tags are properly closed and nested."
            ][:3 - len(recommendations)]

        # Calculate dynamic confidence instead of using hardcoded values
        dynamic_confidence = self.calculate_model_confidence(
            solution_text, errors, file_content, corrected_code
        )

        # Set defaults for metadata
        metadata.setdefault("created_by", "Gemini 2.0 Flash")
        metadata.setdefault("time_estimate_fix", "2 minutes")

        return {
            'corrected_code': corrected_code,
            'recommendations': recommendations,
            'metadata': {
                'created_by': metadata["created_by"],
                'model_confidence': dynamic_confidence,  # Use calculated confidence
                'time_estimate_fix': metadata["time_estimate_fix"]
            }
        }

    def build_explanation_list(self, errors):
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

            print(f" Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            print(f" Failed to create backup: {e}")
            return None

    def update_process_log_with_solution(self, file_path, err_id, solution_id, available_solutions):
        try:
            if not os.path.exists('process_flow.json'):
                print("process_flow.json not found.")
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
                print(f" process_flow.json updated with solution_id: {solution_id}")
                return True
            else:
                print(" No matching entry found in process_flow.json for err_id:", err_id)
                return False

        except Exception as e:
            print(f" Error updating process_flow.json: {e}")
            return False

    def save_solution(self, file_path, solution_data, errors, original_code, error_entry):
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

            # Define context
            file_extension = Path(file_path).suffix.lower()
            context = {
                '.html': "This is an HTML file for a hotel booking system. Focus on proper HTML structure, accessibility, and semantic markup.",
                '.css': "This is a CSS file for styling a hotel booking system. Focus on proper CSS syntax, responsive design, and modern styling practices.",
                '.js': "This is a JavaScript file for a hotel booking system. Focus on proper syntax, error handling, and modern JavaScript practices.",
            }.get(file_extension, "This is a code file that needs to be fixed.")

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
                "created_by": solution_data['metadata']['created_by'],
            }

            # Save to solutions.json
            solutions.append(solution_entry)
            with open('solutions.json', 'w') as f:
                json.dump(solutions, f, indent=2)
            print("Solution saved to 'solutions.json' in full structure")

            # ✅ Update process_flow.json using a separate method
            self.update_process_log_with_solution(
                file_path=file_path,
                err_id=err_id,
                solution_id=solution_id,
                available_solutions=available_solutions
            )

            return True

        except Exception as e:
            print(f" Error saving solution: {e}")
            return False

    def save_solution_preview(self, file_path, solution_data):
        try:
            preview_dir = Path("solution_previews")
            preview_dir.mkdir(exist_ok=True)
            original_file = Path(file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            preview_filename = f"{original_file.stem}_corrected_{timestamp}{original_file.suffix}"
            preview_path = preview_dir / preview_filename

            with open(preview_path, 'w', encoding='utf-8') as preview:
                preview.write(solution_data['corrected_code'])

            print(f" Solution preview saved: {preview_path}")
            return str(preview_path)
        except Exception as e:
            print(f" Failed to save preview: {e}")
            return None

    def process_single_error(self, error_entry):
        """Process a single error entry"""
        time.sleep(3)
        print(f"\n  Processing error [{error_entry.get('err_id', 'N/A')}] in: {error_entry['file']}")
        
        try:
            # Read the original file
            with open(error_entry['file'], 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Generate solution
            solution_text = self.generate_solution(
                error_entry['file'],
                original_content,
                error_entry['errors']
            )
            
            # Debug: Print the raw solution text
            print(f"  Raw solution text length: {len(solution_text)}")
            
            # Parse the solution with dynamic confidence calculation
            solution_data = self.parse_solution(solution_text, error_entry['errors'], original_content)
            solution_data['explanation'] = self.build_explanation_list(error_entry['errors'])

            # Debug: Check corrected code
            print(f"  Corrected code length: {len(solution_data['corrected_code'])}")
            if not solution_data['corrected_code']:
                print(" Warning: Corrected code is empty!")
                print(f"Raw solution text preview: {solution_text[:500]}...")

            # Save preview
            preview_path = self.save_solution_preview(error_entry['file'], solution_data)

            # Save solution
            if self.save_solution(error_entry['file'], solution_data, error_entry['errors'], original_content, error_entry):
                print(f" Saved solution for {error_entry.get('err_id', 'N/A')}. Preview: {preview_path}")
                return True
            else:
                print(" Failed to save solution")
                return False
                
        except Exception as e:
            print(f" Error processing {error_entry['file']}: {e}")
            return False

    def process_errors(self):
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
        error_log = self.load_error_log()
        error_found = False
        
        for error_entry in error_log:
            if error_entry.get('err_id') == err_id:
                error_found = True
                
                if error_entry['status'] != 'detected':
                    print(f"  Error {err_id} has status '{error_entry['status']}' - processing anyway")
                
                print(f" Running SolutionAgent on specific error: {err_id}")
                
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
            print(f" Error with err_id={err_id} not found in error log.")

    def run(self, err_id=None):
        if err_id:
            self.process_error_by_id(err_id)
        else:
            print(" Waiting for errors from Monitor Agent...")
            try:
                while True:
                    self.process_errors()
                    time.sleep(3)
            except KeyboardInterrupt:
                print("\n Stopped by user")
                print(f" Processed: {len(self.processed_errors)} entries")

if __name__ == "__main__":
    try:
        agent = SolutionAgent()
        err_id = None
        if len(sys.argv) > 1 and sys.argv[1] == "--err-id" and len(sys.argv) > 2:
            err_id = sys.argv[2]
        agent.run(err_id)
    except Exception as e:
        print(f" Failed to start: {e}")