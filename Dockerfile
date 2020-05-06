FROM python:3.8-slim
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY src/codacy_pylint.py codacy_pylint.py
COPY src/codacy_pylint_test.py codacy_pylint_test.py
COPY docs /docs
RUN useradd -u 2004 -U docker
RUN mkdir /home/docker
RUN chown -R docker:docker /docs /home/docker
USER docker
ENTRYPOINT [ "python3.8" ]
CMD [ "codacy_pylint.py" ]
