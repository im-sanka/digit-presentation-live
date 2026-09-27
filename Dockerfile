# One image, frontend and model together. The push is the deploy.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY synthesis_check ./synthesis_check
COPY app.py .
COPY data ./data
COPY static ./static
COPY .streamlit ./.streamlit

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8501/_stcore/health')"

# Bind to every interface, or the container answers only itself.
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
