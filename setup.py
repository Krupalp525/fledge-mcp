from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fledge-mcp",
    version="1.0.0",
    author="Krupal Patel",
    author_email="krupalp525@gmail.com",
    description="Fledge Model Context Protocol (MCP) Server for Cursor AI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Krupalp525/fledge-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "fledge-mcp=fledge_mcp.server:main",
            "fledge-mcp-secure=fledge_mcp.secure_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "fledge_mcp": ["tools.json", "smithery.json"],
    },
) 