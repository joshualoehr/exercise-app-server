from setuptools import setup, find_packages

setup(
    name='server',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    author="Josh Loehr",
    description="Backend server for the LiftJL exercise app.",
    url="https://github.com/joshualoehr/exercise-app"
)
