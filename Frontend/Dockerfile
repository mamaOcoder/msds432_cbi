FROM python:3.7.7

ENV PORT 8088
EXPOSE 8088
WORKDIR /app
COPY . ./
RUN pip install --upgrade pip
RUN pip install streamlit psycopg2 pandas plotly pystan prophet matplotlib
CMD ["streamlit", "run", "--server.port=8088", "--server.enableCORS=false", "frontend.py"]
