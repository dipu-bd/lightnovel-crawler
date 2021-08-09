# -*- coding: utf-8 -*-
"""
The purpose of this bot is to test the application and crawlers
"""
import traceback
from random import random

from cloudscraper.exceptions import CaptchaException, CloudflareException
from requests import RequestException
from urllib3.exceptions import HTTPError

from ...core.sources import crawler_list


class TestBot:
    allerrors = dict()

    from .post_github import post_on_github
    from .test_crawler import test_crawler
    from .test_inputs import allowed_failures, test_user_inputs

    def start(self):
        try:
            randomized = sorted(
                crawler_list.keys(),
                key=lambda x: random()
            )
            for index, link in enumerate(randomized):
                print('=' * 80)
                print('>>>', index, ':', link)
                print('=' * 80)

                if link not in self.test_user_inputs:
                    self.allerrors[link] = ['No test for: %s\n' % link]
                    continue
                # end if

                for entry in self.test_user_inputs[link]:
                    try:
                        print('-' * 5, 'Input:', entry, '-' * 5)
                        self.test_crawler(link, entry)
                        print()
                    except CloudflareException:
                        traceback.print_exc()
                    except CaptchaException:
                        traceback.print_exc()
                    except RequestException:
                        traceback.print_exc()
                    except HTTPError:
                        traceback.print_exc()
                    except Exception as err:
                        traceback.print_exc()
                        traces = traceback.format_tb(err.__traceback__)
                        if link not in self.allerrors:
                            self.allerrors[link] = []
                        # end if
                        self.allerrors[link].append(
                            '> Input: %s\n%s\n%s' % (entry, err, ''.join(traces)))
                    # end try
                # end for
                print('\n')
            # end for
            exit(0)
        except Exception:
            traceback.print_exc()
        finally:
            error_count = len([
                x for x in self.allerrors.keys()
                if x in self.test_user_inputs
                and x not in self.allowed_failures
            ])
            if error_count > 0:
                message = self.build_message()
                print()
                print(message)
                self.post_on_github(message)
                exit(1)
            # end if
        # end try
        exit(0)  # to escape colorama errors
    # end def

    def build_message(self):
        num = 0
        errors = '=' * 80 + '\n'
        message = 'Fix %d sources:\n' % (len(self.allerrors.keys()))
        for key in sorted(self.allerrors.keys()):
            if key in self.allowed_failures:
                message += '- [x] %s (allowed)\n' % key
            elif key not in self.test_user_inputs:
                message += '- [ ] %s (no tests)\n' % key
            else:
                message += '- [ ] %s\n' % key
            # end if

            for err in set(self.allerrors[key]):
                num += 1
                errors += '-' * 80 + '\n'
                errors += 'Error #%d: %s\n' % (num, key)
                errors += '-' * 80 + '\n'
                errors += err + '\n'
            # end for
        # end for
        message += '-' * 80 + '\n'
        errors += '\n' + '=' * 80 + '\n'
        body = '\n%s\n```\n%s\n```\n' % (message, errors)
        return body
    # end_def
# end class
