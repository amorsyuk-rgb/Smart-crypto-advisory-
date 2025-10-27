from setuptools import setup, find_packages

setup(
    name="crypto-advisory-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask==2.3.3",
        "requests==2.31.0", 
        "python-dotenv==1.0.0",
        "gunicorn==21.2.0",
    ],
    python_requires=">=3.7",
)
