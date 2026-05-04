from setuptools import setup, find_packages


setup(
    name="codegraph",
    version="0.1.0",
    package_dir={"": "backend"},
    packages=find_packages(where="backend"),
    install_requires=[
        "pydantic>=2.5.3",
        "GitPython>=3.1.41",
        "radon>=6.0.1",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "codegraph=codegraph.__main__:main",
        ],
    },
)
