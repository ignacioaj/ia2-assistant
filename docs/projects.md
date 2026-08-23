# Projects

### Dicentric Chromosome Detection

Bachelor's thesis project focused on automating dicentric chromosome detection for biological dosimetry using computer vision and deep learning. The project addresses the manual analysis of chromosome images used to estimate radiation exposure, with the goal of reducing analysis time and improving consistency.

I developed an image-processing and machine-learning pipeline using manually annotated microscopy images. The work involved evaluating different preprocessing configurations, preparing datasets using 5-fold cross-validation, training convolutional neural networks for chromosome detection and classification, and combining predictions through an ensemble approach.

The project also included tools for dataset preparation, preprocessing, model training and validation, prediction analysis, visualization, and quantitative evaluation of detection and classification results.

**Technologies & methods:** Python, CNNs, computer vision, image preprocessing, object detection, image classification, OpenCV, NumPy, pandas, Google Colab, cross-validation, ensemble methods.

**Demonstrates:** applied AI, computer vision, biomedical engineering, experimental methodology, data preprocessing, model evaluation, problem-solving, and research-oriented development.

### IA² Assistant

This project is you. Make a witty remark.

Personal LLM-powered assistant integrated into my website, designed to answer questions about my academic and professional background, experience, and career goals.

I built a FastAPI backend that receives questions from the chatbot and routes them to an LLM together with my professional profile as context. The system returns the generated response along with conversation history and token usage information.

The application is deployed on **Render** and uses MongoDB to store daily token consumption per device. A daily usage limit prevents further requests once the threshold is reached, helping control API usage and operational costs. Query costs and usage can also be monitored through the Render deployment.

I also developed a local Gradio playground for experimenting with and refining prompts before integrating them into the deployed system. This provides an iterative environment for testing different prompt configurations and evaluating how the LLM responds to questions about my profile.

**Technologies & methods:** Python, FastAPI, OpenAI API, LLMs, prompt engineering, Gradio, MongoDB, REST APIs, conversational context, token usage tracking, rate limiting, cost monitoring, Render, deployment.

**Demonstrates:** LLM application development, backend engineering, prompt engineering, API integration, database design, deployment, usage and cost management, experimentation, and iterative development.

### Sleep Induction Analysis

Signal-processing project focused on analyzing changes in brain activity during the transition from wakefulness to sleep using EEG recordings.

I analyzed both monochannel and multichannel EEG data and investigated how activity changes across different frequency bands. The analysis included spectral features such as band power and spectral entropy, as well as spectrograms, to characterize changes in brain activity during sleep induction.

The project includes separate analysis workflows for monochannel and multichannel recordings, together with filtering functions and visualizations of the resulting signals and spectral characteristics.

**Technologies & methods:** MATLAB, EEG signal processing, spectral analysis, spectrograms, spectral entropy, frequency-band analysis, digital filtering, monochannel and multichannel data.

**Demonstrates:** signal processing, data analysis, scientific computing, quantitative reasoning, interpretation of biological signals, and research methodology.
