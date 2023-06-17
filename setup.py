import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
  name='videohandlercv2',
  version='1.0.0',
  author='Henrique Dev',
  author_email='programmer.henrique@gmail.com',
  description='A simple way to handle videos with cv2',
  long_description=long_description,
  long_description_content_type="text/markdown",
  url='https://github.com/HenriqueDev01/videohandlercv2',
  project_urls = {
      "Bug Tracker": "https://github.com/HenriqueDev01/videohandlercv2/issues"
  },
  license='MIT',
  packages=['videohandlercv2'],
  install_requires=['opencv-python', 'numpy'],
)
