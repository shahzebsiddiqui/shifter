# Shifter, Copyright (c) 2016, The Regents of the University of California,
# through Lawrence Berkeley National Laboratory (subject to receipt of any
# required approvals from the U.S. Dept. of Energy).  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  1. Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#  3. Neither the name of the University of California, Lawrence Berkeley
#     National Laboratory, U.S. Dept. of Energy nor the names of its
#     contributors may be used to endorse or promote products derived from this
#     software without specific prior written permission.`
#
# See LICENSE for full text.

import os
from shifter_imagegw.dockerv2_ext import DockerV2ext
import unittest
import tempfile
import shutil
import json
import base64

class update():

    def update_status(self, state, message):
        print("%s: %s" % (state, message))

class Dockerv2TestCase(unittest.TestCase):

    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        os.environ['PATH'] = cwd + ':' + os.environ['PATH']
        self.updater  = update()
        self.options = None
        if 'LOCALREGISTRY' in os.environ:
            self.options = {'baseUrl': os.environ['LOCALREGISTRY']}
        self.cleanpaths = []
        self.tokens = self.read_tokens()


    def read_tokens(self):
        if not os.path.exists("./tokens.cfg"):
            return None
        with open("./tokens.cfg") as f:
            d = json.load(f)
        return d


    def tearDown(self):
        return
        for path in self.cleanpaths:
            shutil.rmtree(path)

    def test_pull_public(self):
        cache = tempfile.mkdtemp()
        expand = tempfile.mkdtemp()
        image = 'alpine'
        self.cleanpaths.append(cache)
        self.cleanpaths.append(expand)
        dock = DockerV2ext(image, cachedir=cache, updater=self.updater)
        resp = dock.examine_manifest()
        print(resp)
        self.assertIn('id', resp)
        self.assertIn('private', resp)
        resp = dock.pull_layers()
        self.assertTrue(resp)
        dock.extract_docker_layers(expand)
        self.assertTrue(os.path.exists(os.path.join(expand, 'rootfs')))

    def test_pull_private(self):
        if self.tokens is None:
            pass
        tok = base64.b64decode(self.tokens['index.docker.io'])
        username, password = tok.split(':')
        image = 'scanon/shaneprivate'
        options = {'username': username, 'password': password}
        cache = tempfile.mkdtemp()
        expand = tempfile.mkdtemp()
        self.cleanpaths.append(cache)
        self.cleanpaths.append(expand)
        dock = DockerV2ext(image, options=options, cachedir=cache,
                           updater=self.updater)
        resp = dock.examine_manifest()
        self.assertTrue(resp['private'])
        resp = dock.pull_layers()
        self.assertTrue(resp)
        dock.extract_docker_layers(expand)
        self.assertTrue(os.path.exists(os.path.join(expand, 'rootfs')))


    def test_pull_private2(self):
        if self.tokens is None:
            pass
        tok = base64.b64decode(self.tokens['registry.services.nersc.gov'])
        username, password = tok.split(':')
        print(username)
        image = 'scanon/alpine'
        options = {'baseUrl': 'https://registry.services.nersc.gov',
                   'username': username, 'password': password}
        cache = tempfile.mkdtemp()
        expand = tempfile.mkdtemp()
        self.cleanpaths.append(cache)
        self.cleanpaths.append(expand)
        dock = DockerV2ext(image, options=options, cachedir=cache,
                           updater=self.updater)
        resp = dock.examine_manifest()
        self.assertTrue(resp['private'])
        resp = dock.pull_layers()
        self.assertTrue(resp)
        dock.extract_docker_layers(expand)
        self.assertTrue(os.path.exists(os.path.join(expand, 'rootfs')))
