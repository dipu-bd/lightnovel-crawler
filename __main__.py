import sys

if len(sys.argv) <= 1 or sys.argv[1] != '-t':
  from lightnovel_crawler import main
  main()
else:
  from lightnovel_crawler.tests.crawler_app_test import test
  test()
# end if
