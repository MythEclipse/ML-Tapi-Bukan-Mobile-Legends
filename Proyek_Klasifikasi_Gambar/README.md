# Proyek Klasifikasi Gambar Pokemon

Proyek ini adalah submission untuk tugas akhir klasifikasi gambar.
Tujuan: Mengklasifikasikan Pokemon Generasi 1 menggunakan CNN.

## Cara Menjalankan di Google Colab

1.  Buka **Google Colab** (https://colab.research.google.com/).
2.  Upload file `notebook.ipynb` ke Colab.
3.  Siapkan file `kaggle.json` dari akun Kaggle Anda (digunakan untuk mendownload dataset).
4.  Jalankan cell secara berurutan.
5.  Saat diminta, upload file `kaggle.json` pada cell yang bersangkutan.

## Struktur Submission

Setelah training selesai di Colab, notebook akan otomatis membuat dan men-zip folder `submission` yang berisi:

- `tfjs_model/`: Model dalam format TensorFlow.js
- `tflite/`: Model dalam format TFLite (beserta label.txt)
- `saved_model/`: Model dalam format SavedModel TensorFlow
- `notebook.ipynb`: Source code training

## Model Architecture

Model menggunakan arsitektur Sequential Convolutional Neural Network (CNN) dengan:

- 4 Layer Conv2D & MaxPooling2D
- Flatten Layer
- Dropout Layer (0.5) untuk mencegah overfitting
- Dense Layer (512 units)
- Output Layer (Softmax)

## Requirements

- tensorflow
- tensorflowjs
- matplotlib
- numpy
- kaggle
