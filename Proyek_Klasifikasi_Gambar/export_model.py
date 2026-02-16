import os
import logging
import traceback
import subprocess
import tensorflow as tf

# =========================
# LOGGING CONFIG
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logging.info("=== EXPORT STARTED ===")

try:
    # =========================
    # PATH SETUP
    # =========================
    base_dir = os.path.dirname(os.path.abspath(__file__))
    submission_dir = os.path.join(base_dir, "submission")

    model_path = os.path.join(submission_dir, "best_model.keras")
    saved_model_dir = os.path.join(submission_dir, "saved_model")
    tflite_dir = os.path.join(submission_dir, "tflite")
    tfjs_dir = os.path.join(submission_dir, "tfjs")

    os.makedirs(saved_model_dir, exist_ok=True)
    os.makedirs(tflite_dir, exist_ok=True)
    os.makedirs(tfjs_dir, exist_ok=True)

    # =========================
    # LOAD MODEL
    # =========================
    logging.info("Loading model...")
    best_model = tf.keras.models.load_model(model_path, compile=False)
    logging.info("Model loaded successfully")

    # =========================
    # EXPORT SAVEDMODEL
    # =========================
    logging.info("Exporting SavedModel...")
    try:
        tf.saved_model.save(best_model, saved_model_dir)
        logging.info("SavedModel OK")
    except Exception as e:
        logging.warning(f"SavedModel export failed (skipping): {e}")

    # =========================
    # EXPORT TFLITE
    # =========================
    logging.info("Converting to TFLite...")
    converter = tf.lite.TFLiteConverter.from_keras_model(best_model)

    # Enable Flex ops (MobileNetV3 usually needs this)
    converter.target_spec.supported_ops = [
        tf.lite.OpsSet.TFLITE_BUILTINS,
        tf.lite.OpsSet.SELECT_TF_OPS,
    ]

    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    tflite_model = converter.convert()

    tflite_path = os.path.join(tflite_dir, "model.tflite")
    with open(tflite_path, "wb") as f:
        f.write(tflite_model)

    logging.info("TFLite OK")

    # =========================
    # EXPORT TFJS (FROM SAVEDMODEL)
    # =========================
    logging.info("Converting to TFJS (from SavedModel)...")

    cmd = [
        "tensorflowjs_converter",
        "--input_format=tf_saved_model",
        "--output_format=tfjs_graph_model",
        "--signature_name=serving_default",
        "--saved_model_tags=serve",
        saved_model_dir,
        tfjs_dir,
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
    )

    if result.returncode == 0:
        logging.info("TFJS OK")
    else:
        logging.error("TFJS FAILED")
        logging.error(result.stderr)

    logging.info("=== EXPORT COMPLETED ===")

except Exception:
    logging.error("EXPORT FAILED")
    logging.error(traceback.format_exc())
