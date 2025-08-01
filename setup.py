#!/usr/bin/env python3
"""
ScamSimAI - Automated Setup Script (Python)
This script automates the setup process for the ScamSimAI project.
Works on Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
import platform
import shutil
import json
from pathlib import Path
from typing import List, Tuple, Optional

# Colors for cross-platform output
class Colors:
    if platform.system() == "Windows":
        # Windows ANSI color support (Windows 10+)
        os.system("color")
    
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class SetupManager:
    def __init__(self):
        # Find the actual project root by looking for key files
        current_dir = Path(__file__).parent.absolute()
        self.project_root = self._find_project_root(current_dir)
        self.venv_path = self.project_root / "venv"
        self.system = platform.system().lower()
        
        # Platform-specific settings
        if self.system == "windows":
            self.venv_python = self.venv_path / "Scripts" / "python.exe"
            self.venv_pip = self.venv_path / "Scripts" / "pip.exe"
            self.venv_activate = self.venv_path / "Scripts" / "activate.bat"
        else:
            self.venv_python = self.venv_path / "bin" / "python"
            self.venv_pip = self.venv_path / "bin" / "pip"
            self.venv_activate = self.venv_path / "bin" / "activate"
    
    def _find_project_root(self, start_path: Path) -> Path:
        """Find the project root by looking for key files/directories"""
        current = start_path
        max_depth = 5  # Prevent infinite loops
        
        for _ in range(max_depth):
            # Check if this looks like the project root
            if (current / "frontend").exists() and (current / "server").exists():
                return current
            # Also check for package.json in case we're in the frontend dir
            elif (current / "package.json").exists() and (current.parent / "server").exists():
                return current.parent
            # Check for setup files
            elif any((current / f).exists() for f in ["setup.py", "requirements.txt", "README.md"]):
                # Verify this is the right setup.py by checking for frontend/server dirs
                if (current / "frontend").exists() or (current / "server").exists():
                    return current
            
            # Move up one level
            parent = current.parent
            if parent == current:  # We've reached the root
                break
            current = parent
        
        # Fallback to the original directory
        return start_path
    
    def print_step(self, step: int, message: str):
        """Print a step header"""
        print(f"\n{Colors.BLUE}📋 Step {step}: {message}{Colors.RESET}")
        print()
    
    def print_success(self, message: str):
        """Print a success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")
    
    def print_warning(self, message: str):
        """Print a warning message"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")
    
    def print_error(self, message: str):
        """Print an error message"""
        print(f"{Colors.RED}❌ {message}{Colors.RESET}")
    
    def print_info(self, message: str):
        """Print an info message"""
        print(f"{Colors.CYAN}💡 {message}{Colors.RESET}")
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None, 
                   capture_output: bool = True, check: bool = True) -> subprocess.CompletedProcess:
        """Run a command safely"""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=capture_output,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            if not capture_output:
                raise
            self.print_error(f"Command failed: {' '.join(command)}")
            if e.stdout:
                print(f"stdout: {e.stdout}")
            if e.stderr:
                print(f"stderr: {e.stderr}")
            raise
    
    def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH"""
        return shutil.which(command) is not None
    
    def get_version(self, command: List[str]) -> Optional[str]:
        """Get version of a command"""
        try:
            result = self.run_command(command, check=False)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Check if Python version meets requirements"""
        try:
            version_info = sys.version_info
            version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
            
            if version_info.major == 3 and version_info.minor >= 11:
                return True, version_str
            else:
                return False, version_str
        except Exception:
            return False, "unknown"
    
    def _get_npm_command(self) -> List[str]:
        """Get the correct npm command for the current platform"""
        if self.system == "windows":
            # On Windows, npm might be a PowerShell script, batch file, or executable
            # Try different approaches
            
            # First, check if npm.cmd exists (preferred on Windows)
            if shutil.which("npm.cmd"):
                return ["npm.cmd"]
            
            # Then check for npm.bat
            if shutil.which("npm.bat"):
                return ["npm.bat"]
            
            # Check for npm.exe
            if shutil.which("npm.exe"):
                return ["npm.exe"]
            
            # For PowerShell scripts, we need to use powershell to execute them
            if shutil.which("npm"):
                # This might be a PowerShell script, so use cmd /c to execute it
                return ["cmd", "/c", "npm"]
            
            # Fallback
            return ["npm"]
        else:
            return ["npm"]
    
    def check_system_requirements(self):
        """Check all system requirements"""
        self.print_step(1, "Checking System Requirements")
        
        all_good = True
        
        # Check Python
        python_ok, python_version = self.check_python_version()
        if python_ok:
            self.print_success(f"Python found: {python_version}")
        else:
            self.print_error(f"Python 3.11+ required. Found: {python_version}")
            self.print_info("Download from: https://www.python.org/downloads/")
            all_good = False
        
        # Check Node.js
        if self.check_command_exists("node"):
            node_version = self.get_version(["node", "--version"])
            if node_version:
                self.print_success(f"Node.js found: {node_version}")
            else:
                self.print_warning("Node.js found but version check failed")
        else:
            self.print_error("Node.js 18+ required but not found")
            self.print_info("Download from: https://nodejs.org/")
            all_good = False
        
        # Check npm
        npm_cmd = self._get_npm_command()
        if self.check_command_exists(npm_cmd[0]):
            npm_version = self.get_version(npm_cmd + ["--version"])
            if npm_version:
                self.print_success(f"npm found: {npm_version}")
            else:
                self.print_warning("npm found but version check failed")
        else:
            self.print_error("npm required but not found")
            self.print_info("npm is usually installed with Node.js")
            all_good = False
        
        if not all_good:
            print(f"\n{Colors.RED}❌ System requirements not met. Please install missing components.{Colors.RESET}")
            sys.exit(1)
    
    def setup_virtual_environment(self):
        """Set up Python virtual environment"""
        self.print_step(2, "Setting up Python Virtual Environment")
        
        # Create virtual environment
        if not self.venv_path.exists():
            print("Creating Python virtual environment...")
            self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])
            self.print_success("Virtual environment created")
        else:
            self.print_warning("Virtual environment already exists, skipping creation")
        
        # Verify virtual environment
        if not self.venv_python.exists():
            self.print_error("Virtual environment Python not found")
            sys.exit(1)
        
        self.print_success("Virtual environment ready")
        
        # Upgrade pip
        print("Upgrading pip...")
        try:
            self.run_command([str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip"])
            self.print_success("pip upgraded")
        except subprocess.CalledProcessError:
            self.print_warning("pip upgrade failed, continuing anyway")
    
    def _install_with_live_output(self, command: List[str], description: str, cwd: Optional[Path] = None) -> bool:
        """Install packages with live output streaming"""
        print(f"{Colors.CYAN}📦 {description}{Colors.RESET}")
        try:
            # Use Popen for real-time output streaming
            process = subprocess.Popen(
                command, 
                cwd=cwd or self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output in real-time
            if process.stdout:
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output.strip():
                        line = output.strip()
                        # Color code different types of output
                        if any(keyword in line for keyword in ["Collecting", "Found existing installation"]):
                            print(f"{Colors.BLUE}🔍 {line}{Colors.RESET}")
                        elif any(keyword in line for keyword in ["Downloading", "%", "progress"]):
                            print(f"{Colors.CYAN}⬇️  {line}{Colors.RESET}")
                        elif any(keyword in line for keyword in ["Installing", "added", "packages"]):
                            print(f"{Colors.GREEN}📦 {line}{Colors.RESET}")
                        elif any(keyword in line for keyword in ["Successfully installed", "up to date"]):
                            print(f"{Colors.GREEN}✅ {line}{Colors.RESET}")
                        elif any(keyword in line.lower() for keyword in ["error", "failed", "warn"]):
                            print(f"{Colors.RED}❌ {line}{Colors.RESET}")
                        elif "Requirement already satisfied" in line:
                            print(f"{Colors.YELLOW}✓ {line}{Colors.RESET}")
                        else:
                            print(f"   {line}")
            
            # Wait for process to complete and get return code
            process.wait()
            return process.returncode == 0
                    
        except Exception as e:
            print(f"{Colors.RED}❌ Live output failed: {e}{Colors.RESET}")
            return False

    def install_python_dependencies(self):
        """Install Python dependencies"""
        self.print_step(3, "Installing Python Dependencies")
        
        # Try requirements.txt first
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            print("Installing dependencies from requirements.txt...")
            print(f"{Colors.YELLOW}   (This may take a few minutes, especially for torch/transformers){Colors.RESET}")
            
            success = self._install_with_live_output([
                str(self.venv_pip), "install", "-r", str(requirements_file), 
                "--progress-bar", "on"
            ], "Running: pip install -r requirements.txt")
            
            if success:
                self.print_success("Python dependencies installed from requirements.txt")
                return
            else:
                self.print_warning("Failed to install from requirements.txt, trying individual packages")
        
        # Fallback to individual packages
        packages = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0", 
            "pydantic>=2.5.0",
            "python-dotenv>=1.0.0",
            "transformers>=4.35.0",
            "torch>=2.1.0",
            "requests>=2.31.0",
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.10.0",
            "isort>=5.12.0",
            "flake8>=6.1.0"
        ]
        
        print("Installing Python packages individually...")
        for i, package in enumerate(packages, 1):
            print(f"{Colors.BLUE}[{i}/{len(packages)}] Installing {package}...{Colors.RESET}")
            success = self._install_with_live_output([
                str(self.venv_pip), "install", package, "--progress-bar", "on"
            ], f"Installing {package}")
            
            if success:
                print(f"{Colors.GREEN}  ✓ {package} installed successfully{Colors.RESET}")
            else:
                print(f"{Colors.RED}  ✗ Failed to install {package}{Colors.RESET}")
        
        self.print_success("Python dependencies installation completed")
    
    def setup_frontend_dependencies(self):
        """Set up frontend dependencies"""
        self.print_step(4, "Setting up Frontend Dependencies")
        
        frontend_path = self.project_root / "frontend"
        
        if not frontend_path.exists():
            self.print_error(f"Frontend directory not found at: {frontend_path}")
            return
        
        # Check if package.json exists
        package_json = frontend_path / "package.json"
        if not package_json.exists():
            self.print_error(f"package.json not found at: {package_json}")
            # List what's actually in the directory for debugging
            try:
                files = [f.name for f in frontend_path.iterdir() if f.is_file()]
                print(f"{Colors.YELLOW}📁 Files found: {files[:10]}{'...' if len(files) > 10 else ''}{Colors.RESET}")
            except Exception:
                pass
            return
        
        # Get the correct npm command
        npm_cmd = self._get_npm_command()
        print(f"{Colors.CYAN}🔍 Using npm command: {' '.join(npm_cmd)}{Colors.RESET}")
        
        print("Installing Node.js dependencies...")
        print(f"{Colors.CYAN}📂 Working in: {frontend_path}{Colors.RESET}")
        
        # Try with live output first
        success = self._install_with_live_output(
            npm_cmd + ["install"], 
            "Running: npm install", 
            cwd=frontend_path
        )
        
        # If live output fails, try with regular command execution
        if not success:
            print(f"{Colors.YELLOW}⚠️ Live output failed, trying standard npm install...{Colors.RESET}")
            try:
                self.run_command(npm_cmd + ["install"], cwd=frontend_path, capture_output=False)
                self.print_success("Frontend dependencies installed")
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to install frontend dependencies: {e}")
                self.print_info("Try running 'npm install' manually in the frontend directory")
                # Additional troubleshooting info
                print(f"{Colors.YELLOW}💡 Troubleshooting:{Colors.RESET}")
                print("   • Make sure Node.js is installed: https://nodejs.org/")
                print("   • Restart your terminal/command prompt after installing Node.js")
                print("   • Check if npm is in PATH: run 'npm --version' manually")
                sys.exit(1)
        else:
            self.print_success("Frontend dependencies installed")
    
    def setup_environment_files(self):
        """Set up environment configuration files"""
        self.print_step(5, "Setting up Environment Files")
        
        # Server environment file
        server_env = self.project_root / "server" / ".env"
        server_env_example = self.project_root / "server" / ".env.example"
        
        if not server_env.exists() and server_env_example.exists():
            print("Creating server/.env file from template...")
            shutil.copy2(server_env_example, server_env)
            self.print_success("Server .env file created")
        elif server_env.exists():
            self.print_warning("Server .env file already exists, skipping")
        else:
            self.print_error("Server .env.example not found")
        
        # Frontend environment file
        frontend_env = self.project_root / "frontend" / ".env.local"
        frontend_env_example = self.project_root / "frontend" / ".env.local.example"
        
        if not frontend_env.exists() and frontend_env_example.exists():
            print("Creating frontend/.env.local file from template...")
            shutil.copy2(frontend_env_example, frontend_env)
            self.print_success("Frontend .env.local file created")
        elif frontend_env.exists():
            self.print_warning("Frontend .env.local file already exists, skipping")
        else:
            self.print_error("Frontend .env.local.example not found")
    
    def test_installation(self):
        """Test the installation"""
        self.print_step(6, "Testing Installation")
        
        # Test server dependencies
        print("Testing server dependencies...")
        try:
            test_code = "import fastapi, uvicorn, pydantic; print('Server dependencies OK')"
            result = self.run_command([str(self.venv_python), "-c", test_code])
            if "Server dependencies OK" in result.stdout:
                self.print_success("Server dependencies working")
            else:
                self.print_warning("Server dependencies test unclear")
        except subprocess.CalledProcessError:
            self.print_error("Server dependencies test failed")
        
        # Test frontend build
        print("Testing frontend build...")
        try:
            frontend_path = self.project_root / "frontend"
            npm_cmd = self._get_npm_command()
            result = self.run_command(npm_cmd + ["run", "build"], cwd=frontend_path)
            self.print_success("Frontend build test passed")
        except subprocess.CalledProcessError:
            self.print_error("Frontend build test failed")
            self.print_info("Check the console output above for specific errors")
    
    def print_completion_message(self):
        """Print setup completion message"""
        self.print_step(7, "Setup Complete!")
        
        print(f"{Colors.GREEN}🎉 Setup completed successfully!{Colors.RESET}\n")
        
        print(f"{Colors.YELLOW}📋 Next Steps:{Colors.RESET}\n")
        
        print(f"{Colors.YELLOW}1. Configure API Keys:{Colors.RESET}")
        print("   📝 Get your Hugging Face tokens:")
        print("      • Visit: https://huggingface.co/settings/tokens")
        print("      • Create a new token with read access")
        print("      • Copy the token\n")
        
        print("   📝 Update server/.env file:")
        print("      • Set HF_TOKEN_PRED=your-huggingface-token")
        print("      • Set HF_TOKEN_GEN=your-huggingface-token")
        print("      • Set API_KEY=your-secure-api-key-here\n")
        
        print("   📝 Update frontend/.env.local file:")
        print("      • Set NEXT_PUBLIC_API_KEY=your-secure-api-key-here")
        print("      • (Must match the API_KEY in server/.env)\n")
        
        print(f"{Colors.YELLOW}2. Start the Application:{Colors.RESET}")
        print("   📝 Terminal 1 - Start the server:")
        if self.system == "windows":
            print("      cd server")
            print("      ..\\venv\\Scripts\\activate.bat")
            print("      python server.py\n")
        else:
            print("      cd server")
            print("      source ../venv/bin/activate")
            print("      python server.py\n")
        
        print("   📝 Terminal 2 - Start the frontend:")
        print("      cd frontend")
        print("      npm run dev\n")
        
        print(f"{Colors.YELLOW}3. Access the Application:{Colors.RESET}")
        print("   🌐 Frontend: http://localhost:3000")
        print("   🔧 API Docs: http://localhost:8000/docs")
        print("   💚 Health Check: http://localhost:8000/api/health\n")
        
        print(f"{Colors.YELLOW}4. Development:{Colors.RESET}")
        print("   📚 Read the documentation:")
        print("      • README.md - Project overview")
        print("      • DEVELOPER_GUIDE.md - Development guide")
        print("      • server/README.md - Server documentation")
        print("      • frontend/README.md - Frontend documentation\n")
        
        print(f"{Colors.CYAN}💡 Tips:{Colors.RESET}")
        if self.system == "windows":
            print("   • Always activate the virtual environment: venv\\Scripts\\activate.bat")
        else:
            print("   • Always activate the virtual environment: source venv/bin/activate")
        print("   • Check the logs if something doesn't work")
        print("   • Environment variables require server restart to take effect")
        print("   • Use 'deactivate' to exit the virtual environment\n")
        
        print(f"{Colors.GREEN}🚀 Happy coding!{Colors.RESET}")
    
    def run_setup(self):
        """Run the complete setup process"""
        print(f"{Colors.MAGENTA}🚀 ScamSimAI - Automated Setup{Colors.RESET}")
        print(f"{Colors.MAGENTA}=============================={Colors.RESET}")
        
        try:
            self.check_system_requirements()
            self.setup_virtual_environment()
            self.install_python_dependencies()
            self.setup_frontend_dependencies()
            self.setup_environment_files()
            self.test_installation()
            self.print_completion_message()
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️ Setup interrupted by user{Colors.RESET}")
            sys.exit(1)
        except Exception as e:
            print(f"\n{Colors.RED}❌ Setup failed with error: {e}{Colors.RESET}")
            sys.exit(1)

def main():
    """Main entry point"""
    # Change to script directory
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Create and run setup manager
    setup_manager = SetupManager()
    setup_manager.run_setup()

if __name__ == "__main__":
    main()
