from setuptools import setup, find_packages

setup(
    name="chaos-monkey-lite",
    version="1.0.0",
    description="A chaos engineering framework for distributed systems",
    author="ChaosMonkey-Lite Contributors",
    packages=find_packages(),
    install_requires=[
        'click>=8.1.7',
        'docker>=7.0.0',
        'requests>=2.31.0',
        'pyyaml>=6.0.1',
        'rich>=13.7.0',
        'psutil>=5.9.8',
        'prometheus-client>=0.19.0',
        'colorama>=0.4.6',
        'tabulate>=0.9.0',
    ],
    entry_points={
        'console_scripts': [
            'chaos=chaos_monkey.cli.main:cli',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
