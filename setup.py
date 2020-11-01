import setuptools


with open("PYPI_README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='l3ns',
    version='0.0.1',
    license='MIT',
    description='L3 Network Simulator',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Daniil Malevanniy',
    author_email='rukmarr@gmail.com',
    url='https://github.com/rukmarr/l3ns',
    packages=setuptools.find_packages(),
    install_requires=[
          'docker',
          'hashids',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
)
