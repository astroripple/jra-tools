FROM tensorflow/tensorflow:latest-gpu-py3-jupyter

ENV PYTHONPATH=/opt/lib \
    DB=mariadb+pymysql://astroripple:S#tonoprime0407@192.168.0.197/astroripple \
    SETUPTOOLS_USE_DISTUTILS=stdlib

#Install Jupyter Environment
RUN pip install --upgrade pip && \
    pip install jupyterlab seaborn graphviz pydotplus sklearn && \
    apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/3bf863cc.pub && \
    apt update && \
    apt install -y fonts-ipaexfont graphviz && \
    echo -e "font.family       : IPAexGothic" >> /usr/local/lib/python3.6/dist-packages/matplotlib/mpl-data/matplotlibrc

#Install JRDB Environment
RUN mkdir code && \
    mkdir /opt/lib && \
    pip uninstall -y enum34 && \
    pip install jrdb_model bs4

COPY ./src/jra_tools /opt/lib/util
WORKDIR /code
#Launch JUPYTER COMMAND
EXPOSE 8888
CMD ["jupyter-lab","--no-browser", "--port=8888", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''"]