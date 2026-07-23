FROM preprocessing:notebook

LABEL authors="eloygarcia"

WORKDIR /workspace

# RUN pip install -y uvicorn

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8003", "--reload"] 
