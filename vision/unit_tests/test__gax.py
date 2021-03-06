# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import mock


class TestGAXClient(unittest.TestCase):
    def _get_target_class(self):
        from google.cloud.vision._gax import _GAPICVisionAPI
        return _GAPICVisionAPI

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_ctor(self):
        client = mock.Mock()
        with mock.patch('google.cloud.vision._gax.image_annotator_client.'
                        'ImageAnnotatorClient'):
            api = self._make_one(client)
        self.assertIs(api._client, client)

    def test_annotation(self):
        from google.cloud.vision.feature import Feature
        from google.cloud.vision.feature import FeatureTypes
        from google.cloud.vision.image import Image

        client = mock.Mock(spec_set=[])
        feature = Feature(FeatureTypes.LABEL_DETECTION, 5)
        image_content = b'abc 1 2 3'
        image = Image(client, content=image_content)
        with mock.patch('google.cloud.vision._gax.image_annotator_client.'
                        'ImageAnnotatorClient'):
            gax_api = self._make_one(client)

        mock_response = {
            'batch_annotate_images.return_value':
            mock.Mock(responses=['mock response data']),
        }

        gax_api._annotator_client = mock.Mock(
            spec_set=['batch_annotate_images'], **mock_response)

        with mock.patch('google.cloud.vision._gax.Annotations') as mock_anno:
            gax_api.annotate(image, [feature])
            mock_anno.from_pb.assert_called_with('mock response data')
        gax_api._annotator_client.batch_annotate_images.assert_called()

    def test_annotate_no_results(self):
        from google.cloud.vision.feature import Feature
        from google.cloud.vision.feature import FeatureTypes
        from google.cloud.vision.image import Image

        client = mock.Mock(spec_set=[])
        feature = Feature(FeatureTypes.LABEL_DETECTION, 5)
        image_content = b'abc 1 2 3'
        image = Image(client, content=image_content)
        with mock.patch('google.cloud.vision._gax.image_annotator_client.'
                        'ImageAnnotatorClient'):
            gax_api = self._make_one(client)

        mock_response = {
            'batch_annotate_images.return_value': mock.Mock(responses=[]),
        }

        gax_api._annotator_client = mock.Mock(
            spec_set=['batch_annotate_images'], **mock_response)
        with mock.patch('google.cloud.vision._gax.Annotations'):
            self.assertIsNone(gax_api.annotate(image, [feature]))

        gax_api._annotator_client.batch_annotate_images.assert_called()

    def test_annotate_multiple_results(self):
        from google.cloud.vision.feature import Feature
        from google.cloud.vision.feature import FeatureTypes
        from google.cloud.vision.image import Image

        client = mock.Mock(spec_set=[])
        feature = Feature(FeatureTypes.LABEL_DETECTION, 5)
        image_content = b'abc 1 2 3'
        image = Image(client, content=image_content)
        with mock.patch('google.cloud.vision._gax.image_annotator_client.'
                        'ImageAnnotatorClient'):
            gax_api = self._make_one(client)

        mock_response = {
            'batch_annotate_images.return_value': mock.Mock(responses=[1, 2]),
        }

        gax_api._annotator_client = mock.Mock(
            spec_set=['batch_annotate_images'], **mock_response)
        with mock.patch('google.cloud.vision._gax.Annotations'):
            with self.assertRaises(NotImplementedError):
                gax_api.annotate(image, [feature])

        gax_api._annotator_client.batch_annotate_images.assert_called()


class Test__to_gapic_feature(unittest.TestCase):
    def _call_fut(self, feature):
        from google.cloud.vision._gax import _to_gapic_feature
        return _to_gapic_feature(feature)

    def test__to_gapic_feature(self):
        from google.cloud.vision.feature import Feature
        from google.cloud.vision.feature import FeatureTypes
        from google.cloud.grpc.vision.v1 import image_annotator_pb2

        feature = Feature(FeatureTypes.LABEL_DETECTION, 5)
        feature_pb = self._call_fut(feature)
        self.assertIsInstance(feature_pb, image_annotator_pb2.Feature)
        self.assertEqual(feature_pb.type, 4)
        self.assertEqual(feature_pb.max_results, 5)


class Test__to_gapic_image(unittest.TestCase):
    def _call_fut(self, image):
        from google.cloud.vision._gax import _to_gapic_image
        return _to_gapic_image(image)

    def test__to_gapic_image_content(self):
        import base64
        from google.cloud.vision.image import Image
        from google.cloud.grpc.vision.v1 import image_annotator_pb2

        image_content = b'abc 1 2 3'
        b64_content = base64.b64encode(image_content)
        client = object()
        image = Image(client, content=image_content)
        image_pb = self._call_fut(image)
        self.assertIsInstance(image_pb, image_annotator_pb2.Image)
        self.assertEqual(image_pb.content, b64_content)

    def test__to_gapic_image_uri(self):
        from google.cloud.vision.image import Image
        from google.cloud.grpc.vision.v1 import image_annotator_pb2

        image_uri = 'gs://1234/34.jpg'
        client = object()
        image = Image(client, source_uri=image_uri)
        image_pb = self._call_fut(image)
        self.assertIsInstance(image_pb, image_annotator_pb2.Image)
        self.assertEqual(image_pb.source.gcs_image_uri, image_uri)

    def test__to_gapic_with_empty_image(self):
        image = mock.Mock(
            content=None, source=None, spec=['content', 'source'])
        with self.assertRaises(ValueError):
            self._call_fut(image)
