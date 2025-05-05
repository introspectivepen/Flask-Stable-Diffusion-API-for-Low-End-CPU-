Optimized Flask Stable Diffusion API for Low-End CPU
Overview
This project provides a Flask-based web API for generating images using the Stable Diffusion model (CompVis/stable-diffusion-v1-4), specifically optimized for low-end CPU systems, such as an 8GB RAM laptop. The application focuses on memory efficiency and performance, making it feasible for resource-constrained hardware. Key optimizations include CPU-only configuration, reduced inference steps, memory-saving techniques, and detailed logging for debugging.
Features

CPU-Only Support: Configured to run on CPU with torch.float32 for stability.
Memory Optimizations: Uses low_cpu_mem_usage=True and enable_attention_slicing() to minimize memory usage.
Reduced Inference Steps: Lowers steps to 25 for faster generation on low-end hardware.
Prompt Limit: Caps prompts at 200 characters to ensure stability.
Logging: Implements custom logging with the logging module for runtime feedback.
Image Quality: Reduces PNG quality to 85 to save memory.
Health Check: Enhanced /health endpoint with model details and optimization status.
Error Handling: Provides actionable error messages (e.g., "Try a shorter prompt").

System Requirements

Hardware:
Minimum: 8GB RAM CPU laptop (e.g., Intel i5, AMD Ryzen quad-core).
Swap Space: 4-8GB recommended (on SSD) to handle memory overflows.


Operating System:
Windows, Linux, or macOS (lightweight distros like Lubuntu recommended for Linux).


Software:
Python 3.8+
Dependencies: Flask, flask-cors, PIL, torch, diffusers, waitress (optional), logging.
Hugging Face Authentication Token (HF_AUTH_TOKEN) via environment variable or authtoken.py.



Setup Instructions
1. Clone the Repository
git clone https://github.com/yourusername/flask-stable-diffusion.git
cd flask-stable-diffusion

2. Install Dependencies
Create a virtual environment and install the required packages:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask flask-cors pillow torch diffusers waitress

3. Configure Hugging Face Token
Set your Hugging Face authentication token:

Option 1: Environment Variableexport HF_AUTH_TOKEN="your-huggingface-token"  # On Windows: set HF_AUTH_TOKEN=your-huggingface-token


Option 2: authtoken.pyCreate a file named authtoken.py in the project root:HF_AUTH_TOKEN = "your-huggingface-token"



4. Set Up Swap Space (Recommended for 8GB RAM)
To handle memory overflows:

Linux:sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile


Windows: Increase virtual memory in System Settings (Control Panel > System > Advanced System Settings > Performance Settings > Advanced > Virtual Memory).
macOS: Ensure free disk space for automatic swap (at least 4GB).

5. Run the Application
Start the Flask server:
python app.py


The server runs on http://localhost:5000 by default.
Uses waitress for production if available; falls back to Flask’s development server with debug=False.

Usage
API Endpoints

Root (/):

Serves index.html (assumes a frontend interface; not provided by default).
Access: http://localhost:5000/


Health Check (/health):

Returns server status, device, model, and optimizations.
Example Request:curl http://localhost:5000/health


Example Response:{
  "status": "healthy",
  "device": "cpu",
  "model": "CompVis/stable-diffusion-v1-4",
  "optimizations": {
    "attention_slicing": true,
    "low_memory": true
  }
}




Generate Image (/generate, POST):

Generates a 512x512 image from a text prompt.
Input: JSON payload with a prompt field (max 200 characters).
Example Request:curl -X POST -H "Content-Type: application/json" -d '{"prompt": "a cat"}' http://localhost:5000/generate --output cat.png


Example Response: PNG image file.
Error Responses:
400: Invalid JSON, empty prompt, or prompt > 200 characters.
500: Generation failure with actionable advice (e.g., "Try a shorter prompt").





Performance on 8GB RAM CPU Laptop

Model Loading:
Time: 5-10 minutes.
Memory: 4-5GB with optimizations.


Image Generation:
Time: 2-8 minutes per 512x512 image (25 inference steps, quad-core CPU).
Memory: 5-6GB (swap space may be used).


Feasibility:
Suitable for occasional use (e.g., a few images).
Swap space (4-8GB) recommended to avoid crashes.
Generation may take 8-15 minutes on older/dual-core CPUs.



Optimizations for Low-End Hardware

CPU-Only: Uses DEVICE="cpu" and torch.float32 for stability.
Memory Savings:
low_cpu_mem_usage=True: Reduces memory during model loading.
enable_attention_slicing(): Lowers memory usage during inference.


Reduced Load:
Inference steps lowered to 25 (from 50).
Prompt length capped at 200 characters.
PNG quality reduced to 85.


Logging: Detailed logs for debugging (model loading, generation, server events).

Potential Improvements

Frontend Interface:
Add an index.html with a form for prompt input and image display.
Example: HTML form with JavaScript to send POST requests to /generate.


Rate Limiting:
Use Flask-Limiter to prevent CPU overload from multiple requests.
Install: pip install Flask-Limiter.


Security:
Re-enable safety_checker or add custom content filtering.
Restrict CORS to specific origins in production.
Secure HF_AUTH_TOKEN storage (use environment variable, not authtoken.py).


Further Memory Reduction:
Use a smaller model (e.g., runwayml/stable-diffusion-v1-5).
Lower image resolution to 256x256:image = pipe(prompt, guidance_scale=7.5, num_inference_steps=25, height=256, width=256).images[0]




Performance Monitoring:
Add generation time logging:import time
start_time = time.time()
image = pipe(...)
logger.info(f"Image generated in {round(time.time() - start_time, 2)} seconds")





Security Considerations

CORS: Globally enabled; restrict to trusted origins in production.
Auth Token: Securely manage HF_AUTH_TOKEN to prevent leaks.
Safety Checker: Disabled by default; re-enable for public use to filter inappropriate content.
Prompt Handling: 200-character limit reduces risks, but consider adding sanitization.

Recommendations for 8GB RAM CPU Laptop

Setup Swap Space: Configure 4-8GB swap on an SSD.
Close Background Processes: Free up RAM by closing other apps.
Use Lightweight OS: Use a lightweight Linux distro (e.g., Lubuntu) to reduce OS memory usage.
Test Incrementally:
Start the server and monitor memory usage.
Test with short prompts (e.g., curl -X POST -H "Content-Type: application/json" -d '{"prompt": "a cat"}' http://localhost:5000/generate).


Monitor Performance:
Check logs for slow operations or errors.
If generation exceeds 10 minutes, lower inference steps to 20 or resolution to 256x256.



Deployment Recommendations

Low-End Hardware: Suitable for testing or occasional use on an 8GB RAM CPU laptop (expect 2-8 minutes per image).
Production: Use a server with 16GB RAM for better performance.
Monitoring: Use /health endpoint and logs to monitor uptime and performance.
Scaling: Avoid heavy traffic on low-end hardware; use load balancing for production.

Conclusion
This Flask Stable Diffusion API is optimized for low-end CPU systems, making it feasible for an 8GB RAM laptop with swap space. It can generate images in 2-8 minutes, though performance varies with CPU and memory conditions. For frequent or production use, a 16GB RAM system or cloud deployment is recommended.
