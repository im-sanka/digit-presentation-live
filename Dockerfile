# One image, three processes: the API, the MCP server, and the Streamlit
# frontend. docker-compose.yml picks the command per service.
FROM python:3.11-slim

WORKDIR /app

# Install dependencies against an empty stub of the package, so editing the
# backend does not reinstall pandas and friends. The real code lands on top.
COPY pyproject.toml requirements.txt ./
RUN mkdir -p backend/synthesis_check && touch backend/synthesis_check/__init__.py \
 && pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY data ./data
COPY .streamlit ./.streamlit

EXPOSE 8501 8000 8080

HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8501/_stcore/health')"

# Bind to every interface, or the container answers only itself.
CMD ["streamlit", "run", "frontend/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
