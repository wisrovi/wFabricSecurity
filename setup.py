from setuptools import setup, find_packages

with open("requirements.txt", "r") as file:
    requirements = [
        line.strip() for line in file if line.strip() and not line.startswith("#")
    ]

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="wFabricSecurity",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Intended Audience :: Developers",
    ],
    description="Fabric Security - Librería Python para seguridad distribuida en Hyperledger Fabric",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wisrovi/wFabricSecurity",
    author="William Steve Rodriguez Villamizar",
    author_email="wisrovi.rodriguez@gmail.com",
    license="MIT",
    python_requires=">=3.10",
)
