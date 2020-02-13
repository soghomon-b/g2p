# -*- coding: utf-8 -*-

""" Checks all data resources give 200s
"""

from unittest import main, TestCase
import re

import requests

from g2p.app import APP
from g2p.log import LOGGER
from g2p.mappings.langs import LANGS_NETWORK


class ResourceIntegrationTest(TestCase):
    """
    This tests that the api returns 200s for all basic
    GET requests.
    """

    def setUp(self):
        # host
        self.hosts = [
            "http://localhost:5000",
            # "https://g2p-studio.herokuapp.com"
        ]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}
        self.prefix = "/api/v1"
        # routes
        self.conversion_route = '/api/v1/g2p'
        self.static_route = "/static/<path:filename>"
        self.routes = [str(route) for route in APP.url_map.iter_rules()]
        self.routes_no_args = [
            route for route in self.routes if not "<" in route and route != self.conversion_route]
        self.routes_only_args = [
            route for route in self.routes if "<" in route and route != self.static_route]
        # endpoints
        self.rules_by_endpoint = APP.url_map._rules_by_endpoint
        self.endpoints = [rt for rt in self.rules_by_endpoint.keys()]
        # args
        self.arg_match = re.compile(r'\<[a-z:]+\>')
        self.args_to_check = ("node")

    def return_endpoint_arg(self, ep):
        split = ep.split('.')
        split_length = len(split)
        return split[split_length-1]

    def return_route_from_endpoint(self, ep):
        return str(self.rules_by_endpoint[ep][0])

    def test_response_code(self):
        '''
        Ensure all routes return 200
        '''
        for rt in self.routes_no_args:
            for host in self.hosts:
                try:
                    r = requests.get(host + rt)
                    self.assertEqual(r.status_code, 200)
                    LOGGER.info("Route " + host + rt +
                                " returned " + str(r.status_code))
                except:
                    LOGGER.error("Couldn't connect. Is flask running?")

    def test_response_code_with_args(self):
        '''
        Ensure all args return 200
        '''
        for ep in self.routes_only_args:
            for host in self.hosts:
                for node in LANGS_NETWORK.nodes:
                    rt = re.sub(self.arg_match, node, ep)
                    try:
                        r = requests.get(host + rt)
                        self.assertEqual(r.status_code, 200)
                    except:
                        LOGGER.error("Couldn't connect. Is flask running?")
                LOGGER.info("Successfully tested " + str(len(LANGS_NETWORK.nodes)
                                                         ) + " node resources at route " + host + ep + " .")

    def test_g2p_conversion(self):
        '''
        Ensure conversion returns proper response
        '''
        params = {'in-lang': 'dan', 'out-lang': 'eng-arpabet',
                  'text': "hej", 'debugger': True, 'index': True}
        bad_params = {'in-lang': 'dan', 'out-lang': 'moh', 'text': "hej"}
        missing_params = {'in-lang': 'not-here',
                          'out-lang': 'eng-arpabet', 'text': "hej"}
        for host in self.hosts:
            response = requests.get(
                host + self.conversion_route, params=params, headers=self.headers)
            res_json = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                res_json, {'output-text': 'HH EH Y', 'index': [[1, 5], [2, 6], [3, 7]], 'debugger': [{'end': 2,
                                                                                                      'input': 'hej',
                                                                                                      'output': 'hɛj',
                                                                                                      'rule': {'context_after': '',
                                                                                                               'context_before': '',
                                                                                                               'in': 'e',
                                                                                                               'out': 'ɛ'},
                                                                                                      'start': 1},
                                                                                                     {'end': 2,
                                                                                                      'input': 'hɛj',
                                                                                                      'output': 'hEH j',
                                                                                                      'rule': {'context_after': '',
                                                                                                               'context_before': '',
                                                                                                               'in': 'ɛ',
                                                                                                               'out': 'EH'},
                                                                                                      'start': 1},
                                                                                                     {'end': 1,
                                                                                                      'input': 'hEH j',
                                                                                                      'output': 'HH EH j',
                                                                                                      'rule': {'context_after': '',
                                                                                                               'context_before': '',
                                                                                                               'in': 'h',
                                                                                                               'out': 'HH'},
                                                                                                      'start': 0},
                                                                                                     {'end': 7,
                                                                                                      'input': 'HH EH j',
                                                                                                      'output': 'HH EH Y',
                                                                                                      'rule': {'context_after': '',
                                                                                                               'context_before': '',
                                                                                                               'in': 'j',
                                                                                                               'out': 'Y'},
                                                                                                      'start': 6}]})
            bad_response = requests.get(
                host + self.conversion_route, params=bad_params, headers=self.headers)
            self.assertEqual(bad_response.status_code, 400)
            missing_response = requests.get(
                host + self.conversion_route, params=missing_params, headers=self.headers)
            self.assertEqual(missing_response.status_code, 404)


if __name__ == '__main__':
    main()
