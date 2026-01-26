#!/usr/bin/env python3
"""
Copy formatted content to clipboard as HTML for Substack
Ensures proper formatting when pasted into Substack editor
"""

import sys
import subprocess
import tempfile
import os

def copy_html_to_clipboard(html_content):
    """
    Copy HTML content to clipboard as text/html format
    This ensures Substack editor recognizes and preserves formatting
    """
    try:
        # Check if required tools are available
        if not check_dependencies():
            return False
        
        # Write HTML to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            # Copy HTML to clipboard with correct MIME type
            cmd = f'cat "{temp_file}" | xclip -selection clipboard -t text/html'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Formatted content copied to clipboard as HTML")
                print("📋 Ready to paste into Substack editor")
                print("💡 Bold/italic/headers will be preserved automatically")
                return True
            else:
                print(f"❌ Error copying to clipboard: {result.stderr}")
                return False
                
        finally:
            # Clean up temporary file
            os.unlink(temp_file)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_dependencies():
    """Check if required tools are installed"""
    try:
        # Check for xclip
        subprocess.run(['which', 'xclip'], capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ xclip not found. Install with:")
        print("   Ubuntu/Debian: sudo apt install xclip")
        print("   Arch: sudo pacman -S xclip")
        print("   macOS: Use pbcopy instead (different implementation needed)")
        return False

def copy_with_pandoc(markdown_content):
    """
    Alternative method using pandoc to convert markdown to HTML
    Then copy as text/html
    """
    try:
        # Check if pandoc is available
        subprocess.run(['which', 'pandoc'], capture_output=True, check=True)
        
        # Convert markdown to HTML using pandoc
        pandoc_cmd = ['pandoc', '-f', 'markdown', '-t', 'html']
        pandoc_result = subprocess.run(pandoc_cmd, input=markdown_content, 
                                     capture_output=True, text=True)
        
        if pandoc_result.returncode != 0:
            print(f"❌ Pandoc error: {pandoc_result.stderr}")
            return False
        
        html_content = pandoc_result.stdout
        
        # Copy HTML to clipboard
        xclip_cmd = ['xclip', '-selection', 'clipboard', '-t', 'text/html']
        xclip_result = subprocess.run(xclip_cmd, input=html_content, 
                                    capture_output=True, text=True)
        
        if xclip_result.returncode == 0:
            print("✅ Markdown converted to HTML and copied to clipboard")
            print("📋 Ready to paste into Substack editor")
            return True
        else:
            print(f"❌ Error copying to clipboard: {xclip_result.stderr}")
            return False
            
    except subprocess.CalledProcessError:
        print("❌ pandoc not found. Install with:")
        print("   Ubuntu/Debian: sudo apt install pandoc")
        print("   Arch: sudo pacman -S pandoc") 
        print("   macOS: brew install pandoc")
        return False

def verify_clipboard():
    """Verify what's currently in the clipboard"""
    try:
        result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("\n📄 Current clipboard contents:")
            print("-" * 40)
            print(result.stdout[:500])  # First 500 chars
            if len(result.stdout) > 500:
                print("... (truncated)")
            print("-" * 40)
        else:
            print("❌ Could not read clipboard")
    except Exception as e:
        print(f"❌ Error reading clipboard: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 copy_to_substack.py 'html content' [--verify]")
        print("   or: python3 copy_to_substack.py --markdown 'markdown content'")
        print("\nThis script copies HTML content to clipboard as text/html format")
        print("so that Substack editor preserves formatting when you paste.")
        return
    
    if sys.argv[1] == '--verify':
        verify_clipboard()
        return
    
    if sys.argv[1] == '--markdown' and len(sys.argv) > 2:
        # Use pandoc method for markdown input
        success = copy_with_pandoc(sys.argv[2])
    else:
        # Use direct HTML method
        html_content = sys.argv[1]
        success = copy_html_to_clipboard(html_content)
    
    # Verify clipboard if requested
    if '--verify' in sys.argv:
        verify_clipboard()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Go to Substack editor")
        print("2. Click in the content area") 
        print("3. Paste (Ctrl+V or Cmd+V)")
        print("4. Formatting should be preserved!")
    else:
        print("\n💡 Alternative: Copy the HTML output manually and paste into Substack")

if __name__ == "__main__":
    main()