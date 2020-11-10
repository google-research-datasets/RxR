r"""Pose trace visualization setup."""

import gzip
import json
import os

from absl import app
from absl import flags
from absl import logging

import numpy as np

FLAGS = flags.FLAGS

flags.DEFINE_string('data_dir', 'rxr_data',
                    'The directory containing RxR data. Directory schema is '
                    'defined: https://github.com/google-research-datasets/RxR. '
                    'Visualizations require the pose traces, but not the text '
                    'features.')
flags.DEFINE_string('mesh_dir', 'mp3d',
                    'The directory (or cloud bucket) containing Matterport3D '
                    'textured meshes. Directory schema is defined: '
                    'https://github.com/niessner/Matterport/blob/master/'
                    'data_organization.md')
flags.DEFINE_string('connectivity_dir', 'Matterport3DSimulator/connectivity',
                    'The directory containing the navigation graphs: '
                    'https://github.com/peteanderson80/Matterport3DSimulator/'
                    'tree/master/connectivity')
flags.DEFINE_enum('split', 'rxr_train',
                  ['rxr_train', 'rxr_val_seen', 'rxr_val_unseen',
                   'rxr_test_standard'],
                  'The split to to visualize an annotation from.')
flags.DEFINE_integer('instruction_id', None,
                     'The guide annotation to visualize. If none is provided, '
                     'the first annotation in the file will be used.')
flags.DEFINE_string('args_file', './args.json',
                    'The output args JSON used by the visualizations.')
flags.DEFINE_string('scan_to_mesh_file', './scan_to_mesh.json',
                    'A JSON file mapping Matterport scan IDs to mesh IDs.')


def main(argv):
  if len(argv) > 1:
    raise app.UsageError('Too many command-line arguments.')

  # Find the guide annotation to visualize.
  args = None
  with open(os.path.join(
      FLAGS.data_dir, f'{FLAGS.split}_guide.jsonl.gz'), 'rb') as f:
    logging.info('Reading data file: %s', f.name)
    for args in map(json.loads, gzip.open(f)):
      if (FLAGS.instruction_id is None or
          FLAGS.instruction_id == args['instruction_id']):
        logging.info('Instruction found: %d', args['instruction_id'])
        break
  assert args is not None, (
      f'Unable to find instruction_id: {FLAGS.instruction_id}')

  # Load its numpy pose trace and convert it into a JSON object.
  with open(os.path.join(
      FLAGS.data_dir, 'pose_traces', FLAGS.split,
      f'{args["instruction_id"]:06}_guide_pose_trace.npz'), 'rb') as f:
    logging.info('Reading pose trace file: %s', f.name)
    pose_trace = np.load(f)
    args['pose_trace'] = [
        {  # pylint: disable=g-complex-comprehension
            'time': time,
            'intrinsic_matrix': intrinsic_matrix.reshape([16]).tolist(),
            'extrinsic_matrix': extrinsic_matrix.reshape([16]).tolist(),
        } for time, intrinsic_matrix, extrinsic_matrix in zip(
            pose_trace['time'],
            pose_trace['intrinsic_matrix'],
            pose_trace['extrinsic_matrix'],
        )
    ]

  # Load the navigation graph for the scan.
  with open(os.path.join(
      FLAGS.connectivity_dir, args['scan'] + '_connectivity.json')) as f:
    logging.info('Reading connectivity file: %s', f.name)
    args['connectivity'] = json.load(f)

  with open(FLAGS.scan_to_mesh_file) as f:
    scan_to_mesh_id = json.load(f)
  mesh_id = scan_to_mesh_id[args['scan']]
  args['mesh_url'] = os.path.join(
      FLAGS.mesh_dir, 'v1', 'scans', args['scan'], 'matterport_mesh',
      mesh_id, mesh_id)

  with open(FLAGS.args_file, 'w') as f:
    logging.info('Writing args file: %s', f.name)
    json.dump(args, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
  app.run(main)
