from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
from PIL import Image
from io import BytesIO
import torch
from diffusers import StableDiffusionPipeline
import os
import logging

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for all routes

# Configuration for low-end CPU systems
MODEL_ID = "CompVis/stable-diffusion-v1-4"
DEVICE = "cpu"  # Force CPU usage
TORCH_DTYPE = torch.float32  # Use float32 for CPU stability

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model():
    """Load the model with optimizations for low-end hardware"""
    try:
        logger.info("Loading model... (This may take several minutes)")
        
        # Get auth token - prioritize environment variable
        auth_token = os.getenv('HF_AUTH_TOKEN')
        if not auth_token:
            try:
                from authtoken import auth_token as file_token
                auth_token = file_token
            except ImportError:
                logger.error("Missing auth token! Create authtoken.py or set HF_AUTH_TOKEN")
                raise

        # Model loading with CPU optimizations
        pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            token=auth_token,
            torch_dtype=TORCH_DTYPE,
            use_safetensors=True,
            safety_checker=None,
            low_cpu_mem_usage=True  # Reduces memory usage during loading
        )
        
        # Optimize for CPU
        pipe = pipe.to(DEVICE)
        pipe.enable_attention_slicing()  # Reduces memory usage during generation
        
        logger.info("Model loaded successfully!")
        return pipe
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise

# Load the model (this will take time)
pipe = load_model()

@app.route("/")
def index():
    """Serve the frontend interface"""
    return render_template('index.html')

@app.route("/health")
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "device": DEVICE,
        "model": MODEL_ID,
        "optimizations": ["attention_slicing", "low_memory"]
    })

@app.route("/generate", methods=["POST"])
def generate_image():
    """Generate image from text prompt with CPU optimizations"""
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        if len(prompt) > 200:  # Reduced from 500 for CPU safety
            return jsonify({"error": "Prompt too long (max 200 chars)"}), 400

        logger.info(f"Generating image for prompt: {prompt[:50]}...")
        
        # Generate with reduced steps for CPU
        with torch.no_grad():
            image = pipe(
                prompt,
                guidance_scale=7.5,
                num_inference_steps=25,  # Reduced from 50 for faster CPU generation
                height=512,  # Standard size
                width=512
            ).images[0]

        # Prepare response
        img_io = BytesIO()
        image.save(img_io, format="PNG", quality=85)  # Slightly reduced quality
        img_io.seek(0)

        logger.info("Image generated successfully")
        return send_file(
            img_io,
            mimetype="image/png",
            as_attachment=False,
            download_name="generated_image.png"
        )

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}")
        return jsonify({
            "error": "Image generation failed",
            "details": "Try a shorter prompt or wait a few minutes",
            "device": DEVICE
        }), 500

if __name__ == "__main__":
    logger.info("Starting server...")
    try:
        from waitress import serve
        logger.info("Running production server at http://localhost:5000")
        serve(app, host="0.0.0.0", port=5000)
    except ImportError:
        logger.warning("Waitress not found, using Flask development server")
        app.run(host="0.0.0.0", port=5000, debug=False)  # debug=False for better CPU performance