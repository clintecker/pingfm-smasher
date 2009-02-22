from distutils.core import setup

setup(name='pingfmsmash',
      version='1.0',
      description='Combine RSS feeds into Ping.FM',
      author='Clint Ecker',
      author_email='me@clintecker.com',
      url='http://github.com/clintecker/pingfm-smasher/tree/master',
      packages=['pingfmsmash', 'pingfmsmash.management', 'pingfmsmash.management.commands'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      )